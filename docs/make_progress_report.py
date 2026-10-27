#!/usr/bin/env python3
"""Build the Week 4 progress report PDF."""

import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, KeepTogether, NextPageTemplate)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Week4_Progress_Report.pdf")

INK = colors.HexColor("#12181A")
INK2 = colors.HexColor("#2A3639")
MUTED = colors.HexColor("#6B7671")
RULE = colors.HexColor("#C7CDC6")
RULE2 = colors.HexColor("#E4E8E2")
GREEN = colors.HexColor("#0B6E4F")
RED = colors.HexColor("#A32A1F")
AMBER = colors.HexColor("#B8830C")
BAND = colors.HexColor("#F4F6F3")

W, H = A4
ML, MR, MT, MB = 20 * mm, 20 * mm, 26 * mm, 20 * mm

S = {}
S["body"] = ParagraphStyle("body", fontName="Helvetica", fontSize=9.6, leading=14.4,
                           textColor=INK2, spaceAfter=7, alignment=TA_LEFT)
S["h1"] = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=15, leading=18,
                         textColor=INK, spaceBefore=16, spaceAfter=8)
S["h2"] = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.8, leading=14,
                         textColor=INK, spaceBefore=11, spaceAfter=5)
S["eyebrow"] = ParagraphStyle("eyebrow", fontName="Courier-Bold", fontSize=7.6, leading=11,
                              textColor=MUTED, spaceAfter=3)
S["small"] = ParagraphStyle("small", fontName="Helvetica-Oblique", fontSize=8.4, leading=12,
                            textColor=MUTED, spaceAfter=6)
S["cell"] = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.6, leading=12, textColor=INK2)
S["cellb"] = ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=8.6, leading=12, textColor=INK)
S["mono"] = ParagraphStyle("mono", fontName="Courier", fontSize=8.2, leading=11.6, textColor=INK2)
S["cover_t"] = ParagraphStyle("cover_t", fontName="Helvetica-Bold", fontSize=27, leading=31,
                              textColor=colors.white, spaceAfter=6)
S["cover_s"] = ParagraphStyle("cover_s", fontName="Helvetica", fontSize=11, leading=16,
                              textColor=colors.HexColor("#9DAEA3"))

TITLE = "Week 4 progress report"


def p(t, st="body"):
    return Paragraph(t, S[st])


def bullets(items, style="body"):
    return [Paragraph("&bull;&nbsp;&nbsp;" + it, ParagraphStyle(
        "b", parent=S[style], leftIndent=10, bulletIndent=0, spaceAfter=4.5)) for it in items]


def table(head, rows, widths, zebra=True):
    data = [[Paragraph(h, S["cellb"]) for h in head]]
    for r in rows:
        data.append([Paragraph(str(c), S["cell"]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BAND),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, RULE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, RULE2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
    ]
    if zebra:
        for i in range(2, len(data), 2):
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#FAFBF9")))
    t.setStyle(TableStyle(style))
    return t


def callout(title, text, tone=AMBER):
    inner = [Paragraph(title, ParagraphStyle("ct", fontName="Courier-Bold", fontSize=8,
                                             textColor=tone, spaceAfter=4)),
             Paragraph(text, ParagraphStyle("cb", parent=S["body"], fontSize=9, spaceAfter=0))]
    t = Table([[inner]], colWidths=[W - ML - MR], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBFCFA")),
        ("BOX", (0, 0), (-1, -1), 0.8, tone),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def cover_bg(canv, doc):
    canv.saveState()
    canv.setFillColor(INK)
    canv.rect(0, H - 118 * mm, W, 118 * mm, stroke=0, fill=1)
    # perforation notches along the bottom edge of the band
    canv.setFillColor(colors.white)
    x = 4 * mm
    while x < W:
        canv.circle(x, H - 118 * mm, 2.6 * mm, stroke=0, fill=1)
        x += 7.8 * mm

    y = H - 30 * mm
    canv.setFont("Courier-Bold", 8.4)
    canv.setFillColor(colors.HexColor("#8FA096"))
    canv.drawString(ML, y, "S A F E X   S O L U T I O N S   /   W E E K   4   /   G R O U P   5 7")

    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 30)
    for i, line in enumerate(["Which language model", "should answer our", "customers first?"]):
        canv.drawString(ML, y - 18 * mm - i * 11.4 * mm, line)

    canv.setFont("Helvetica", 10.6)
    canv.setFillColor(colors.HexColor("#9DAEA3"))
    for i, line in enumerate([
        "A vendor evaluation for a courier operation deciding which model reads",
        "its inbound customer support first. Three providers, one prompt, thirty",
        "hand-labelled cases, one weighted recommendation.",
    ]):
        canv.drawString(ML, y - 62 * mm - i * 5.6 * mm, line)

    canv.setStrokeColor(colors.HexColor("#2E3B3E"))
    canv.setLineWidth(0.6)
    canv.line(ML, y - 72 * mm, W - MR, y - 72 * mm)
    canv.setFont("Courier", 8.2)
    canv.setFillColor(colors.HexColor("#7E9089"))
    canv.drawString(ML, y - 79 * mm, "Progress report  /  Fatima Naseer  /  Institute of Space Technology")
    canv.drawRightString(W - MR, y - 79 * mm, "9 August 2026")

    canv.restoreState()
    footer(canv, doc, first=True)


def footer(canv, doc, first=False):
    canv.saveState()
    canv.setFont("Courier", 7.4)
    canv.setFillColor(MUTED)
    canv.drawString(ML, 12 * mm, "Fatima Naseer  /  SafeX Solutions  /  Group 57  /  Week 4")
    canv.drawRightString(W - MR, 12 * mm, "Page %d" % canv.getPageNumber())
    if not first:
        canv.setStrokeColor(RULE2)
        canv.setLineWidth(0.5)
        canv.line(ML, 16 * mm, W - MR, 16 * mm)
        canv.setFont("Courier-Bold", 7.4)
        canv.setFillColor(MUTED)
        canv.drawString(ML, H - 15 * mm, TITLE.upper())
        canv.line(ML, H - 18 * mm, W - MR, H - 18 * mm)
    canv.restoreState()


def build():
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=ML, rightMargin=MR,
                          topMargin=MT, bottomMargin=MB, title=TITLE,
                          author="Fatima Naseer", subject="LLM vendor comparison, courier support triage")
    frame_cover = Frame(ML, MB, W - ML - MR, H - MB - 126 * mm, id="cover")
    frame_body = Frame(ML, MB + 6 * mm, W - ML - MR, H - MB - MT - 6 * mm, id="body")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame_cover], onPage=cover_bg),
        PageTemplate(id="body", frames=[frame_body], onPage=footer),
    ])

    F = []

    # ---------------- cover ----------------
    meta = [
        ["Candidate", "Fatima Naseer, Institute of Space Technology, Islamabad"],
        ["Group", "57, Group Leader Salman Aslam"],
        ["Week", "4, AI and ML department, client-ready sprint"],
        ["Project", "Which language model should answer our customers first"],
        ["Use case", "Inbound courier support triage and first reply"],
        ["Vendors tested", "OpenAI, Anthropic, Google, matched on small and fast tier"],
        ["Status", "Harness, eval set, dashboard and memo complete. Live run pending."],
    ]
    F.append(table(["Field", "Detail"], meta, [34 * mm, W - ML - MR - 34 * mm]))
    F.append(Spacer(1, 7 * mm))
    F.append(callout("READ THIS FIRST",
                     "The dashboard shipped with this report is currently rendering synthetic data, generated so the "
                     "layout could be reviewed before spending API credit. It carries a red band across the top saying "
                     "so. The benchmark has to be run against live keys before any figure in it is quoted to anyone. "
                     "Nothing in this progress report claims a measured result.", RED))

    F.append(NextPageTemplate("body"))
    F.append(PageBreak())

    # ---------------- 1 objective ----------------
    F.append(p("01", "eyebrow"))
    F.append(p("Objective and scope", "h1"))
    F.append(p("Compare three language model providers on one narrow job and recommend one, with enough working shown "
               "that somebody who disagrees can check the reasoning rather than argue about taste."))
    F.append(p("The job is first-line triage of inbound customer support for a courier business. One message arrives on "
               "WhatsApp or web chat, in English, Roman Urdu, or the mix people actually type. The model returns a JSON "
               "object carrying an intent label, three extracted entities, a routing decision, and a customer-facing "
               "reply. The JSON goes to the ticketing system and the reply goes to the customer."))
    F.append(p("This continues the courier business case from Week 3 rather than starting a new one. Week 3 established "
               "the operation; Week 4 answers a build decision inside it."))

    F.append(p("Why this scope and not a general comparison", "h2"))
    F.append(p("A general capability ranking would have been faster to produce and worth nothing to a decision maker. "
               "The question in front of an operations lead is not which model is cleverest. It is which one labels "
               "forty thousand messages a month correctly, cheaply, quickly, and without telling a customer something "
               "it invented."))

    # ---------------- 2 built ----------------
    F.append(p("02", "eyebrow"))
    F.append(p("What was built", "h1"))
    rows = [
        ["Evaluation set", "eval/eval_set.json", "Thirty cases labelled by hand before any model ran. Eight intents plus "
         "an out-of-scope class. Nine Roman Urdu, six mixed, fifteen English. Six deliberately adversarial."],
        ["Shared prompt", "eval/system_prompt.txt", "One file, sent byte for byte to all three vendors. Its SHA is printed "
         "in the report header so nobody has to take that on trust."],
        ["Vendor clients", "bench/providers.py", "Raw HTTP per vendor rather than SDKs, plus an optional path through a "
         "local LiteLLM gateway."],
        ["Scoring", "bench/scoring.py", "Six deterministic scorers, Wilson confidence intervals, percentile helpers. No "
         "model grades another model."],
        ["Runner", "bench/run_benchmark.py", "Concurrency, backoff on 429 only, per-vendor runs that merge into one "
         "results file, prompt-hash guard against mixing two prompts in one table."],
        ["Aggregation", "report/aggregate.py", "Every figure in the report is computed here and nowhere else, so there "
         "is one place a number can be wrong."],
        ["Dashboard", "report/dashboard.html", "Comparison table, accuracy breakdown, latency percentiles, cost against "
         "the human baseline, sensitivity analysis, side-by-side sample outputs, failure log."],
        ["Memo", "docs/recommendation_memo.md", "Generated from the same summary object as the dashboard, so the two "
         "cannot drift apart."],
        ["Methodology", "docs/methodology.md", "Every measure defined, including the six-line integration rubric that is "
         "scored by hand."],
        ["Workbooks", "trackers/", "Outreach tracker with dropdowns and a rules sheet, plus a live-formula scorecard so "
         "the weights can be argued with directly."],
        ["Outreach", "docs/outreach.md", "Three target organisations with the reasoning, and one message each."],
        ["Video script", "docs/video_script.md", "Seven-minute walkthrough, timed, with what to show on screen."],
    ]
    F.append(table(["Component", "Path", "What it is"],
                   rows, [26 * mm, 34 * mm, W - ML - MR - 60 * mm]))

    # ---------------- 3 method ----------------
    F.append(p("03", "eyebrow"))
    F.append(p("Method, in short", "h1"))
    F.append(p("Vendors were matched on tier rather than on brand. All three models are each vendor's small and fast "
               "tier, the class you would actually deploy at this volume. Comparing a frontier model from one vendor "
               "against a budget model from another produces a number that looks like a finding and means nothing."))
    F.append(Spacer(1, 2 * mm))
    F.append(table(["Axis", "Weight", "How it is scored"], [
        ["Accuracy", "40%", "Composite of six components: schema validity 20, intent 25, entity F1 20, routing action 15, "
         "grounding 10, policy facts 10. A reply that does not parse scores zero on all six."],
        ["Cost", "25%", "Token counts from each vendor's own usage field, priced at rates in config/pricing.json with the "
         "date they were checked. Cheapest scores 100, the rest scale by ratio."],
        ["Latency", "20%", "Scored on p95, not mean, because on WhatsApp the customers who leave are the ones in the tail. "
         "Full marks at or below the target, zero at or above the failure threshold."],
        ["Integration", "15%", "Six-line rubric scored by hand after writing the client code: SDK quality, structured "
         "output, docs, error semantics, rate limit headroom, data residency."],
    ], [22 * mm, 18 * mm, W - ML - MR - 40 * mm]))

    F.append(p("Fairness controls", "h2"))
    F.extend(bullets([
        "One prompt file, read once, hashed, sent identically to all three.",
        "Temperature zero everywhere, three repeats per case, so run-to-run variance shows up as a stability number "
        "instead of disappearing into an average.",
        "Raw HTTP rather than vendor SDKs, because a vendor whose SDK retries silently would post better latency for a "
        "reason that has nothing to do with the model.",
        "Same machine, same connection, same session for all three.",
        "The weighted score is recomputed under five different weight profiles. If the winner changes, the memo names "
        "the assumption the decision rests on instead of hiding it.",
    ]))

    # ---------------- 4 status ----------------
    F.append(p("04", "eyebrow"))
    F.append(p("Status", "h1"))
    F.append(table(["Deliverable", "State", "What remains"], [
        ["Comparison table", "Built, unpopulated", "Run the benchmark against live keys"],
        ["Sample outputs from each provider", "Built, unpopulated", "Same run fills this"],
        ["Recommendation memo", "Generated, awaiting real figures", "Regenerates automatically after the run"],
        ["Integration rubric", "Rubric written, unscored", "Score by hand after writing client code against each API"],
        ["Outreach messages", "Written", "Identify the right contact at each company, then send"],
        ["Outreach tracker", "Built", "One row per message on the day it goes out"],
        ["Walkthrough video", "Scripted", "Record after the dashboard holds real numbers"],
        ["Presentation slides", "Built", "Update the three figure slides after the run"],
    ], [46 * mm, 30 * mm, W - ML - MR - 76 * mm]))

    F.append(Spacer(1, 5 * mm))
    F.append(callout("WHY THE NUMBERS ARE NOT HERE YET",
                     "A full run is thirty cases times three repeats times three vendors, which is two hundred and "
                     "seventy requests. Free tiers rate-limit partway through that, which leaves a half-finished results "
                     "file. The runner was built to handle it by running one vendor at a time and merging into the same "
                     "file, but the run itself needs live keys on all three accounts. Publishing invented figures to fill "
                     "the gap would have made the report look finished and made it worthless.", AMBER))

    F.append(PageBreak())

    # ---------------- 5 daily log ----------------
    F.append(p("05", "eyebrow"))
    F.append(p("Daily work log", "h1"))
    F.append(p("Fill one row per working day, with actual hours. The first row shows the expected format and should be "
               "deleted before submission."))
    log_rows = [["Example, delete this row", "Mon", "3.5", "Drafted the eval set, wrote twelve of the thirty cases",
                 "Kept getting the Roman Urdu register wrong, went back to real WhatsApp screenshots"]]
    for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        log_rows.append(["", d, "", "", ""])
    F.append(table(["Date", "Day", "Hours", "What I worked on", "What got in the way"],
                   log_rows, [20 * mm, 12 * mm, 16 * mm, 52 * mm, W - ML - MR - 100 * mm]))

    # ---------------- 6 problems ----------------
    F.append(p("06", "eyebrow"))
    F.append(p("Problems encountered and how they were solved", "h1"))
    probs = [
        ["Vendor SDKs are not comparable",
         "Some SDKs retry internally and some do not. A vendor that retries silently posts better latency for a reason "
         "that has nothing to do with its model.",
         "Wrote the HTTP calls by hand, one small function per vendor, with identical timeout and retry policy. Writing "
         "them also turned into the evidence for the integration score."],
        ["Models wrapped valid JSON in a code fence",
         "Counting a fenced reply as invalid would have overstated the failure rate. Counting it as clean would have "
         "hidden a real integration cost, since production code has to strip it.",
         "Split into two measures: schema validity, and a separate clean-JSON rate that records how often the raw text "
         "needed unwrapping. Both appear in the comparison table."],
        ["Entity scoring rewarded returning nothing",
         "Most cases have at least one genuinely empty slot. A first version of the F1 counted those as correct, so a "
         "model that answered null to everything scored well.",
         "Slots empty in both the gold and the prediction are now excluded from the F1 entirely, so nulls earn nothing."],
        ["English keyword matching failed Roman Urdu replies",
         "A correct Urdu reply was scoring zero on policy coverage because the required fact was checked as an English "
         "string.",
         "Each required fact became a set of acceptable surface forms across both languages. A reply gets the mark for "
         "saying the thing, in whichever language the customer used."],
        ["Free-tier rate limits on a 270-request run",
         "Hitting a 429 partway through leaves a half-written results file and no record of which half is real.",
         "Backoff on 429 only, other errors recorded rather than retried, and per-vendor runs that merge into one file "
         "as long as the prompt hash matches. A smoke-test mode runs nine requests first."],
        ["Thirty cases cannot separate close vendors",
         "A bare percentage at this sample size implies precision the evidence does not support.",
         "Added Wilson confidence intervals to the intent accuracy row and stated a ten-point tie threshold in the memo, "
         "the methodology, and the dashboard itself."],
        ["The weights are a judgement, not a measurement",
         "Anyone can object that the weights were chosen to produce a preferred answer.",
         "The report recomputes the ranking under five weight profiles including cost-first and speed-first, and says in "
         "plain words whether the winner survives all five."],
        ["Risk of synthetic preview data being mistaken for a result",
         "A demo dataset built to check the layout is exactly the kind of thing that gets submitted by accident at 2am.",
         "The results file carries a provenance field, the dashboard renders a red band whenever it reads DEMO, the build "
         "script prints a warning, and the demo file is gitignored."],
    ]
    for title, prob, fix in probs:
        F.append(KeepTogether([
            p(title, "h2"),
            p("<font color='#A32A1F'><b>Problem.</b></font> " + prob),
            p("<font color='#0B6E4F'><b>Solution.</b></font> " + fix),
        ]))

    F.append(PageBreak())

    # ---------------- 7 outreach ----------------
    F.append(p("07", "eyebrow"))
    F.append(p("Client outreach", "h1"))
    F.append(p("Three e-commerce logistics companies in Pakistan, all tech-forward enough to already be thinking about "
               "support automation, and all small enough that a comparison like this is useful rather than something "
               "they have already paid a consultancy for."))
    F.append(table(["Organisation", "Why they fit", "Channel"], [
        ["PostEx", "Courier plus payments for e-commerce sellers, so support carries both delivery questions and money "
         "questions. The cash-on-delivery cases in the eval set are exactly their message mix.", "LinkedIn"],
        ["Rider", "Karachi last-mile built around online shippers, founded 2019, API-first. Volume high enough for "
         "per-contact support cost to be a real line item.", "LinkedIn"],
        ["Unity Retail", "Sells fulfilment software to merchants rather than delivering parcels, so their support "
         "conversations are with sellers rather than consumers. Same triage problem, different message mix.", "LinkedIn"],
    ], [26 * mm, W - ML - MR - 48 * mm, 22 * mm]))
    F.append(Spacer(1, 4 * mm))
    F.append(p("Rules held to", "h2"))
    F.extend(bullets([
        "One message per organisation, written and sent by hand. No automation, no list send.",
        "The message states plainly that I am an intern and that I am not selling anything.",
        "No claim to have studied their operation, because I have not. The offer is to show the method and ask where "
        "the test cases are wrong.",
        "A not-interested reply closes the row on the day it arrives, with no follow-up later.",
        "No reply after ten days is logged as no reply and the row closes.",
        "If a conversation ever reached paid work it would go through SafeX Solutions, and I would say so during the "
        "call rather than after it.",
    ]))

    # ---------------- 8 next week ----------------
    F.append(p("08", "eyebrow"))
    F.append(p("Next week", "h1"))
    F.append(table(["Priority", "Task", "Done when"], [
        ["1", "Run the full benchmark against live keys on all three vendors, one vendor at a time if rate limits bite",
         "results/results.json holds 270 records and the dashboard band reads Measured"],
        ["2", "Score the integration rubric by hand after writing client code against each API and deliberately "
         "triggering a few errors", "All eighteen rubric cells filled in config.yaml"],
        ["3", "Rebuild the dashboard and memo, update the three figure slides", "Red band gone, memo carries real numbers"],
        ["4", "Record the seven-minute walkthrough", "1080p, face visible on the open and close"],
        ["5", "Find the right contact at each of the three companies and send the messages", "Three rows in the tracker "
         "with dates"],
        ["6", "Expand the eval set toward a hundred cases and get a second person to label a sample independently",
         "Inter-annotator agreement measured and reported"],
        ["7", "Add prompt injection cases, since a customer message is untrusted input and nothing in this round tests it",
         "At least ten injection cases with gold behaviour defined"],
        ["8", "Rerun latency from the production region rather than a laptop", "p95 figures the ops team would accept in "
         "an SLA conversation"],
    ], [17 * mm, W - ML - MR - 72 * mm, 55 * mm]))

    F.append(Spacer(1, 5 * mm))
    F.append(p("Items 6 and 7 are the ones that would change the quality of the answer rather than its presentation. "
               "Thirty cases is enough to rule a vendor out and not enough to sign a contract, and untested prompt "
               "injection on a channel where the input is written by strangers is the largest open risk in the work."))

    doc.build(F)
    print(OUT)


if __name__ == "__main__":
    build()
