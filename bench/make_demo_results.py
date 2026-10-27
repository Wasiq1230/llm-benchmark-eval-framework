#!/usr/bin/env python3
"""
Build results/demo_results.json.

This exists for one reason: so the dashboard layout can be reviewed, and the
whole pipeline exercised, before spending a single API call. The numbers it
produces are invented. They are not a measurement of any vendor and must never
appear in a submitted report.

The file it writes carries provenance = "SYNTHETIC DEMO", and the dashboard
renders a red band across the top of every page whenever it sees that value.
Delete results/demo_results.json once you have a real run.

    python bench/make_demo_results.py
"""

import json
import os
import random
import sys
from datetime import datetime, timezone

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scoring import score_case  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RNG = random.Random(20260809)

# Invented behavioural profiles. Nothing here came from a vendor.
PROFILE = {
    "openai":    {"correct": 0.86, "clean": 0.93, "lat": (760, 240), "in": 690, "out": 96},
    "anthropic": {"correct": 0.90, "clean": 0.99, "lat": (980, 300), "in": 705, "out": 88},
    "google":    {"correct": 0.81, "clean": 0.88, "lat": (610, 380), "in": 688, "out": 112},
}
OTHER_INTENTS = ["track_status", "delayed_delivery", "cod_query", "address_change",
                 "damaged_parcel", "pickup_request", "refund_return", "rate_query",
                 "out_of_scope"]
OTHER_ACTIONS = ["resolve_with_info", "create_ticket", "escalate_human",
                 "refund_request", "none"]


def make_reply(case, good):
    """Assemble a reply that satisfies (or fails) the case's policy points."""
    groups = case.get("policy_points") or []
    if good:
        bits = [g[0] for g in groups]
        base = "Thank you for writing in. We will " + ", ".join(bits) if bits else \
               "Thank you for writing in. Our team is on it."
        return base + " and come back to you on this same chat."
    banned = case.get("must_not_contain") or []
    if banned and RNG.random() < 0.5:
        return "Thanks for writing in. Your parcel is " + banned[0] + " and all is well."
    return "Thanks for writing in."


def make_record(case, prof, attempt):
    good = RNG.random() < prof["correct"]
    gold = case["gold"]
    parsed = dict(gold)
    parsed["reply"] = make_reply(case, good)

    if not good:
        roll = RNG.random()
        if roll < 0.35:
            parsed["intent"] = RNG.choice([i for i in OTHER_INTENTS if i != gold["intent"]])
        elif roll < 0.6:
            parsed["action"] = RNG.choice([a for a in OTHER_ACTIONS if a != gold["action"]])
        elif roll < 0.8:
            parsed["tracking_id"] = None if gold["tracking_id"] else "RGX-0000000"
        else:
            parsed["city"] = None if gold["city"] else "Karachi"

    clean = RNG.random() < prof["clean"]
    raw = json.dumps(parsed, ensure_ascii=False)
    if not clean:
        raw = "```json\n" + raw + "\n```"

    mu, sigma = prof["lat"]
    latency = max(120.0, RNG.gauss(mu, sigma))
    if RNG.random() < 0.04:            # occasional slow request, as happens in practice
        latency *= RNG.uniform(2.0, 3.4)

    return {
        "case_id": case["id"], "attempt": attempt, "ok": True,
        "latency_ms": round(latency, 1),
        "input_tokens": prof["in"] + RNG.randint(-18, 18),
        "output_tokens": prof["out"] + RNG.randint(-14, 22),
        "finish": "stop", "raw_text": raw,
        "parsed": parsed, "clean_json": clean, "error": None,
    }


def main():
    with open(os.path.join(ROOT, "config/config.yaml"), encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    with open(os.path.join(ROOT, "eval/eval_set.json"), encoding="utf-8") as fh:
        evalset = json.load(fh)

    # Give the demo a filled-in integration rubric so the fourth axis renders.
    demo_rubric = {
        "openai":    {"sdk_quality": 5, "structured_output": 5, "docs": 5,
                      "error_semantics": 4, "rate_limit_headroom": 4, "data_residency": 3},
        "anthropic": {"sdk_quality": 4, "structured_output": 4, "docs": 5,
                      "error_semantics": 5, "rate_limit_headroom": 3, "data_residency": 3},
        "google":    {"sdk_quality": 4, "structured_output": 4, "docs": 3,
                      "error_semantics": 3, "rate_limit_headroom": 5, "data_residency": 4},
    }
    cfg["integration_scores"] = demo_rubric

    records = {}
    for pcfg in cfg["providers"]:
        prof = PROFILE[pcfg["key"]]
        rows = []
        for case in evalset["cases"]:
            for rep in range(cfg["run"]["repeats"]):
                rec = make_record(case, prof, rep)
                rec["scores"] = score_case(rec["parsed"], rec["clean_json"],
                                           case, cfg["accuracy_components"])
                rows.append(rec)
        records[pcfg["key"]] = rows

    payload = {
        "provenance": "SYNTHETIC DEMO",
        "run_started_utc": datetime.now(timezone.utc).isoformat(),
        "run_finished_utc": datetime.now(timezone.utc).isoformat(),
        "operator": "demo generator",
        "prompt_sha": "demo00000000",
        "eval_set_sha": "demo00000000",
        "config": cfg, "eval_set": evalset, "records": records,
    }
    out = os.path.join(ROOT, "results/demo_results.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print("wrote results/demo_results.json  (synthetic, not a measurement)")


if __name__ == "__main__":
    main()
