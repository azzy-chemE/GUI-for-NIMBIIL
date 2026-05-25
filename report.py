"""
report.py — PDF report generation for NIIMBL Digital Twin GUI
Requires: reportlab

⚠️  PLACEHOLDER: Charts in the PDF are text-based summaries.
Once you have real simulation data, you can embed Plotly figures as images
using plotly.io.write_image + kaleido, then insert into the PDF.
"""

# Comments are sprinkled throughout the script to explain context and usage of certain functions
# and what calculations are for, but I have not defined generally known functions or structures
# in Python, which can be consulted/found independently using external sources.

import io
from datetime import datetime
import pandas as pd

def generate_pdf(run_params: dict, kpis: dict, df_time: pd.DataFrame,
                 df_glyco: pd.DataFrame, df_zones: pd.DataFrame) -> bytes:
    """Generate a PDF summary report and return as bytes."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
    )

    # ── Styles ──────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    TEAL  = colors.HexColor("#0A7A6E")
    NAVY  = colors.HexColor("#0D2137")
    SLATE = colors.HexColor("#2C4A5A")
    MUTED = colors.HexColor("#6B8A85")
    LIGHT = colors.HexColor("#F4F7F6")

    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=22,
        textColor=NAVY, spaceAfter=4, leading=28,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontName="Helvetica", fontSize=11,
        textColor=MUTED, spaceAfter=14,
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=13,
        textColor=TEAL, spaceBefore=14, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10,
        textColor=SLATE, spaceAfter=4, leading=14,
    )
    small_style = ParagraphStyle(
        "Small", parent=styles["Normal"],
        fontName="Helvetica-Oblique", fontSize=8,
        textColor=MUTED, spaceAfter=4,
    )
    center_style = ParagraphStyle(
        "Center", parent=body_style,
        alignment=TA_CENTER,
    )

    def table_style_default():
        return TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  TEAL),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, LIGHT]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#C8DAD7")),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ])

    # ── Content ─────────────────────────────────────────────────────────────
    story = []

    # Header
    story.append(Paragraph("NIIMBL Bioreactor Digital Twin", title_style))
    story.append(Paragraph("Simulation Report", subtitle_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y  %H:%M')}",
        small_style,
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=TEAL, spaceAfter=14))

    # ── Section 1: Run Parameters ──────────────────────────────────────────
    story.append(Paragraph("1. Run Parameters", section_style))
    param_data = [["Parameter", "Value"]] + [
        [k.replace("_", " ").title(), str(v)]
        for k, v in run_params.items()
    ]
    param_table = Table(param_data, colWidths=[9*cm, 8*cm])
    param_table.setStyle(table_style_default())
    story.append(param_table)

    # ── Section 2: Derived KPIs ────────────────────────────────────────────
    story.append(Paragraph("2. Derived Hydrodynamic KPIs", section_style))
    kpi_labels = {
        "power_input_W":   ("Power input", "W"),
        "P_per_V":         ("Power per unit volume (P/V)", "W/m³"),
        "mixing_time_s":   ("Estimated mixing time", "s"),
        "tip_speed_m_s":   ("Impeller tip speed", "m/s"),
        "kolmogorov_um":   ("Kolmogorov length scale", "μm"),
        "kLa_per_hr":      ("kLa (mass transfer coeff.)", "hr⁻¹"),
        "Re_imp":          ("Impeller Reynolds number", "—"),
    }
    kpi_data = [["KPI", "Value", "Unit"]] + [
        [label, str(kpis.get(key, "—")), unit]
        for key, (label, unit) in kpi_labels.items()
    ]
    kpi_table = Table(kpi_data, colWidths=[10*cm, 4.5*cm, 2.5*cm])
    kpi_table.setStyle(table_style_default())
    story.append(kpi_table)

    # ── Section 3: Cell Kinetics Summary ──────────────────────────────────
    story.append(Paragraph("3. Cell Kinetics Summary", section_style))
    story.append(Paragraph(
        "⚠ Placeholder — replace with compartment model outputs once CFD database is ready.",
        small_style,
    ))
    final_t = df_time.iloc[-1]
    peak_X  = df_time["cell_density_e6_cells_mL"].max()
    kin_data = [
        ["Metric", "Value", "Unit"],
        ["Peak cell density",    f"{peak_X:.2f}",                "×10⁶ cells/mL"],
        ["Final cell density",   f"{final_t['cell_density_e6_cells_mL']:.2f}", "×10⁶ cells/mL"],
        ["Final viability",      f"{final_t['viability_pct']:.1f}", "%"],
        ["Final titer",          f"{final_t['titer_mg_L']:.0f}",    "mg/L"],
        ["Avg DO",               f"{df_time['DO_pct'].mean():.1f}", "%"],
        ["Avg glucose",          f"{df_time['glucose_mM'].mean():.1f}", "mM"],
        ["Final lactate",        f"{final_t['lactate_mM']:.2f}",   "mM"],
    ]
    kin_table = Table(kin_data, colWidths=[9*cm, 4*cm, 4*cm])
    kin_table.setStyle(table_style_default())
    story.append(kin_table)

    # ── Section 4: Glycosylation Summary ──────────────────────────────────
    story.append(Paragraph("4. Glycosylation Profile (final time point)", section_style))
    story.append(Paragraph(
        "⚠ Placeholder — replace with glycosylation kinetics module outputs.",
        small_style,
    ))
    final_g = df_glyco.iloc[-1]
    glyco_data = [
        ["Glycan Species", "Fraction (%)"],
        ["G0F",   f"{final_g['G0F_pct']:.1f}"],
        ["G1F",   f"{final_g['G1F_pct']:.1f}"],
        ["G2F",   f"{final_g['G2F_pct']:.1f}"],
        ["Man5",  f"{final_g['Man5_pct']:.1f}"],
        ["Other", f"{final_g['Other_pct']:.1f}"],
    ]
    glyco_table = Table(glyco_data, colWidths=[9*cm, 8*cm])
    glyco_table.setStyle(table_style_default())
    story.append(glyco_table)

    # ── Section 5: Zone Analysis ───────────────────────────────────────────
    story.append(Paragraph("5. Zone Analysis Summary", section_style))
    story.append(Paragraph(
        "⚠ Placeholder — replace with RTD + DO integration from compartment model.",
        small_style,
    ))
    zone_summary = df_zones.groupby("zone_type").agg(
        n_compartments=("compartment", "count"),
        avg_DO_pct=("local_DO_pct", "mean"),
        avg_power=("local_power_W_m3", "mean"),
        avg_RT_hr=("residence_time_hr", "mean"),
    ).reset_index().round(2)

    zone_data = [["Zone Type", "# Compartments", "Avg DO (%)", "Avg Power (W/m³)", "Avg RT (hr)"]]
    for _, row in zone_summary.iterrows():
        zone_data.append([
            row["zone_type"],
            str(int(row["n_compartments"])),
            f"{row['avg_DO_pct']:.1f}",
            f"{row['avg_power']:.1f}",
            f"{row['avg_RT_hr']:.2f}",
        ])
    zone_table = Table(zone_data, colWidths=[5.5*cm, 3.5*cm, 3*cm, 3.5*cm, 2.5*cm])
    zone_table.setStyle(table_style_default())
    story.append(zone_table)

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED, spaceAfter=6))
    story.append(Paragraph(
        "NIIMBL Bioreactor Digital Twin  ·  All outputs are placeholders until real CFD database is connected.",
        small_style,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
