"""
Turn raw per-call records into one summary object.

Everything the dashboard and the memo show is computed here, so there is exactly
one place where a number can be wrong.
"""

import json
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bench"))
from scoring import percentile, wilson_interval  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMPONENTS = ["json_valid", "intent_exact", "entities_f1", "action_exact",
              "grounding", "policy_points"]


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else 0.0


def _rubric_mean(scores):
    vals = [v for v in (scores or {}).values() if isinstance(v, (int, float))]
    return statistics.fmean(vals) if vals else None


def cost_of(model, pricing, in_tok, out_tok):
    row = pricing["models"].get(model)
    if not row:
        return None
    return (in_tok / 1e6) * row["input"] + (out_tok / 1e6) * row["output"]


def latency_score(p95_ms, target, fail):
    if p95_ms is None:
        return 0.0
    if p95_ms <= target:
        return 100.0
    if p95_ms >= fail:
        return 0.0
    return 100.0 * (fail - p95_ms) / (fail - target)


def build(results, pricing):
    cfg = results["config"]
    cases = {c["id"]: c for c in results["eval_set"]["cases"]}
    client = cfg["client"]
    weights = cfg["weights"]
    contacts = client["monthly_support_contacts"]
    fx = client["usd_to_pkr"]

    providers = []
    for pcfg in cfg["providers"]:
        recs = results["records"].get(pcfg["key"])
        if not recs:
            continue

        ok = [r for r in recs if r["ok"]]
        lat = [r["latency_ms"] for r in ok if r["latency_ms"] is not None]
        in_tok = _mean([r["input_tokens"] for r in ok]) or 0.0
        out_tok = _mean([r["output_tokens"] for r in ok]) or 0.0

        comp = {c: _mean([r["scores"][c] for r in recs]) for c in COMPONENTS}
        accuracy = _mean([r["scores"]["accuracy"] for r in recs])

        intent_hits = sum(1 for r in recs if r["scores"]["intent_exact"] == 1.0)
        lo, hi = wilson_interval(intent_hits, len(recs))

        # Which cases the model got wrong, deduplicated across repeats.
        grounding_fails, intent_fails, parse_fails = set(), set(), set()
        for r in recs:
            if r["scores"]["grounding"] < 1.0:
                grounding_fails.add(r["case_id"])
            if r["scores"]["intent_exact"] < 1.0:
                intent_fails.add(r["case_id"])
            if r["parsed"] is None:
                parse_fails.add(r["case_id"])

        # Consistency: how often the three repeats of a case agreed on intent.
        by_case = {}
        for r in recs:
            by_case.setdefault(r["case_id"], []).append(
                (r["parsed"] or {}).get("intent")
            )
        stable = sum(1 for v in by_case.values() if len(set(v)) == 1)
        consistency = stable / len(by_case) if by_case else 0.0

        unit_usd = cost_of(pcfg["model"], pricing, in_tok, out_tok)
        monthly_usd = (unit_usd or 0.0) * contacts
        p95 = percentile(lat, 95) if lat else None

        providers.append({
            "key": pcfg["key"], "label": pcfg["label"], "model": pcfg["model"],
            "calls": len(recs), "errors": len(recs) - len(ok),
            "error_rate": (len(recs) - len(ok)) / len(recs) if recs else 0.0,
            "accuracy": accuracy,
            "components": comp,
            "intent_ci": [lo, hi],
            "consistency": consistency,
            "clean_json_rate": _mean([r["scores"]["clean_json"] for r in recs]),
            "reply_length_ok": _mean([r["scores"]["reply_length"] for r in recs]),
            "latency": {
                "mean": statistics.fmean(lat) if lat else None,
                "p50": percentile(lat, 50) if lat else None,
                "p90": percentile(lat, 90) if lat else None,
                "p95": p95,
                "p99": percentile(lat, 99) if lat else None,
                "min": min(lat) if lat else None,
                "max": max(lat) if lat else None,
                "samples": lat,
            },
            "tokens": {"input": in_tok, "output": out_tok},
            "cost": {
                "per_request_usd": unit_usd,
                "per_1k_usd": (unit_usd or 0.0) * 1000,
                "monthly_usd": monthly_usd,
                "monthly_pkr": monthly_usd * fx,
            },
            "failures": {
                "grounding": sorted(grounding_fails),
                "intent": sorted(intent_fails),
                "parse": sorted(parse_fails),
            },
            "integration_rubric": cfg["integration_scores"].get(pcfg["key"], {}),
            "integration_mean": _rubric_mean(cfg["integration_scores"].get(pcfg["key"])),
        })

    # Normalise each axis to 0-100, then apply the decision weights.
    costs = [p["cost"]["per_request_usd"] for p in providers if p["cost"]["per_request_usd"]]
    cheapest = min(costs) if costs else None

    for p in providers:
        c = p["cost"]["per_request_usd"]
        p["axes"] = {
            "accuracy": p["accuracy"] * 100,
            "cost": (100.0 * cheapest / c) if (c and cheapest) else 0.0,
            "latency": latency_score(p["latency"]["p95"],
                                     cfg["latency"]["target_p95_ms"],
                                     cfg["latency"]["fail_p95_ms"]),
            "integration": ((p["integration_mean"] - 1) / 4 * 100)
                           if p["integration_mean"] else None,
        }
        active = {k: w for k, w in weights.items()
                  if p["axes"].get(k) is not None}
        total_w = sum(active.values()) or 1.0
        p["composite"] = sum(p["axes"][k] * w for k, w in active.items()) / total_w
        p["integration_scored"] = p["axes"]["integration"] is not None

    providers.sort(key=lambda p: p["composite"], reverse=True)
    for i, p in enumerate(providers):
        p["rank"] = i + 1

    # Does the winner survive a different set of weights? If it does not, the
    # memo has to say which assumption the recommendation depends on.
    profiles = {
        "As specified": weights,
        "Accuracy first": {"accuracy": 0.60, "cost": 0.15, "latency": 0.15, "integration": 0.10},
        "Cost first": {"accuracy": 0.25, "cost": 0.50, "latency": 0.15, "integration": 0.10},
        "Speed first": {"accuracy": 0.25, "cost": 0.15, "latency": 0.50, "integration": 0.10},
        "Equal": {"accuracy": 0.25, "cost": 0.25, "latency": 0.25, "integration": 0.25},
    }
    sensitivity = []
    for name, w in profiles.items():
        row = {"profile": name, "weights": w, "scores": {}}
        for p in providers:
            active = {k: ww for k, ww in w.items() if p["axes"].get(k) is not None}
            tw = sum(active.values()) or 1.0
            row["scores"][p["key"]] = sum(p["axes"][k] * ww for k, ww in active.items()) / tw
        row["winner"] = max(row["scores"], key=row["scores"].get) if row["scores"] else None
        sensitivity.append(row)

    winner_key = providers[0]["key"] if providers else None
    stable_winner = all(r["winner"] == winner_key for r in sensitivity)

    # Side-by-side outputs, one record per case per provider.
    samples = []
    for cid, case in cases.items():
        entry = {"case": case, "outputs": {}}
        for p in providers:
            recs = [r for r in results["records"][p["key"]] if r["case_id"] == cid]
            if not recs:
                continue
            r = recs[0]
            entry["outputs"][p["key"]] = {
                "raw": r["raw_text"], "parsed": r["parsed"],
                "scores": {k: v for k, v in r["scores"].items() if k != "schema_issues"},
                "latency_ms": r["latency_ms"], "error": r["error"],
            }
        if entry["outputs"]:
            samples.append(entry)

    # Business case, computed on the winner.
    biz = None
    if providers:
        w = providers[0]
        deflected = contacts * client["target_deflection"]
        human_cost = contacts * client["agent_cost_pkr_per_contact"]
        saved = deflected * client["agent_cost_pkr_per_contact"]
        biz = {
            "monthly_contacts": contacts,
            "deflection_target": client["target_deflection"],
            "deflected_contacts": deflected,
            "human_baseline_pkr": human_cost,
            "llm_monthly_pkr": w["cost"]["monthly_pkr"],
            "gross_saving_pkr": saved,
            "net_saving_pkr": saved - w["cost"]["monthly_pkr"],
            "llm_share_of_human_cost": (w["cost"]["monthly_pkr"] / human_cost) if human_cost else 0.0,
        }

    return {
        "provenance": results.get("provenance", "unknown"),
        "run_started_utc": results.get("run_started_utc"),
        "run_finished_utc": results.get("run_finished_utc"),
        "operator": results.get("operator"),
        "prompt_sha": results.get("prompt_sha"),
        "eval_set_sha": results.get("eval_set_sha"),
        "pricing_checked_on": pricing["checked_on"],
        "pricing_caveats": pricing["caveats"],
        "client": client,
        "use_case": cfg["use_case"],
        "weights": weights,
        "accuracy_components": cfg["accuracy_components"],
        "latency_targets": cfg["latency"],
        "n_cases": len(cases),
        "repeats": cfg["run"]["repeats"],
        "providers": providers,
        "sensitivity": sensitivity,
        "stable_winner": stable_winner,
        "samples": samples,
        "business": biz,
    }


def load_all(results_path, pricing_path="config/pricing.json"):
    with open(os.path.join(ROOT, results_path), encoding="utf-8") as fh:
        results = json.load(fh)
    with open(os.path.join(ROOT, pricing_path), encoding="utf-8") as fh:
        pricing = json.load(fh)
    return build(results, pricing)
