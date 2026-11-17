"""Builds reports/test_report.pdf from the REAL results of the last pytest run
(reports/junit.xml) plus screenshots in screenshots/. Run pytest first."""
import platform
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import config

junit = config.REPORT_DIR / "junit.xml"
if not junit.exists():
    sys.exit("reports/junit.xml not found. Run pytest first.")

rows, counts = [], {"passed": 0, "failed": 0, "skipped": 0}
for case in ET.parse(junit).getroot().iter("testcase"):
    status, note = "PASSED", ""
    if case.find("failure") is not None or case.find("error") is not None:
        node = case.find("failure") if case.find("failure") is not None else case.find("error")
        status, note = "FAILED", (node.get("message") or "")[:160]
    elif case.find("skipped") is not None:
        status, note = "SKIPPED", (case.find("skipped").get("message") or "")[:160]
    counts[status.lower()] += 1
    rows.append((case.get("name"), status, f'{float(case.get("time", 0)):.1f}s', note))

styles = getSampleStyleSheet()
story = [
    Paragraph("QA Signup Automation - Test Report", styles["Title"]),
    Paragraph(f"Target: {config.BASE_URL}/register", styles["Normal"]),
    Paragraph(f"Generated: {datetime.now():%Y-%m-%d %H:%M}", styles["Normal"]),
    Paragraph(f"Environment: {platform.system()} {platform.release()}, Python {platform.python_version()}, "
              f"browser channel: {config.BROWSER_CHANNEL or 'bundled Chromium'}", styles["Normal"]),
    Spacer(1, 12),
    Paragraph(f"Summary: {counts['passed']} passed, {counts['failed']} failed, {counts['skipped']} skipped "
              f"(skipped tests were not executed).", styles["Heading3"]),
]
table = Table([["Test case", "Status", "Time", "Notes"]] +
              [[Paragraph(r[0], styles["BodyText"]), r[1], r[2], Paragraph(r[3], styles["BodyText"])] for r in rows],
              colWidths=[210, 55, 40, 190], repeatRows=1)
style = [("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
         ("VALIGN", (0, 0), (-1, -1), "TOP")]
for i, r in enumerate(rows, start=1):
    c = {"PASSED": colors.green, "FAILED": colors.red, "SKIPPED": colors.orange}[r[1]]
    style.append(("TEXTCOLOR", (1, i), (1, i), c))
table.setStyle(TableStyle(style))
story += [table, PageBreak(), Paragraph("Evidence screenshots (captured during the run)", styles["Heading2"])]
for shot in sorted(config.SCREENSHOT_DIR.glob("*.png")):
    story += [Paragraph(shot.name, styles["Heading4"]), Image(str(shot), width=420, height=240, kind="proportional"),
              Spacer(1, 8)]
out = config.REPORT_DIR / "test_report.pdf"
SimpleDocTemplate(str(out), pagesize=A4).build(story)
print("Wrote", out)
