#!/usr/bin/env python3
"""
Build the dashboard and the recommendation memo from a results file.

    python report/build_report.py                          uses results/results.json
    python report/build_report.py --results results/demo_results.json

Outputs:
    report/dashboard.html
    docs/recommendation_memo.md
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aggregate import load_all  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def money_pkr(v):
    return "Rs " + f"{v:,.0f}"


def write_memo(s, path):
    """
    The memo is generated, not typed, so it can never drift from the numbers on
    the dashboard. Edit the wording here, not in the output file.
    """
    P = s["providers"]
    w, second = P[0], (P[1] if len(P) > 1 else None)
    demo = "DEMO" in str(s["provenance"]).upper()
    b = s["business"]
    ci = w["intent_ci"]

    L = []
    if demo:
        L += ["> Built from synthetic demo data. Every figure below is invented and is here only",
              "> to show the shape of the memo. Run the benchmark and rebuild before sending this",
              "> to anyone.", ""]

    L += [
        f"# Which model should answer {s['client']['name']} customers first",
        "",
        f"To: Head of Customer Experience, {s['client']['name']}  ",
        f"From: {s.get('operator') or 'evaluation team'}, SafeX Solutions  ",
        f"Date: {(s.get('run_finished_utc') or '')[:10]}  ",
        f"Subject: Vendor choice for first-line support triage",
        "",
        "## Recommendation",
        "",
        f"Go with {w['label']} {w['model']} for first-line triage.",
        "",
        f"It scored {w['composite']:.1f} out of 100 on the weighted comparison"
        + (f", {w['composite'] - second['composite']:.1f} points ahead of {second['label']}." if second else "."),
        f"It labelled customer intent correctly on {w['components']['intent_exact']*100:.0f}% of calls "
        f"(95% confidence interval {ci[0]*100:.0f} to {ci[1]*100:.0f}%), and it invented a fact it had no way of "
        f"knowing on {(1-w['components']['grounding'])*100:.0f}% of replies.",
        "",
    ]

    if s["stable_winner"]:
        L += ["The same vendor comes out ahead under every set of weights we tested, including ones that put cost first "
              "and ones that put speed first. The decision does not hinge on how the scoring was set up.", ""]
    else:
        L += ["The ranking changes depending on what you weight most heavily. Before this becomes a decision, agree "
              "whether accuracy, cost, or response time matters most, then read the sensitivity table in section 06 "
              "of the dashboard.", ""]

    L += ["## What it costs", ""]
    if b:
        L += [
            f"At {b['monthly_contacts']:,} inbound contacts a month, {w['label']} costs about "
            f"{money_pkr(b['llm_monthly_pkr'])} a month in API spend. Handling the same volume with agents costs "
            f"{money_pkr(b['human_baseline_pkr'])}.",
            "",
            f"If the model deflects {b['deflection_target']*100:.0f}% of contacts without a human, that removes "
            f"{money_pkr(b['gross_saving_pkr'])} of agent cost, for a net monthly effect of "
            f"{money_pkr(b['net_saving_pkr'])}.",
            "",
            "The deflection rate is the assumption to watch. It is a target, not a measurement, and the business case "
            "moves with it. Two weeks of live traffic will tell you the real number.",
            "",
        ]

    L += ["## Why not the other two", ""]
    for p in P[1:]:
        losses = []
        if p["accuracy"] < w["accuracy"]:
            losses.append(f"{(w['accuracy']-p['accuracy'])*100:.0f} points behind on accuracy")
        if p["cost"]["per_request_usd"] and w["cost"]["per_request_usd"]:
            r = p["cost"]["per_request_usd"] / w["cost"]["per_request_usd"]
            if r > 1.05:
                losses.append(f"{r:.1f} times the cost per call")
            elif r < 0.95:
                losses.append(f"cheaper per call at {money_pkr(p['cost']['monthly_pkr'])} a month")
        if p["latency"]["p95"] and w["latency"]["p95"]:
            d = p["latency"]["p95"] - w["latency"]["p95"]
            if abs(d) > 100:
                losses.append(f"{abs(d):,.0f} ms {'slower' if d > 0 else 'faster'} at p95")
        gf = len(p["failures"]["grounding"])
        if gf:
            losses.append(f"invented facts on {gf} cases")
        L += [f"{p['label']} {p['model']}: " + "; ".join(losses) + ".", ""]

    L += [
        "## What would change this answer",
        "",
        f"The eval set has {s['n_cases']} cases. That is enough to catch a vendor that is clearly worse and not enough "
        "to separate two that are close. Anything under about ten points of difference should be treated as a tie.",
        "",
        "Three things would make us revisit:",
        "",
        "1. A price change. Rates were checked on " + s["pricing_checked_on"] + " and all three vendors have moved "
        "prices this year.",
        "2. Live deflection coming in well below target. Below roughly half the target, the case for any vendor "
        "gets thin and the conversation becomes about a narrower deployment rather than about which model.",
        "3. Grounding failures appearing in production that the eval set did not catch. That is the failure mode "
        "that reaches customers, so it is worth sampling replies by hand for the first fortnight.",
        "",
        "## Next step",
        "",
        f"A two-week shadow deployment. Run {w['label']} against live inbound traffic without sending its replies to "
        "customers, compare its triage against what agents actually did, and measure real deflection. That gives a "
        "decision on real traffic before anything is switched on.",
        "",
        "---",
        "",
        f"Method, full comparison table, sample outputs, and the failure log are in the dashboard at "
        f"`report/dashboard.html`. Prompt hash `{s['prompt_sha']}`, eval set hash `{s['eval_set_sha']}`.",
        "",
    ]

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results/results.json")
    ap.add_argument("--out", default="report/dashboard.html")
    ap.add_argument("--memo", default="docs/recommendation_memo.md")
    args = ap.parse_args()

    path = os.path.join(ROOT, args.results)
    if not os.path.exists(path):
        alt = os.path.join(ROOT, "results/demo_results.json")
        if os.path.exists(alt):
            print(f"{args.results} not found, falling back to the synthetic demo file")
            args.results = "results/demo_results.json"
        else:
            sys.exit(f"No results at {args.results}. Run bench/run_benchmark.py first.")

    summary = load_all(args.results)

    with open(os.path.join(ROOT, "report/template.html"), encoding="utf-8") as fh:
        tpl = fh.read()
    html = tpl.replace(
        "/*__DATA__*/ null",
        json.dumps(summary, ensure_ascii=False).replace("</", "<\\/")
    )
    out = os.path.join(ROOT, args.out)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)

    memo = os.path.join(ROOT, args.memo)
    os.makedirs(os.path.dirname(memo), exist_ok=True)
    write_memo(summary, memo)

    print(f"wrote {args.out}")
    print(f"wrote {args.memo}")
    if "DEMO" in str(summary["provenance"]).upper():
        print("\n  built from SYNTHETIC data. Do not submit this version.")


if __name__ == "__main__":
    main()
