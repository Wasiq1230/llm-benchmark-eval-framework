# How this evaluation was built

## The question

A courier company gets tens of thousands of inbound support messages a month, mostly on WhatsApp, mostly in Roman Urdu or a mix of Urdu and English. Every one of them has to be read, labelled, routed, and answered. The question is which language model should do the first pass.

That is a narrow question and it deserves a narrow test. This is not a general capability comparison and it should not be read as one.

## Why these three models

Vendors were matched on tier, not on brand. All three models here are each vendor's small, fast, cheap tier: the class of model you would actually deploy on forty thousand calls a month. Comparing a frontier model from one vendor against a budget model from another produces a number that looks like a finding and means nothing.

If the recommendation is later challenged with "but their flagship is better", the answer is that the flagship costs ten to twenty-five times more per call, and at this volume that difference is the entire business case.

## The task

One customer message in, one JSON object out. The object carries an intent label, three extracted entities, a routing action, and a customer-facing reply. The JSON goes to the ticketing system, the reply goes to the customer.

Both halves matter and they fail differently. A wrong intent creates a ticket in the wrong queue, which costs time. A reply that invents a delivery date reaches the customer, which costs trust. The scoring treats these as separate things.

## The eval set

Thirty cases, written by hand before any model was run, covering eight intents plus an out-of-scope class. Messages are written in the register customers actually use: lowercase, unpunctuated, misspelled, code-mixed. Nine cases are Roman Urdu, six are mixed, the rest English.

Each case carries three things:

- gold labels, set by hand
- `policy_points`, the facts the reply has to contain, each expressed as a set of acceptable surface forms so a Roman Urdu reply and an English reply can both score full marks for saying the same thing
- `must_not_contain`, the specific inventions that would be dangerous on that message, such as a delivery date on a tracking query or an approved refund on a damage claim

Six cases are deliberately adversarial: a customer who has already given their tracking number and is annoyed at being asked again, a compliment with no request in it, an off-topic weather question, a message with two tracking numbers, a legal threat, and a chargeback threat.

## The six accuracy components

| Component | Weight | What it measures |
|---|---|---|
| Schema valid | 20% | Parses, and every field sits inside its enum |
| Intent exact | 25% | Exact match against the hand-set label |
| Entity F1 | 20% | Micro-F1 over tracking number, city, cash-on-delivery amount |
| Action exact | 15% | The routing decision |
| Grounding | 10% | Zero if the reply contains anything from that case's banned list |
| Policy facts | 10% | Share of required facts present in the reply |

A reply that does not parse scores zero on all six. That is harsher than averaging, and it is deliberate: in production the ticketing system would have dropped the message silently, and a dropped ticket is worse than a wrong one because nobody knows it happened.

Entity F1 excludes slots that are empty in both the gold and the prediction. Without that, a model could return nothing but nulls and score well on the cases where most slots are genuinely empty.

Grounding is only worth ten percent of the accuracy composite, which understates it. It is reported separately on the dashboard for that reason, and any vendor with grounding failures should be discussed on that basis regardless of where it lands on the composite.

## Fairness controls

- One prompt file, read once, sent byte for byte to all three. Its SHA is printed in the report header.
- Temperature zero everywhere.
- Three repeats per case, so run-to-run variance shows up as a stability number rather than disappearing into an average.
- Raw HTTP rather than vendor SDKs. SDKs differ in whether they retry internally, and a vendor that retries silently would post better latency for the wrong reason.
- Same machine, same connection, same session for all three.
- Latency covers the network round trip only, not JSON parsing or scoring.

## Cost model

Token counts come from each vendor's own usage field on the response, not from an estimate. Cost per call is mean input tokens times the input rate plus mean output tokens times the output rate, at the rates in `config/pricing.json` with the date they were checked.

Monthly spend is cost per call times the full monthly contact volume, because every inbound message goes through the model whether or not it ends up needing a human.

The saving is calculated against the current cost of handling those contacts by hand, at the assumed deflection rate. That deflection rate is the softest number in the report and the report says so.

## Latency scoring

Scored on p95, not mean. On WhatsApp the mean is close to meaningless: the customers who leave are the ones in the tail.

Full marks at or below the p95 target, zero at or above the failure threshold, linear in between. Both thresholds sit in `config/config.yaml` so they can be argued about openly rather than buried in code.

## Integration rubric

This axis is scored by hand, because the things that make an API pleasant or miserable to live with do not show up on a stopwatch. Score each vendor 1 to 5 on all six lines, after you have written the client code and deliberately triggered a few errors.

**1. SDK and client quality.** 5: worked first time from the docs, sensible defaults, typed responses. 3: worked after a bit of reading. 1: had to read the source or a GitHub issue to send a request.

**2. Structured output support.** 5: a first-class mode that guarantees schema-valid JSON. 3: a JSON mode that usually holds. 1: prompt-only, and the model wraps its answer in a code fence anyway. Check this against the `clean_json_rate` column, which measures how often the raw text needed unwrapping.

**3. Documentation.** 5: the error you hit is documented with a fix. 3: the reference is complete but the guides are thin. 1: you found the answer on a forum.

**4. Error semantics.** 5: distinct status codes, machine-readable bodies, a retry-after header that is actually correct. 3: correct codes, vague bodies. 1: everything is a 400 with a paragraph of prose.

**5. Rate limit headroom.** Score against the free or entry tier you would start on. 5: the full run finished without a single 429. 1: rate-limited within the first ten calls.

**6. Data residency and terms.** 5: clear written commitment that API inputs are not used for training, with a documented retention window. 3: clear on training, vague on retention. 1: you could not find a straight answer. Check this yourself against the current terms rather than trusting a summary, including this one.

Leave a vendor's rubric at `null` in the config and the report drops the integration axis entirely and renormalises the other three weights. It will not quietly score an unscored vendor as zero.

## Sensitivity

The weighted score is only as good as the weights. The report recomputes the ranking under five profiles: the agreed weights, accuracy first, cost first, speed first, and equal. If the same vendor wins all five, the recommendation is robust to disagreement about priorities and the memo says so. If it does not, the memo names the assumption the decision rests on.

## What this does not tell you

Thirty cases gives a 95% confidence interval on intent accuracy roughly fifteen points wide. Two vendors within about ten points are not distinguishable by this evidence, and no amount of decimal places changes that. To separate close vendors you need a few hundred cases, which is a different piece of work.

The cases came from one person's model of what customers write. They cover the common message types and miss the long tail, which is where support actually gets expensive.

Latency was measured from one location, on one connection, on one day, outside peak. Rerun from the production region before any of these numbers go into an SLA.

Nothing here tests behaviour under load, during a vendor incident, or against someone deliberately trying to make the model say something damaging. Prompt injection through a customer message is a real risk for this use case and it is not covered.

No vendor was contacted, no vendor knew this was running, and no figure in this report came from a vendor's own marketing.
