# Which model should answer our customers first

A vendor evaluation for a courier company deciding which language model to put in front of inbound customer support. Three providers, one prompt, thirty hand-labelled cases, one weighted recommendation.

Built for the SafeX Solutions Week 4 sprint, Group 57.

## Change this first

`config/config.yaml`, line 9: `client.name`. Set it to the courier business you used in Week 3. Nothing else in the repo hardcodes a company name, so that single edit carries through the dashboard, the memo, and the slides.

Then check `client.monthly_support_contacts`, `agent_cost_pkr_per_contact`, and `usd_to_pkr` in the same block. Those three numbers drive the whole business case, so they should be yours, not the defaults.

## Run order

```bash
pip install -r requirements.txt

cp .env.example .env          # add your three API keys
set -a && source .env && set +a

python bench/run_benchmark.py --repeats 1 --limit 3   # smoke test, 9 requests
python bench/run_benchmark.py                          # full run, 270 requests
python report/build_report.py
open report/dashboard.html
```

The smoke test is not optional. A full run is 270 requests and free tiers will rate-limit you partway through, which leaves you with a half-finished results file and no idea which half.

If you do get rate-limited, run one vendor at a time. Results merge into the same file as long as the prompt has not changed:

```bash
python bench/run_benchmark.py --only anthropic
python bench/run_benchmark.py --only openai
python bench/run_benchmark.py --only google
```

## Looking at the dashboard before spending any credit

```bash
python bench/make_demo_results.py
python report/build_report.py --results results/demo_results.json
```

That fills the page with invented numbers so you can see the layout. The file it writes carries `provenance: SYNTHETIC DEMO`, and the dashboard puts a red band across the top whenever it sees that. Delete `results/demo_results.json` once you have a real run, so there is no way to submit the wrong one by accident.

## What is where

| Path | What it does |
|---|---|
| `config/config.yaml` | Client context, the three models, weights, latency targets, integration rubric scores |
| `config/pricing.json` | Per-token rates with the date they were checked and the vendor pages they came from |
| `eval/system_prompt.txt` | The one prompt, sent byte for byte to all three vendors |
| `eval/eval_set.json` | Thirty cases with hand-set gold labels, required policy facts, and banned inventions |
| `bench/providers.py` | One HTTP client per vendor, plus an optional LiteLLM gateway path |
| `bench/scoring.py` | Six deterministic scoring functions, Wilson intervals, percentiles |
| `bench/run_benchmark.py` | Runs everything, writes `results/results.json` |
| `report/aggregate.py` | Every number in the report is computed here and nowhere else |
| `report/build_report.py` | Renders `report/dashboard.html` and `docs/recommendation_memo.md` |
| `docs/methodology.md` | How each measure is defined, including the integration rubric you score by hand |

## The integration score is yours to fill in

Four axes go into the weighted score. Three are measured automatically. The fourth, ease of integration, is a hand-scored rubric, because a stopwatch cannot tell you whether the error messages made sense at 2am.

Score it in `config/config.yaml` under `integration_scores`, using the rubric in `docs/methodology.md`, after you have written the client code and hit a few errors on purpose. Leave a vendor's scores at `null` and the report drops that axis and renormalises the weights, rather than quietly scoring it zero.

## Reproducibility

The dashboard header prints a hash of the prompt and a hash of the eval set. Same hashes, same setup, same numbers within run-to-run variance. If you edit the prompt, the runner notices the hash changed and discards earlier records rather than mixing two prompts in one table.

## Honest limits

Thirty cases is a small set. The confidence interval on intent accuracy is roughly plus or minus fifteen points at that size, so two vendors within about ten points of each other are not distinguishable here and the report says so in its own words. Latency was measured from one machine on one connection. Nothing here tests load, incidents, or adversarial input. Treat this as enough to rule a vendor out, not enough to sign a two-year contract.
