# Walkthrough video script

Target 7 minutes. Face on camera for the open and the close, screen share for the middle. Record at 1080p. Speak slower than feels natural; everyone rushes the first take.

Before you hit record: close every other tab, set the browser to 110% zoom so the dashboard type is readable in a compressed upload, and have the terminal already sitting in the project folder. Rebuild the dashboard from real results first. If the red synthetic-data band is on screen at any point, the video is unusable.

---

## 0:00 to 0:35, face on camera

I am Fatima Naseer, computer science at the Institute of Space Technology, interning with SafeX Solutions. This is my Week 4 project.

The question is narrow. A courier company gets forty thousand support messages a month, mostly on WhatsApp, mostly in a mix of Urdu and English. Which language model should read them first? I tested three and I have a recommendation, but the more useful part is how I tested them, because the method is the thing you would reuse.

## 0:35 to 1:30, screen: eval_set.json

Everything rests on this file. Thirty customer messages, written the way people actually type on WhatsApp, and labelled by hand before I ran a single model.

Read one aloud: `bhai mera parcel kahan hai 3 din ho gaye RGX8830115`.

Each case carries three things. The gold labels. A list of facts the reply has to contain. And this list here, `must_not_contain`, which is the one I care about most: the specific things a model must not say on this message. The model has no access to the tracking database, so if it tells this customer their parcel arrives tomorrow, it has made that up, and that reaches a real person.

## 1:30 to 2:15, screen: system_prompt.txt and providers.py

One prompt file. Read once, sent byte for byte to all three vendors. The report prints a hash of it so anyone can check I did not quietly tune the prompt for a favourite.

I wrote the HTTP calls by hand instead of using the vendor SDKs, for one reason: some SDKs retry internally and some do not, and a vendor that retries silently posts better latency for a reason that has nothing to do with the model.

## 2:15 to 2:50, screen: terminal

Show a short run: `python bench/run_benchmark.py --repeats 1 --limit 3`.

While it runs: thirty cases, three repeats, three vendors, two hundred and seventy requests. Three repeats because I want to see whether a model gives the same answer twice, and averaging that away would hide it.

Then `python report/build_report.py`.

## 2:50 to 4:15, screen: dashboard, verdict and scorecard

Open the dashboard. Point at the green band at the top: this says the page came from a measured run, with the prompt hash and eval set hash next to it. Rerun with those hashes and you get this page back.

Walk down the three vendor cards, then the comparison table. Do not read the table out. Pick three rows and say why each one is there:

- intent accuracy, with the confidence interval next to it, because thirty cases is a small set and the interval is wide
- grounding, the share of replies that invented nothing
- cost per thousand calls, which at this volume is the row that decides the budget

## 4:15 to 5:15, screen: sample outputs section

This is the part to slow down on. Click "jump to biggest disagreement". Same message, three answers, side by side, with the gold answer on the left.

Read one model's reply out loud and point at where it goes wrong. If one of them invented a delivery date, that is your moment: this is what a ninety-four percent accuracy score does not tell you.

## 5:15 to 6:00, screen: sensitivity and money

The weights are mine, so the obvious objection is that I picked weights that produced the answer I wanted. This table recomputes the ranking under five different weight profiles, including ones that put cost first and speed first.

Say plainly which happened: either the same vendor wins all five, which means the recommendation survives disagreement about priorities, or it does not, in which case name the assumption it depends on.

Then the money panel: API spend against the cost of handling the same volume by hand, and the net effect at the deflection target. Flag the deflection rate as an assumption out loud. Do not let it slide past.

## 6:00 to 6:40, screen: methodology, limits column

Read three of the limits straight off the page. Thirty cases cannot separate two vendors within ten points of each other. Latency was measured from one machine on one connection. Nothing here tests prompt injection through a customer message, which for this use case is a real risk I did not cover.

Saying this out loud is not a weakness in the video. It is the reason anyone would trust the rest.

## 6:40 to 7:00, face on camera

The recommendation is in the memo, the method is in the repo, and the next step I would argue for is a two-week shadow deployment against live traffic before anything is switched on.

Repo link is in the description. Thanks for watching.

---

## Recording notes

Do the face segments last. By then you will have said the middle section four times and the open will come out clean on the first try.

Do not use a voice clone for this one. The brief allows AI voice tools, but this video is a portfolio piece whose whole argument is that you did the work carefully. Your own voice, with a couple of ums in it, is worth more here.

Keep the raw recording. If the upload compresses the dashboard type into mush you will want to re-cut rather than re-record.
