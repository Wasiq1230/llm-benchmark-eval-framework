#!/usr/bin/env python3
"""Build the two workbooks: the outreach tracker and the weighted scorecard."""

import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "12181A"
HEAD_FILL = PatternFill("solid", fgColor="1F2C2F")
BAND_FILL = PatternFill("solid", fgColor="EFF2EE")
INPUT_FILL = PatternFill("solid", fgColor="FFFFCC")
CALC_FILL = PatternFill("solid", fgColor="F2F5F1")
THIN = Side(style="thin", color="C7CDC6")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

H = Font(name="Arial", size=10, bold=True, color="FFFFFF")
B = Font(name="Arial", size=10, bold=True, color=INK)
N = Font(name="Arial", size=10, color=INK)
BLUE = Font(name="Arial", size=10, color="0000FF")
SM = Font(name="Arial", size=9, italic=True, color="5A6560")
TITLE = Font(name="Arial", size=14, bold=True, color=INK)


def header(ws, row, labels, widths):
    for i, (lab, wd) in enumerate(zip(labels, widths), start=1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font, c.fill, c.border = H, HEAD_FILL, BOX
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = wd
    ws.row_dimensions[row].height = 30
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


# ----------------------------------------------------------------------------
# 1. Outreach tracker
# ----------------------------------------------------------------------------
def outreach():
    wb = Workbook()
    ws = wb.active
    ws.title = "Outreach log"

    ws["A1"] = "Week 4 outreach tracker"
    ws["A1"].font = TITLE
    ws["A2"] = ("One row per organisation, filled in on the day the message goes out. "
                "Yellow cells are yours to type in. Silence counts as a response and gets "
                "logged as 'No reply'. A 'not interested' closes the row and nothing follows.")
    ws["A2"].font = SM
    ws.merge_cells("A2:J2")
    ws.row_dimensions[2].height = 28

    cols = ["Organisation", "Why they fit", "Platform", "Contact role",
            "Date sent", "Response", "Response date", "Call booked",
            "Outcome", "Notes"]
    widths = [20, 34, 14, 20, 12, 16, 13, 12, 22, 40]
    header(ws, 4, cols, widths)

    rows = [
        ["PostEx", "Courier plus payments for e-commerce sellers, so support carries both "
                   "delivery and money questions", "LinkedIn DM", "", "", "", "", "", "", ""],
        ["Rider", "Karachi last-mile built around online shippers, volume high enough for "
                  "per-contact support cost to matter", "LinkedIn DM", "", "", "", "", "", "", ""],
        ["Unity Retail", "Fulfilment software for merchants, so their support conversations "
                         "are with sellers rather than consumers", "LinkedIn DM", "", "", "", "", "", "", ""],
    ]
    for r, data in enumerate(rows, start=5):
        for c, v in enumerate(data, start=1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.border = BOX
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if c <= 3:
                cell.font = N
                cell.fill = BAND_FILL
            else:
                cell.font = BLUE
                cell.fill = INPUT_FILL
        ws.row_dimensions[r].height = 46

    # Example row, clearly marked, so the expected format is obvious.
    ex = ["Example row, delete before submitting", "Shows the format only", "LinkedIn DM",
          "Head of Customer Experience", "2026-08-11", "Replied", "2026-08-13", "Yes",
          "Intro call held 15 Aug", "Asked for the eval set, said their Urdu message share is higher than mine"]
    for c, v in enumerate(ex, start=1):
        cell = ws.cell(row=9, column=c, value=v)
        cell.font = SM
        cell.border = BOX
        cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[9].height = 42

    dv_resp = DataValidation(type="list",
                             formula1='"Replied,No reply,Not interested,Out of office,Referred on"',
                             allow_blank=True)
    dv_yn = DataValidation(type="list", formula1='"Yes,No,Pending"', allow_blank=True)
    ws.add_data_validation(dv_resp)
    ws.add_data_validation(dv_yn)
    dv_resp.add("F5:F8")
    dv_yn.add("H5:H8")

    ws2 = wb.create_sheet("Rules")
    ws2["A1"] = "Rules this log is kept under"
    ws2["A1"].font = TITLE
    ws2.column_dimensions["A"].width = 108
    for i, line in enumerate([
        "One message per organisation, written and sent by hand. No automation, no list sends.",
        "A 'not interested' reply closes the row on the day it arrives. No follow-up, no second attempt later.",
        "No reply after ten days is logged as 'No reply' and the row closes. Silence is an answer.",
        "The message says plainly that I am an intern and that I am not selling anything.",
        "I do not claim to have studied their operation, because I have not.",
        "If a conversation reaches actual paid work, it goes through SafeX Solutions, and I say so during the call.",
        "Nothing in this log is shared outside SafeX without the person's agreement.",
    ], start=3):
        c = ws2.cell(row=i, column=1, value=line)
        c.font = N
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws2.row_dimensions[i].height = 30

    path = os.path.join(HERE, "Week4_Outreach_Tracker.xlsx")
    wb.save(path)
    return path


# ----------------------------------------------------------------------------
# 2. Weighted scorecard, formulas live so the weights can be argued with
# ----------------------------------------------------------------------------
def scorecard():
    wb = Workbook()
    ws = wb.active
    ws.title = "Scorecard"

    ws["A1"] = "Vendor scorecard"
    ws["A1"].font = TITLE
    ws["A2"] = ("Type measured values into the yellow cells from report/dashboard.html. "
                "Everything else is a formula. Change a weight in B6:B9 and every score below "
                "recalculates, which is the point of having this alongside the dashboard.")
    ws["A2"].font = SM
    ws.merge_cells("A2:F2")
    ws.row_dimensions[2].height = 28

    ws["A4"] = "Decision weights"
    ws["A4"].font = B
    for i, (lab, val) in enumerate([("Accuracy", 0.40), ("Cost", 0.25),
                                    ("Latency", 0.20), ("Integration", 0.15)], start=5):
        ws.cell(row=i, column=1, value=lab).font = N
        c = ws.cell(row=i, column=2, value=val)
        c.font, c.fill, c.border = BLUE, INPUT_FILL, BOX
        c.number_format = "0%"
    ws["A9"] = "Total"
    ws["A9"].font = B
    ws["B9"] = "=SUM(B5:B8)"
    ws["B9"].font = B
    ws["B9"].number_format = "0%"
    ws["C9"] = '=IF(ABS(B9-1)<0.0001,"ok","weights must sum to 100%")'
    ws["C9"].font = SM

    ws["A11"] = "Measured inputs"
    ws["A11"].font = B
    header(ws, 12, ["Measure", "OpenAI", "Anthropic", "Google", "Direction", "Where it comes from"],
           [30, 14, 14, 14, 12, 46])
    ws.freeze_panes = "A13"

    inputs = [
        ("Accuracy composite (0 to 1)", 0.90, 0.93, 0.86, "higher", "Dashboard, comparison table, accuracy row"),
        ("Cost per 1,000 calls (USD)", 0.25, 1.15, 0.45, "lower", "Dashboard, comparison table, cost row"),
        ("Latency p95 (ms)", 1400, 1750, 1250, "lower", "Dashboard, comparison table, p95 row"),
        ("Integration rubric (1 to 5)", 4.3, 4.0, 3.8, "higher", "Scored by hand, rubric in docs/methodology.md"),
    ]
    for r, (lab, a, b, c, direction, src) in enumerate(inputs, start=13):
        ws.cell(row=r, column=1, value=lab).font = N
        for col, v in zip((2, 3, 4), (a, b, c)):
            cell = ws.cell(row=r, column=col, value=v)
            cell.font, cell.fill, cell.border = BLUE, INPUT_FILL, BOX
            cell.number_format = "0.00" if r != 15 else "#,##0"
        ws.cell(row=r, column=5, value=direction).font = SM
        ws.cell(row=r, column=6, value=src).font = SM

    ws["A18"] = ("Values above are placeholders that show the expected format. Replace all twelve "
                 "with your own measured numbers before using this sheet for anything.")
    ws["A18"].font = SM
    ws.merge_cells("A18:F18")

    ws["A20"] = "Latency scoring thresholds (ms)"
    ws["A20"].font = B
    ws["A21"] = "Full marks at or below"
    ws["A21"].font = N
    ws["B21"] = 2500
    ws["B21"].font, ws["B21"].fill, ws["B21"].border = BLUE, INPUT_FILL, BOX
    ws["A22"] = "Zero at or above"
    ws["A22"].font = N
    ws["B22"] = 6000
    ws["B22"].font, ws["B22"].fill, ws["B22"].border = BLUE, INPUT_FILL, BOX

    ws["A24"] = "Normalised scores out of 100"
    ws["A24"].font = B
    header(ws, 25, ["Axis", "OpenAI", "Anthropic", "Google", "", "How it is normalised"],
           [30, 14, 14, 14, 12, 46])

    # Accuracy: straight percentage.
    for col in "BCD":
        ws[f"{col}26"] = f"={col}13*100"
    ws["A26"] = "Accuracy"
    ws["F26"] = "Accuracy composite times 100"

    # Cost: cheapest gets 100, others scale by ratio.
    ws["A27"] = "Cost"
    for col in "BCD":
        ws[f"{col}27"] = f"=IF({col}14=0,0,MIN($B$14:$D$14)/{col}14*100)"
    ws["F27"] = "Cheapest vendor scores 100, the rest scale by the ratio"

    # Latency: piecewise between the two thresholds.
    ws["A28"] = "Latency"
    for col in "BCD":
        ws[f"{col}28"] = (f"=IF({col}15<=$B$21,100,IF({col}15>=$B$22,0,"
                          f"($B$22-{col}15)/($B$22-$B$21)*100))")
    ws["F28"] = "100 at or under the target p95, 0 at or over the failure threshold, linear between"

    # Integration: 1 to 5 mapped onto 0 to 100.
    ws["A29"] = "Integration"
    for col in "BCD":
        ws[f"{col}29"] = f"=({col}16-1)/4*100"
    ws["F29"] = "Rubric mean, rescaled so 1 becomes 0 and 5 becomes 100"

    for r in range(26, 30):
        ws.cell(row=r, column=1).font = B
        ws.cell(row=r, column=6).font = SM
        for col in (2, 3, 4):
            cell = ws.cell(row=r, column=col)
            cell.font, cell.fill, cell.border = N, CALC_FILL, BOX
            cell.number_format = "0.0"

    ws["A31"] = "Weighted score"
    ws["A31"].font = B
    for col in "BCD":
        ws[f"{col}31"] = (f"=IFERROR(({col}26*$B$5+{col}27*$B$6+{col}28*$B$7+{col}29*$B$8)/$B$9,0)")
        ws[f"{col}31"].font = Font(name="Arial", size=12, bold=True, color=INK)
        ws[f"{col}31"].number_format = "0.0"
        ws[f"{col}31"].border = BOX
    ws["F31"] = "Sum of axis scores times weights, divided by the weight total"
    ws["F31"].font = SM

    ws["A32"] = "Rank"
    ws["A32"].font = B
    for col in "BCD":
        ws[f"{col}32"] = f"=RANK({col}31,$B$31:$D$31,0)"
        ws[f"{col}32"].font = N
        ws[f"{col}32"].border = BOX

    ws["A34"] = "Winner"
    ws["A34"].font = B
    ws["B34"] = '=INDEX($B$25:$D$25,MATCH(MAX($B$31:$D$31),$B$31:$D$31,0))'
    ws["B34"].font = Font(name="Arial", size=12, bold=True, color="0B6E4F")

    ws["A36"] = ("Assumption: the four weights above were set for a courier support use case where a "
                 "mislabelled ticket costs staff time and a wrong reply costs customer trust. They are "
                 "a judgement, not a measurement. Move them and see whether the winner changes.")
    ws["A36"].font = SM
    ws.merge_cells("A36:F36")
    ws.row_dimensions[36].height = 30

    path = os.path.join(HERE, "Vendor_Scorecard.xlsx")
    wb.save(path)
    return path


if __name__ == "__main__":
    print(outreach())
    print(scorecard())
