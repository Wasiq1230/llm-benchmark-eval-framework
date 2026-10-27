> Built from synthetic demo data. Every figure below is invented and is here only
> to show the shape of the memo. Run the benchmark and rebuild before sending this
> to anyone.

# Which model should answer Rahguzar Express customers first

To: Head of Customer Experience, Rahguzar Express  
From: demo generator, SafeX Solutions  
Date: 2026-08-09  
Subject: Vendor choice for first-line support triage

## Recommendation

Go with OpenAI gpt-5.6-luna for first-line triage.

It scored 96.0 out of 100 on the weighted comparison, 14.3 points ahead of Google.
It labelled customer intent correctly on 96% of calls (95% confidence interval 89 to 98%), and it invented a fact it had no way of knowing on 3% of replies.

The same vendor comes out ahead under every set of weights we tested, including ones that put cost first and ones that put speed first. The decision does not hinge on how the scoring was set up.

## What it costs

At 42,000 inbound contacts a month, OpenAI costs about Rs 3,086 a month in API spend. Handling the same volume with agents costs Rs 1,428,000.

If the model deflects 60% of contacts without a human, that removes Rs 856,800 of agent cost, for a net monthly effect of Rs 853,714.

The deflection rate is the assumption to watch. It is a target, not a measurement, and the business case moves with it. Two weeks of live traffic will tell you the real number.

## Why not the other two

Google gemini-3.5-flash-lite: 1 points behind on accuracy; 1.9 times the cost per call; 201 ms slower at p95; invented facts on 7 cases.

Anthropic claude-haiku-4-5-20251001: 4.4 times the cost per call; 294 ms slower at p95; invented facts on 5 cases.

## What would change this answer

The eval set has 30 cases. That is enough to catch a vendor that is clearly worse and not enough to separate two that are close. Anything under about ten points of difference should be treated as a tie.

Three things would make us revisit:

1. A price change. Rates were checked on 2026-08-09 and all three vendors have moved prices this year.
2. Live deflection coming in well below target. Below roughly half the target, the case for any vendor gets thin and the conversation becomes about a narrower deployment rather than about which model.
3. Grounding failures appearing in production that the eval set did not catch. That is the failure mode that reaches customers, so it is worth sampling replies by hand for the first fortnight.

## Next step

A two-week shadow deployment. Run OpenAI against live inbound traffic without sending its replies to customers, compare its triage against what agents actually did, and measure real deflection. That gives a decision on real traffic before anything is switched on.

---

Method, full comparison table, sample outputs, and the failure log are in the dashboard at `report/dashboard.html`. Prompt hash `demo00000000`, eval set hash `demo00000000`.
