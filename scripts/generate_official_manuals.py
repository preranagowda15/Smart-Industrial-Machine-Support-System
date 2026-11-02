"""
Generate the exact three official hackathon PDF manuals:
1. HP200_Operations_Rev1_0.pdf (3 pages)
2. AC90_Operations_Maintenance_Rev1_0.pdf (3 pages)
3. HP200_Maintenance_Rev1_0.pdf (3 pages)

Grounded with word-for-word accuracy to the hackathon dataset.
"""
import os
import shutil
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MANUALS_DIR = DATA_DIR / "Manuals"
MEDIA_MANUALS_DIR = BASE_DIR / "media" / "manuals"

MANUALS_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_MANUALS_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Title"],
    fontSize=20,
    leading=24,
    textColor=colors.black,
    alignment=0,
    spaceAfter=12,
    fontName="Helvetica-Bold",
)
meta_style = ParagraphStyle(
    "DocMeta",
    parent=styles["Normal"],
    fontSize=9.5,
    leading=14,
    textColor=colors.black,
    spaceAfter=4,
)
disclaimer_style = ParagraphStyle(
    "DocDisclaimer",
    parent=styles["Normal"],
    fontSize=9,
    leading=13,
    textColor=colors.black,
    spaceAfter=14,
)
h1_style = ParagraphStyle(
    "DocH1",
    parent=styles["Heading1"],
    fontSize=13,
    leading=17,
    textColor=colors.black,
    spaceBefore=12,
    spaceAfter=6,
    fontName="Helvetica-Bold",
)
h2_style = ParagraphStyle(
    "DocH2",
    parent=styles["Heading2"],
    fontSize=11,
    leading=15,
    textColor=colors.black,
    spaceBefore=8,
    spaceAfter=4,
    fontName="Helvetica-Bold",
)
body_style = ParagraphStyle(
    "DocBody",
    parent=styles["Normal"],
    fontSize=9.5,
    leading=14,
    textColor=colors.black,
    spaceAfter=8,
)
footer_style = ParagraphStyle(
    "DocFooter",
    parent=styles["Normal"],
    fontSize=8.5,
    leading=11,
    textColor=colors.black,
    spaceBefore=16,
)

def build_pdf(filepath, elements):
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=40,
        bottomMargin=40,
    )
    doc.build(elements)
    print(f"Generated official PDF: {filepath}")

def create_table(data, col_widths):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#eef2f6")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('LEADING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return t

# ========================================================
# 1. HP-200 Operations Manual (Document ID: HP-OPS-01)
# ========================================================
def generate_hp200_operations():
    elements = []

    # PAGE 1
    elements.append(Paragraph("HP 200 Operations Manual", title_style))
    elements.append(Paragraph("Document ID: HP-OPS-01 | Machine: M-HP200 / HP-200 | Revision: 1.0", meta_style))
    elements.append(Paragraph("Issued: October 1, 2026 | Publisher: Blessed IT Solution Pvt Ltd", meta_style))
    elements.append(Paragraph("Fictional equipment and specifications created solely for this hackathon. These documents are a closed demonstration dataset and must not be used to operate or maintain real equipment.", disclaimer_style))
    
    elements.append(Paragraph("Equipment identity and purpose", h1_style))
    elements.append(Paragraph("The fictional HP-200 is an enclosed hydraulic forming press in the demonstration factory. It shapes small metal blanks using a hydraulic ram. Its reference operating fluid is H46 hydraulic oil. Product quality classification and defect causes are not covered by this manual.", body_style))
    
    elements.append(Paragraph("Operating reference values", h1_style))
    t1 = create_table([
        ["Parameter", "HP-200 reference"],
        ["Normal hydraulic pressure", "120 to 140 bar during the forming stage"],
        ["Oil temperature ready range", "35 to 55 degrees C"],
        ["Oil temperature high warning", "Above 60 degrees C"],
        ["Oil temperature high stop", "65 degrees C or higher"],
        ["Reservoir level indication", "Between MIN and MAX sight-glass marks"],
        ["Pressure-low trigger", "Below 110 bar for more than 5 seconds during forming"],
    ], [200, 320])
    elements.append(t1)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Machine states", h1_style))
    elements.append(Paragraph("OFF means the demonstration machine is not running. READY requires the guard-closed indicator, oil level within the marked range, and oil temperature in the ready range. FORMING is the stage in which the pressure range applies. HOLD means a fault has interrupted the cycle; a recorded review is required before resumption.", body_style))
    elements.append(Paragraph("A ready-state reading does not establish the pressure reached during forming. A pressure reading alone does not identify a failed component. Use alarm context and the maintenance reference when answering diagnostic questions.", body_style))
    
    elements.append(Paragraph("Document map", h1_style))
    elements.append(Paragraph("Page 2 describes the operator workflow and alarms. Page 3 describes fault reporting and limits of available information. For inspection intervals and maintenance checks, use HP-MNT-01, revision 1.0. It complements this manual and is not a replacement revision.", body_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("HP-OPS-01 | Rev 1.0 | Page 1", footer_style))
    elements.append(PageBreak())

    # PAGE 2
    elements.append(Paragraph("Operator Workflow and Alarm Reference", title_style))
    elements.append(Paragraph("Pre-cycle review", h1_style))
    elements.append(Paragraph("In the demonstration workflow, the operator checks the machine ID, reads the displayed state, confirms the guard-closed indicator, checks the reservoir level against MIN and MAX, and records the oil temperature. If a required indication is abnormal, the cycle remains on HOLD and the issue is reported. A guard interlock must never be bypassed.", body_style))

    elements.append(Paragraph("Alarm codes", h1_style))
    t2 = create_table([
        ["Code", "Meaning", "Documented response"],
        ["E17", "Low hydraulic pressure", "Record pressure and cycle stage; place on HOLD and request the checks in HP-MNT-01 page 3."],
        ["E24", "Oil temperature high warning", "Above 60 degrees C: hold the cycle and request cooling-system inspection. At 65 degrees C or higher, the high-temperature stop applies."],
        ["E31", "Guard-open indication", "Keep the cycle inhibited. Report an indication that remains open when the guard is closed; never bypass the interlock."],
        ["E42", "Return-filter restriction", "Record the indicator state and request the filter inspection in HP-MNT-01 page 2."],
    ], [50, 160, 310])
    elements.append(t2)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Interpreting E17", h1_style))
    elements.append(Paragraph("E17 is generated when pressure stays below 110 bar for more than 5 seconds during forming. The normal forming range is 120 to 140 bar. E17 does not prove that a pump has failed. The maintenance manual lists evidence to collect before selecting a cause.", body_style))

    elements.append(Paragraph("Temperature response", h1_style))
    elements.append(Paragraph("A reading of 62 degrees C is above the warning threshold but below the high-stop threshold. The warning response still requires a hold and cooling-system inspection. A reading of 65 degrees C meets the high-stop condition. The reference does not provide a guaranteed cooldown duration.", body_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("HP-OPS-01 | Rev 1.0 | Page 2", footer_style))
    elements.append(PageBreak())

    # PAGE 3
    elements.append(Paragraph("Fault Reporting and Scope of Guidance", title_style))
    elements.append(Paragraph("Information to record", h1_style))
    elements.append(Paragraph("An HP-200 escalation record includes machine ID M-HP200, timestamp, active alarm code, displayed pressure, oil temperature, cycle stage, reservoir indication, visible leak observations, and whether the issue repeated. Record observations separately from suspected causes.", body_style))

    elements.append(Paragraph("Repeated pressure loss", h1_style))
    elements.append(Paragraph("If E17 repeats after the documented checks have been reviewed, keep the demonstration machine on HOLD and escalate to authorized maintenance. Include the previous incident reference. Do not raise the pressure setting to suppress the alarm. Detailed low-pressure checks are in HP-MNT-01 page 3.", body_style))

    elements.append(Paragraph("Who reviews the event", h1_style))
    elements.append(Paragraph("The operator records the symptoms. Authorized maintenance reviews inspection findings. The supervisor records the decision on whether the issue has been resolved. The portal may summarize this workflow but must not issue commands to actual equipment.", body_style))

    elements.append(Paragraph("Relationship to the maintenance manual", h1_style))
    elements.append(Paragraph("HP-OPS-01 supplies operating ranges, alarm definitions, and reporting requirements. HP-MNT-01 supplies inspection intervals and maintenance observations. When a question asks for both the E17 trigger and the first inspection checks, cite the relevant pages from both documents.", body_style))

    elements.append(Paragraph("Information not provided", h1_style))
    elements.append(Paragraph("This dataset does not specify the pump replacement price, supplier contacts, tightening torque, wiring diagrams, hydraulic circuit drawings, internal repair procedures, pressure adjustment instructions, cycle-time guarantee, or service contract coverage. Questions requiring those details cannot be answered from these manuals.", body_style))
    elements.append(Paragraph("No conclusion about a future failure date or remaining useful life is supported by this document. An alarm is a reported condition, not a prediction of when the equipment will fail.", body_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("HP-OPS-01 | Rev 1.0 | Page 3", footer_style))

    return elements

# ========================================================
# 2. AC-90 Operations and Maintenance Manual (Document ID: AC-OM-01)
# ========================================================
def generate_ac90_manual():
    elements = []

    # PAGE 1
    elements.append(Paragraph("AC 90 Operations and Maintenance Manual", title_style))
    elements.append(Paragraph("Document ID: AC-OM-01 | Machine: M-AC90 / AC-90 | Revision: 1.0", meta_style))
    elements.append(Paragraph("Issued: October 1, 2026 | Publisher: Blessed IT Solution Pvt Ltd", meta_style))
    elements.append(Paragraph("Fictional equipment and specifications created solely for this hackathon. These documents are a closed demonstration dataset and must not be used to operate or maintain real equipment.", disclaimer_style))

    elements.append(Paragraph("Equipment identity and purpose", h1_style))
    elements.append(Paragraph("The fictional AC-90 is an enclosed air compressor supplying compressed air to a demonstration production line. It is a different machine from the HP-200 hydraulic press. It uses AC-L32 compressor lubricant in this dataset. Do not transfer hydraulic-press values, oil types, or alarm definitions to this compressor.", body_style))

    elements.append(Paragraph("Operating reference values", h1_style))
    t1 = create_table([
        ["Parameter", "AC-90 reference"],
        ["Normal outlet pressure", "7.0 to 8.0 bar under steady demand"],
        ["Pressure-low warning", "Below 6.5 bar for more than 10 seconds under steady demand"],
        ["Discharge temperature normal range", "70 to 90 degrees C"],
        ["High discharge-temperature warning", "Above 95 degrees C"],
        ["High discharge-temperature stop", "105 degrees C or higher"],
        ["Lubricant level indication", "Between LOW and HIGH marks"],
    ], [200, 320])
    elements.append(t1)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Operating states", h1_style))
    elements.append(Paragraph("READY means the required indications are acceptable before the demonstration run. LOADED means the compressor is supplying air under demand; the normal outlet-pressure range applies to steady demand in this state. HOLD means operation has been interrupted for review. A transient pressure dip is not automatically the defined pressure-low warning.", body_style))

    elements.append(Paragraph("Document map", h1_style))
    elements.append(Paragraph("Page 2 defines alarm codes and their documented responses. Page 3 lists maintenance intervals and escalation requirements. This single AC-90 manual is the complete reference for M-AC90 in the student pack. No AC-90 supplementary manual is provided.", body_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("AC-OM-01 | Rev 1.0 | Page 1", footer_style))
    elements.append(PageBreak())

    # PAGE 2
    elements.append(Paragraph("Alarm Reference and Diagnostic Limits", title_style))
    elements.append(Paragraph("Alarm codes", h1_style))
    t2 = create_table([
        ["Code", "AC-90 meaning", "Documented response"],
        ["E17", "High discharge temperature", "Record temperature; above 95 degrees C, hold and request cooling-path review. At 105 degrees C or higher, the high-temperature stop applies."],
        ["E08", "Low outlet pressure", "Below 6.5 bar for more than 10 seconds under steady demand: record demand and pressure; request leak and inlet-filter review."],
        ["E31", "Condensate-drain fault", "Record the drain fault indication and request authorized drain inspection. This is not a guard-open code on AC-90."],
        ["E42", "Inlet-filter restriction", "Record the inlet-filter indicator and review the AF-10 service history."],
    ], [50, 160, 310])
    elements.append(t2)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("High discharge temperature or E17", h1_style))
    elements.append(Paragraph("Review the reported cooling-air path condition, cooling-fan status indication, lubricant-level indication, and recent demand pattern. A reading of 98 degrees C exceeds the warning level but is below the stop threshold. Keep the event on HOLD for review. The dataset does not establish the cause from temperature alone.", body_style))

    elements.append(Paragraph("Low outlet pressure or E08", h1_style))
    elements.append(Paragraph("Record the pressure, duration of the low reading, and demand state. Report visible or audible leak observations without attempting repair, then review the AF-10 restriction indication. A low-pressure event does not by itself prove a worn compressor element. Internal diagnostic procedures are not provided.", body_style))

    elements.append(Paragraph("Machine-specific codes", h1_style))
    elements.append(Paragraph("E17 on AC-90 means high discharge temperature; E17 on another machine may mean something else. Interpret the code using the selected machine and its own manual. This page does not authorize adjustment of pressure or temperature limits.", body_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("AC-OM-01 | Rev 1.0 | Page 2", footer_style))
    elements.append(PageBreak())

    # PAGE 3
    elements.append(Paragraph("Maintenance Schedule and Escalation", title_style))
    t3 = create_table([
        ["When", "AC-90 item", "Required record"],
        ["Before each shift", "Lubricant level and condensate-drain status", "LOW-to-HIGH level indication and drain status"],
        ["Every 100 operating hours", "AF-10 inlet-filter restriction indicator", "Indicator state and abnormal findings"],
        ["Every 400 operating hours", "External cooling-air path", "Obstruction observation and reviewer"],
        ["Every 600 operating hours", "Planned AF-10 replacement", "Part identifier, hours, date, reviewer"],
        ["Every 3,000 hours or 12 months", "Planned AC-L32 lubricant replacement", "Whichever limit occurs first; record date and hours"],
    ], [130, 180, 210])
    elements.append(t3)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Inspection and replacement are different", h1_style))
    elements.append(Paragraph("The AF-10 indicator is checked every 100 operating hours; planned replacement is every 600 hours. Confirmed restriction can require earlier authorized replacement. A calendar interval for AF-10 replacement is not supplied. The HP-200 RF-20 filter is not the AC-90 filter.", body_style))

    elements.append(Paragraph("Escalation and review", h1_style))
    elements.append(Paragraph("Record machine ID M-AC90, timestamp, operating hours, active alarm, outlet pressure, discharge temperature, demand state, lubricant indication, filter indication, drain status where relevant, and previous incident reference. Repeated warnings or unresolved abnormal indications remain on HOLD for authorized review.", body_style))
    elements.append(Paragraph("Physical maintenance requires authorized personnel and the site's isolation and pressure-release procedure, which is not supplied here. The supervisor records any return-to-service decision. The assistant may summarize documented information but cannot authorize operation.", body_style))

    elements.append(Paragraph("Information not provided", h1_style))
    elements.append(Paragraph("This manual does not supply maintenance costs, spare-part prices, supplier contacts, electrical diagrams, tightening torques, motor rewinding steps, compressor-element replacement steps, expected remaining life, or a guaranteed repair time. Do not invent these details.", body_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("AC-OM-01 | Rev 1.0 | Page 3", footer_style))

    return elements

# ========================================================
# 3. HP-200 Maintenance Manual (Document ID: HP-MNT-01)
# ========================================================
def generate_hp200_maintenance():
    elements = []

    # PAGE 1
    elements.append(Paragraph("HP 200 Maintenance Manual", title_style))
    elements.append(Paragraph("Document ID: HP-MNT-01 | Machine: M-HP200 / HP-200 | Revision: 1.0", meta_style))
    elements.append(Paragraph("Issued: October 1, 2026 | Publisher: Blessed IT Solution Pvt Ltd", meta_style))
    elements.append(Paragraph("Fictional equipment and specifications created solely for this hackathon. These documents are a closed demonstration dataset and must not be used to operate or maintain real equipment.", disclaimer_style))

    elements.append(Paragraph("Coverage", h1_style))
    elements.append(Paragraph("This manual covers observation-based inspection and escalation for the fictional HP-200 hydraulic press. It applies only to M-HP200. It complements HP-OPS-01 revision 1.0; both manuals are current in this dataset. It does not describe internal component repairs or authorize physical work on real equipment.", body_style))

    elements.append(Paragraph("Maintenance reference data", h1_style))
    t1 = create_table([
        ["Item", "HP-200 reference"],
        ["Hydraulic fluid", "H46 hydraulic oil"],
        ["Return-filter identifier", "RF-20"],
        ["Reservoir level", "Between MIN and MAX marks"],
        ["Oil replacement interval", "Every 2,000 operating hours or 12 months, whichever occurs first"],
        ["Return-filter planned replacement", "Every 500 operating hours or earlier after confirmed restriction"],
        ["Condition requiring escalation", "Repeated alarms, confirmed leaks, or an abnormal indicator that persists"],
    ], [180, 340])
    elements.append(t1)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Inspection boundaries", h1_style))
    elements.append(Paragraph("Any physical inspection or maintenance requires an authorized person to follow the site's isolation and stored-energy procedure. This training dataset does not supply that procedure. Observations must not be treated as permission to open pressurized lines, remove guards, or adjust operating settings.", body_style))

    elements.append(Paragraph("Recording completed work", h1_style))
    elements.append(Paragraph("Record machine ID, operating-hour reading, date, inspection item, observation, action reference, and reviewer. Record actual findings; do not mark a check complete because an AI answer suggested it. A completed inspection does not by itself prove a fault is resolved.", body_style))
    elements.append(Paragraph("Page 2 contains the inspection schedule. Page 3 contains low-pressure and cooling checks. Operating ranges and alarm thresholds are defined in HP-OPS-01.", body_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("HP-MNT-01 | Rev 1.0 | Page 1", footer_style))
    elements.append(PageBreak())

    # PAGE 2
    elements.append(Paragraph("Inspection Schedule and Filter Reference", title_style))
    t2 = create_table([
        ["When", "Inspection item", "Record or escalation"],
        ["Before each shift", "Reservoir sight-glass and visible leakage", "Record MIN-to-MAX indication; report low level or a visible leak."],
        ["Every 50 operating hours", "Return-filter restriction indicator for RF-20", "Record indicator state. A restriction indication requires maintenance review."],
        ["Every 250 operating hours", "Cooling-air path and external hose condition", "Record obstruction, visible damage, or leakage; escalate abnormalities."],
        ["Every 500 operating hours", "Planned RF-20 replacement", "Record the replacement reference and reviewer; earlier replacement may follow confirmed restriction."],
        ["Every 2,000 hours or 12 months", "Planned H46 oil replacement", "Use whichever limit occurs first; record hours and date."],
    ], [120, 190, 210])
    elements.append(t2)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("E42 and the return filter", h1_style))
    elements.append(Paragraph("E42 refers to return-filter restriction on the HP-200. The applicable filter identifier is RF-20. Review the restriction indicator and the last service record. A confirmed restriction may require replacement before the planned 500-hour interval. A calendar interval for RF-20 replacement is not specified.", body_style))

    elements.append(Paragraph("Oil replacement example", h1_style))
    elements.append(Paragraph("If oil has been in service for 12 months but the machine has run only 1,400 hours, the calendar limit has been reached. If it has run 2,000 hours in eight months, the operating-hour limit has been reached. The rule is whichever occurs first; it is not necessary for both limits to be met.", body_style))

    elements.append(Paragraph("Scope of the schedule", h1_style))
    elements.append(Paragraph("These are the only inspection intervals provided in the dataset. Do not infer a daily, weekly, or annual interval for an item unless the schedule explicitly states it. No spare-part price or supplier is included.", body_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("HP-MNT-01 | Rev 1.0 | Page 2", footer_style))
    elements.append(PageBreak())

    # PAGE 3
    elements.append(Paragraph("Troubleshooting Observations and Escalation", title_style))
    elements.append(Paragraph("Low hydraulic pressure or E17", h1_style))
    elements.append(Paragraph("Collect these observations in order: (1) reservoir level relative to MIN and MAX; (2) visible external leakage reported by the operator; (3) RF-20 restriction-indicator state; (4) oil temperature and the recorded pressure during forming. Use the operating manual to interpret the pressure and temperature values.", body_style))
    elements.append(Paragraph("A low reservoir indication, a visible leak, or filter restriction is a finding to review, not a confirmed root cause. The manuals do not contain a test that proves pump failure. If E17 repeats after review, retain HOLD status and escalate to authorized maintenance with the findings and prior incident reference.", body_style))

    elements.append(Paragraph("High oil temperature or E24", h1_style))
    elements.append(Paragraph("Review the cooling-air path for reported obstruction, the cooling-fan status indication, reservoir level, and the recent operating pattern. Record all findings. The operating manual supplies the E24 warning and high-stop temperatures. The dataset does not specify a cooling-fan replacement procedure or a predicted cooldown time.", body_style))

    elements.append(Paragraph("Escalation record", h1_style))
    elements.append(Paragraph("Include machine ID, date and time, hours, alarm code, pressure, oil temperature, reservoir level, leak observation, filter indicator, cooling-fan indication where relevant, previous incident ID, and reviewer. Keep confirmed observations separate from suspected explanations.", body_style))

    elements.append(Paragraph("Return to service", h1_style))
    elements.append(Paragraph("Return-to-service authorization belongs to the designated supervisor after maintenance review under site procedures. An AI-generated checklist or a cleared alarm alone is not authorization. The portal records the decision; it does not control the press.", body_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("HP-MNT-01 | Rev 1.0 | Page 3", footer_style))

    return elements

def main():
    print("Building exact official manuals...")
    hp_ops_pdf = MANUALS_DIR / "HP200_Operations_Rev1_0.pdf"
    ac_pdf = MANUALS_DIR / "AC90_Operations_Maintenance_Rev1_0.pdf"
    hp_mnt_pdf = MANUALS_DIR / "HP200_Maintenance_Rev1_0.pdf"

    build_pdf(hp_ops_pdf, generate_hp200_operations())
    build_pdf(ac_pdf, generate_ac90_manual())
    build_pdf(hp_mnt_pdf, generate_hp200_maintenance())

    # Also copy to media/manuals/
    for p in [hp_ops_pdf, ac_pdf, hp_mnt_pdf]:
        dest = MEDIA_MANUALS_DIR / p.name
        shutil.copy2(p, dest)
        print(f"Copied to media: {dest}")

    print("\nAll 3 official PDF manuals successfully generated with exact page layouts!")

if __name__ == "__main__":
    main()

