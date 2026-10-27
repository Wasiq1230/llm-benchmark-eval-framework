#!/usr/bin/env python3
"""
Run every case against every provider and write results/results.json.

Usage:
    set -a && source .env && set +a
    python bench/run_benchmark.py
    python bench/run_benchmark.py --only anthropic       one vendor at a time
    python bench/run_benchmark.py --repeats 1 --limit 5  cheap smoke test first

Read this before your first full run: 30 cases times 3 repeats times 3 vendors
is 270 requests. On free tiers that will hit a rate limit. Do the smoke test,
confirm the output looks right, then run the vendors one at a time.
"""

import argparse
import concurrent.futures as futures
import hashlib
import json
import os
import platform
import random
import socket
import sys
import time
from datetime import datetime, timezone

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from providers import build_caller, extract_json, RateLimited, ProviderError  # noqa: E402
from scoring import score_case  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return yaml.safe_load(fh) if path.endswith((".yaml", ".yml")) else json.load(fh)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def one_call(caller, system_prompt, case, run_cfg, attempt_label):
    """One request, with backoff on 429 only. Other errors are recorded, not retried."""
    delay = 2.0
    last_error = None
    for _ in range(run_cfg["retry_on_429"] + 1):
        try:
            out = caller(system_prompt, case["message"], run_cfg)
            pred, clean = extract_json(out["text"])
            return {
                "case_id": case["id"], "attempt": attempt_label, "ok": True,
                "latency_ms": out["latency_ms"],
                "input_tokens": out["input_tokens"], "output_tokens": out["output_tokens"],
                "finish": out.get("raw_finish"), "raw_text": out["text"],
                "parsed": pred, "clean_json": clean, "error": None,
            }
        except RateLimited as exc:
            last_error = f"429 rate limited: {str(exc.body)[:160]}"
            time.sleep(delay + random.random())
            delay *= 2
        except ProviderError as exc:
            last_error = f"{exc.status}: {str(exc.body)[:160]}"
            break
        except Exception as exc:  # network, timeout, malformed response envelope
            last_error = f"{type(exc).__name__}: {exc}"
            break
    return {
        "case_id": case["id"], "attempt": attempt_label, "ok": False,
        "latency_ms": None, "input_tokens": 0, "output_tokens": 0,
        "finish": None, "raw_text": "", "parsed": None, "clean_json": False,
        "error": last_error,
    }


def run_provider(pcfg, cases, system_prompt, cfg):
    run_cfg = cfg["run"]
    caller = build_caller(pcfg, cfg.get("gateway", {}))
    jobs = [(c, r) for c in cases for r in range(run_cfg["repeats"])]
    records = []

    print(f"  {pcfg['label']} / {pcfg['model']}: {len(jobs)} requests")
    with futures.ThreadPoolExecutor(max_workers=run_cfg["concurrency"]) as pool:
        pending = {
            pool.submit(one_call, caller, system_prompt, case, run_cfg, rep): (case, rep)
            for case, rep in jobs
        }
        done = 0
        for fut in futures.as_completed(pending):
            case, _ = pending[fut]
            rec = fut.result()
            rec["scores"] = score_case(
                rec["parsed"], rec["clean_json"], case, cfg["accuracy_components"]
            )
            records.append(rec)
            done += 1
            if done % 10 == 0 or done == len(jobs):
                print(f"    {done}/{len(jobs)}")
    records.sort(key=lambda r: (r["case_id"], r["attempt"]))
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="provider key: openai, anthropic, google")
    ap.add_argument("--limit", type=int, help="first N cases only")
    ap.add_argument("--repeats", type=int, help="override config repeats")
    ap.add_argument("--out", default="results/results.json")
    args = ap.parse_args()

    cfg = load("config/config.yaml")
    evalset = load("eval/eval_set.json")
    with open(os.path.join(ROOT, "eval/system_prompt.txt"), encoding="utf-8") as fh:
        system_prompt = fh.read()

    if args.repeats:
        cfg["run"]["repeats"] = args.repeats
    cases = evalset["cases"][: args.limit] if args.limit else evalset["cases"]
    providers = [p for p in cfg["providers"] if not args.only or p["key"] == args.only]

    print(f"prompt sha       {sha(system_prompt)}")
    print(f"eval set sha     {sha(json.dumps(evalset, sort_keys=True))}")
    print(f"cases            {len(cases)}   repeats {cfg['run']['repeats']}")

    started = datetime.now(timezone.utc)
    per_provider = {}
    for pcfg in providers:
        try:
            per_provider[pcfg["key"]] = run_provider(pcfg, cases, system_prompt, cfg)
        except RuntimeError as exc:
            print(f"  skipped {pcfg['key']}: {exc}")

    out_path = os.path.join(ROOT, args.out)
    existing = {}
    if os.path.exists(out_path):
        # Merge, so you can run vendors on separate days without losing earlier work.
        with open(out_path, encoding="utf-8") as fh:
            prior = json.load(fh)
        if prior.get("prompt_sha") == sha(system_prompt):
            existing = prior.get("records", {})
        else:
            print("  prompt changed since the last run, previous records discarded")
    existing.update(per_provider)

    payload = {
        "provenance": "measured",
        "run_started_utc": started.isoformat(),
        "run_finished_utc": datetime.now(timezone.utc).isoformat(),
        "operator": os.environ.get("OPERATOR_NAME", os.environ.get("USER", "unknown")),
        "host": socket.gethostname(),
        "python": platform.python_version(),
        "prompt_sha": sha(system_prompt),
        "eval_set_sha": sha(json.dumps(evalset, sort_keys=True)),
        "config": cfg,
        "eval_set": evalset,
        "records": existing,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print(f"\nwrote {args.out}")
    print("next: python report/build_report.py")


if __name__ == "__main__":
    main()
