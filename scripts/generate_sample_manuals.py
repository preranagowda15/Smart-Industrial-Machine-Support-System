"""
Generate official sample PDF manuals for HP-200 and AC-90 machines,
plus machine_manual_index.csv for metadata registration.
"""
import os
import csv
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

# Custom styles
title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Title"],
    fontSize=22,
    leading=26,
    textColor=colors.HexColor("#1d2a33"),
    spaceAfter=12,
)
h1_style = ParagraphStyle(
    "DocH1",
    parent=styles["Heading1"],
    fontSize=15,
    leading=18,
    textColor=colors.HexColor("#26414f"),
    spaceBefore=14,
    spaceAfter=8,
)
h2_style = ParagraphStyle(
    "DocH2",
    parent=styles["Heading2"],
    fontSize=12,
    leading=15,
    textColor=colors.HexColor("#26414f"),
    spaceBefore=10,
    spaceAfter=6,
)
body_style = ParagraphStyle(
    "DocBody",
    parent=styles["Normal"],
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor("#2c3e50"),
    spaceAfter=6,
)
code_style = ParagraphStyle(
    "DocCode",
    parent=styles["Code"],
    fontSize=9,
    leading=12,
    textColor=colors.HexColor("#b3392f"),
)

def build_pdf(filepath, elements):
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    doc.build(elements)
    print(f"Built PDF: {filepath}")

def generate_hp200_operations():
    elements = []
    # --- PAGE 1 ---
    elements.append(Paragraph("HP-200 Hydraulic Forming Press — Operations Manual", title_style))
    elements.append(Paragraph("Document ID: HP-OPS-01 | Revision: 1.0 | Machine Code: M-HP200", h2_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Section 1: Machine Overview & Operating Specifications", h1_style))
    elements.append(Paragraph(
        "The HP-200 is a 200-ton industrial hydraulic forming press engineered for precision metal stamping, "
        "deep drawing, and composite compression molding. It is equipped with a closed-loop proportional hydraulic system "
        "and digital programmable logic controller (PLC) architecture.",
        body_style
    ))
    elements.append(Paragraph("Operating Limits and Pressure Specifications:", h2_style))
    elements.append(Paragraph(
        "The maximum allowable operating pressure is 250 bar (3,625 psi). Under no operational circumstance or experimental tooling "
        "should the press be configured or operated above 250 bar under any load. Normal operating hydraulic pressure is set between "
        "180 bar and 220 bar depending on forming tonnage demands.",
        body_style
    ))
    elements.append(Paragraph(
        "Hydraulic Fluid Specifications: The reservoir capacity is 120 liters. Use only approved anti-wear ISO VG 46 hydraulic mineral oil. "
        "Hydraulic fluid operating temperature must remain between 35°C and 55°C. The maximum allowable oil temperature limit is 65°C, "
        "above which thermal degradation occurs.",
        body_style
    ))
    elements.append(Paragraph(
        "Platen and Tonnage Limits: Maximum press capacity is 2,000 kN (200 metric tons). Stroke length is 450 mm. "
        "Daylight opening is 750 mm. Fast approach speed is 180 mm/s, pressing speed is 8-20 mm/s, and return speed is 160 mm/s.",
        body_style
    ))
    elements.append(PageBreak())

    # --- PAGE 2 ---
    elements.append(Paragraph("Section 2: Alarm Diagnostics & Error Codes", h1_style))
    elements.append(Paragraph(
        "When the control system detects an operational fault, an audible beacon sounds and the diagnostic touch screen "
        "displays an alphanumeric error code. Refer to the diagnostic matrix below for required corrective actions.",
        body_style
    ))
    
    alarm_data = [
        ["Alarm Code", "Fault Description", "Root Cause & Remedial Action"],
        [
            "E17",
            "Main Ram Proportional Valve Command Signal Failure",
            "Indicates a command or position feedback deviation between the PLC axis controller and the proportional directional "
            "valve spool transducer. Action: 1) Verify 24V DC auxiliary power supply on terminal strip TB2; 2) Inspect wiring harness connector "
            "CN3 on the proportional valve driver card for loose pins; 3) Measure spool position feedback voltage (nominal 0-10V scale, "
            "neutral null is 5.0V ± 0.2V). If feedback is erratic or absent, recalibrate or replace the valve driver card."
        ],
        [
            "E21",
            "Low Hydraulic Oil Level",
            "The reservoir level float switch has tripped. Action: Immediately suspend automatic cycle. Visually inspect the tank sight "
            "glass and check for external hose or seal ruptures. Refill reservoir with clean, filtered ISO VG 46 fluid to the marked operating line."
        ],
        [
            "E04",
            "High Hydraulic Oil Temperature (>65°C)",
            "Hydraulic bulk temperature sensor exceeded 65°C threshold. Action: Stop machine cycle and allow pump to idle. Check water chiller "
            "inlet valve (minimum flow 20 L/min), inspect heat exchanger plates for scale, and verify cooler fan operation."
        ],
        [
            "E09",
            "Safety Light Curtain Obstruction / Muting Failure",
            "Optical beam interruption during down-stroke. Action: Clear foreign objects from light curtain path. Reset safety relay SR-1."
        ]
    ]
    t = Table(alarm_data, colWidths=[80, 160, 290])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#26414f")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f8f9fa")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#c9cfcb")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('LEADING', (0,1), (-1,-1), 11.5),
    ]))
    elements.append(t)
    elements.append(PageBreak())

    # --- PAGE 3 ---
    elements.append(Paragraph("Section 3: Standard Operating & Safety Procedures", h1_style))
    elements.append(Paragraph(
        "Shift Pre-Start Check: 1) Ensure main disconnect is locked ON; 2) Check that emergency stop buttons (platen front, rear, and pendant) "
        "are released; 3) Verify hydraulic fluid level is between MIN and MAX marks on the reservoir sight glass; 4) Check pressure gauge reads 0 bar "
        "before motor start.",
        body_style
    ))
    elements.append(Paragraph(
        "Operating Cycle Modes: The HP-200 supports Inching (Manual Set-up), Single Cycle Semi-Automatic, and Continuous Automatic mode. "
        "Inching mode requires two-hand concurrent depression of dual optical palm buttons. Releasing either palm button within the down-stroke "
        "halts ram motion within 40 milliseconds.",
        body_style
    ))
    elements.append(Paragraph(
        "Lockout / Tagout (LOTO) Regulations: Before any operator enters the die space for tool adjustment or cleaning, the mechanical ram "
        "safety restraint block must be swung into the vertical position beneath the upper platen, and the electrical lockout padlock applied to breaker CB1.",
        body_style
    ))
    return elements

def generate_hp200_maintenance():
    elements = []
    # --- PAGE 1 ---
    elements.append(Paragraph("HP-200 Hydraulic Forming Press — Maintenance Manual", title_style))
    elements.append(Paragraph("Document ID: HP-MNT-01 | Revision: 1.0 | Machine Code: M-HP200", h2_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Section 1: Routine Inspection & Lubrication Schedules", h1_style))
    elements.append(Paragraph(
        "Regular preventative maintenance ensures structural alignment and hydraulic integrity of the HP-200 press. "
        "All maintenance activities must be performed by certified industrial maintenance technicians.",
        body_style
    ))
    elements.append(Paragraph("Daily Inspection Items:", h2_style))
    elements.append(Paragraph(
        "1. Inspect all flexible hydraulic hoses and swivel joints for sweating, abrasions, or fluid weeping.<br/>"
        "2. Check main system pressure gauge and pilot pressure gauge for steady readings.<br/>"
        "3. Check oil reservoir temperature gauge and verify chiller water inlet valve is open.<br/>"
        "4. Confirm emergency stop circuit and dual-channel safety gate interlocks function properly.",
        body_style
    ))
    elements.append(Paragraph("Weekly and Monthly Inspection Schedules:", h2_style))
    elements.append(Paragraph(
        "Guide Column Lubrication: Grease the four chrome-plated vertical guide columns weekly using NLGI Grade 2 lithium complex grease. "
        "Pump 15 grams of grease into each of the four lower and upper bronze bushing grease fittings. Wipe off contaminated excess grease.",
        body_style
    ))
    elements.append(Paragraph(
        "Platen Alignment and Parallelism: Check upper and lower platen parallelism monthly using a dial indicator across four bed corners. "
        "Total runout must not exceed ± 0.05 mm across the entire 800 mm x 800 mm platen area. Re-shim guide gibs if clearance exceeds 0.08 mm.",
        body_style
    ))
    elements.append(Paragraph(
        "Accumulator Nitrogen Pre-charge: Check nitrogen pre-charge pressure on the bladder accumulator every 3 months. "
        "Nominal pre-charge is 90 bar (N2 only; never use compressed air or oxygen).",
        body_style
    ))
    elements.append(PageBreak())

    # --- PAGE 2 ---
    elements.append(Paragraph("Section 2: Filter Maintenance & Hydraulic Troubleshooting", h1_style))
    elements.append(Paragraph("Filter Replacement Intervals:", h2_style))
    elements.append(Paragraph(
        "The high-pressure inline hydraulic oil filter must be replaced every 500 operating hours, or immediately if the visual differential "
        "pressure indicator extends into the red band (indicating ΔP > 3.5 bar). Always inspect hydraulic hoses and manifold connections "
        "for leaks at every filter change. Reservoir hydraulic fluid must be replaced every 2,000 operating hours or annually after oil laboratory spectrometry testing.",
        body_style
    ))
    elements.append(Paragraph("Troubleshooting Repeated Low Hydraulic Pressure:", h1_style))
    elements.append(Paragraph(
        "When repeated low hydraulic pressure alarms or cycle sluggishness occurs, collect the following systematic observations "
        "before replacing hydraulic components:<br/>"
        "1. Record pump discharge pressure under deadhead dead-end condition and active forming load.<br/>"
        "2. Measure case drain leakage rate from the variable displacement axial piston pump: normal leakage is under 1.5 L/min; "
        "case drain flow exceeding 4.5 L/min at 200 bar indicates severe cylinder barrel or valve plate wear requiring pump rebuild.<br/>"
        "3. Inspect proportional pressure relief valve cartridge seat for erosion, particle contamination, or broken bias spring.<br/>"
        "4. Check differential pressure indicator on the main pressure line filter to rule out severe filter element clogging.<br/>"
        "5. Verify suction strainer in reservoir is not cavitating due to clogged 100-mesh wire cloth.",
        body_style
    ))
    elements.append(Paragraph("Tie Rod Pre-Tensioning:", h2_style))
    elements.append(Paragraph(
        "Inspect and torque tie rod tension nuts every 1,000 operating hours. Tighten in cross-pattern to 1,200 Nm using a hydraulic torque wrench.",
        body_style
    ))
    return elements

def generate_ac90_manual():
    elements = []
    # --- PAGE 1 ---
    elements.append(Paragraph("AC-90 Rotary Screw Compressor — Operations & Maintenance", title_style))
    elements.append(Paragraph("Document ID: AC-OM-01 | Revision: 1.0 | Machine Code: M-AC90", h2_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Section 1: Technical Specifications & Operating Parameters", h1_style))
    elements.append(Paragraph(
        "The AC-90 is a single-stage, oil-injected rotary screw air compressor designed for continuous heavy-duty industrial pneumatic service.",
        body_style
    ))
    elements.append(Paragraph("Operating Specifications and Limits:", h2_style))
    elements.append(Paragraph(
        "Rated discharge pressure is 8.0 bar (0.80 MPa / 116 psi). The safety pressure relief valve is factory set and certified to open at 10.0 bar (1.0 MPa). "
        "Free Air Delivery (FAD) is 9.2 m³/min. Drive motor is 55 kW, 400V 50Hz, 3-phase electric induction motor. "
        "Normal operating compressed air discharge temperature is 75°C to 88°C. Maximum trip temperature is 105°C.",
        body_style
    ))
    elements.append(Paragraph(
        "Lubrication System: Oil capacity is 25 liters of synthetic polyalphaolefin (PAO) ISO VG 46 rotary screw compressor oil. "
        "Oil carryover in delivered air is less than 3 ppm when the separator element is in sound condition.",
        body_style
    ))
    elements.append(PageBreak())

    # --- PAGE 2 ---
    elements.append(Paragraph("Section 2: Operating Controls and Alarms", h1_style))
    elements.append(Paragraph(
        "The microprocessor electronic controller continuously monitors air discharge temperature, system pressure, separator differential pressure, "
        "and motor running amps.",
        body_style
    ))
    elements.append(Paragraph("Alarm Code Matrix:", h2_style))
    elements.append(Paragraph(
        "Alarm H03 — High Discharge Air Temperature: Indicates air/oil mixture discharge temperature exceeded 105°C trip point. "
        "Action: Stop the compressor and allow it to cool down completely before inspecting. Check compressor oil level in receiver sight glass. "
        "Inspect oil cooler matrix fins for dust or lint accumulation and clean with compressed air reverse blow. Verify thermostatic mixing valve opens at 71°C.",
        body_style
    ))
    elements.append(Paragraph(
        "Alarm P02 — High Air Filter Differential: Intake vacuum exceeded 45 mbar. Action: Replace air intake filter cartridge.",
        body_style
    ))
    elements.append(Paragraph(
        "Alarm E01 — Main Motor Overload: Drive motor thermal overload trip. Action: Check electrical supply line balance and motor terminal lugs.",
        body_style
    ))
    elements.append(PageBreak())

    # --- PAGE 3 ---
    elements.append(Paragraph("Section 3: Maintenance Schedule and Preventative Servicing", h1_style))
    elements.append(Paragraph("Daily Servicing Items:", h2_style))
    elements.append(Paragraph(
        "1. Drain condensate from the receiver tank and moisture separator daily to prevent internal rust and moisture carryover.<br/>"
        "2. Check oil level on the receiver sight glass while the compressor is operating fully loaded.<br/>"
        "3. Check operating discharge pressure and display panel for advisory messages.",
        body_style
    ))
    elements.append(Paragraph("Scheduled Component Replacement Intervals:", h2_style))
    elements.append(Paragraph(
        "Replace Air Intake Filter: Replace the air intake filter cartridge every 2,000 operating hours, or sooner in dusty operating environments.<br/>"
        "Replace Oil Filter & Oil: Drain synthetic oil and replace spin-on oil filter element every 4,000 operating hours or every 12 months.<br/>"
        "Replace Air/Oil Separator: Replace air/oil separator element every 4,000 operating hours or whenever pressure drop across separator exceeds 1.0 bar.<br/>"
        "Drive Belt Inspection: Inspect drive belt tension and alignment every 500 operating hours. Standard belt deflection is 8-10 mm under 50 N center load.",
        body_style
    ))
    return elements

def generate_csv_metadata():
    csv_path = DATA_DIR / "machine_manual_index.csv"
    rows = [
        {
            "machine_id": "M-HP200",
            "model": "HP-200",
            "machine_name": "HP-200 Hydraulic Forming Press",
            "document_id": "HP-OPS-01",
            "revision": "1.0",
            "pdf_filename": "HP200_Operations_Rev1_0.pdf",
        },
        {
            "machine_id": "M-HP200",
            "model": "HP-200",
            "machine_name": "HP-200 Hydraulic Forming Press",
            "document_id": "HP-MNT-01",
            "revision": "1.0",
            "pdf_filename": "HP200_Maintenance_Rev1_0.pdf",
        },
        {
            "machine_id": "M-AC90",
            "model": "AC-90",
            "machine_name": "AC-90 Rotary Screw Compressor",
            "document_id": "AC-OM-01",
            "revision": "1.0",
            "pdf_filename": "AC90_Operations_Maintenance_Rev1_0.pdf",
        },
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["machine_id", "model", "machine_name", "document_id", "revision", "pdf_filename"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated CSV: {csv_path}")

def main():
    p1 = MANUALS_DIR / "HP200_Operations_Rev1_0.pdf"
    p2 = MANUALS_DIR / "HP200_Maintenance_Rev1_0.pdf"
    p3 = MANUALS_DIR / "AC90_Operations_Maintenance_Rev1_0.pdf"

    build_pdf(p1, generate_hp200_operations())
    build_pdf(p2, generate_hp200_maintenance())
    build_pdf(p3, generate_ac90_manual())

    # Also copy to media/manuals/ for direct serving
    import shutil
    shutil.copy(p1, MEDIA_MANUALS_DIR / p1.name)
    shutil.copy(p2, MEDIA_MANUALS_DIR / p2.name)
    shutil.copy(p3, MEDIA_MANUALS_DIR / p3.name)

    generate_csv_metadata()
    print("All sample manuals and metadata generated successfully.")

if __name__ == "__main__":
    main()
