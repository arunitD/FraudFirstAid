"""
pdf_pack.py - Generates PDF Evidence Dossier using ReportLab.
Includes:
  - Official Header and Reference Metadata
  - Incident Summary Block
  - Specific Fraud Category Details
  - Chronological Incident Timeline
  - Cryptographic Evidence Integrity Table (Filename, SHA-256, Timestamp)
  - Footer Disclaimer & Signatures
"""

import io
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4B5563"))

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 805, 555, 805)
        self.drawString(40, 810, "FRAUDFIRSTAID INDIA — CYBER FINANCIAL FRAUD EVIDENCE DOSSIER")
        self.drawRightString(555, 810, f"Page {self._pageNumber} of {page_count}")

        self.line(40, 45, 555, 45)
        disclaimer = "Documentation aid only; not legal advice; does not replace 1930, bank or police; cryptographic hashes show tampering, not authenticity."
        self.drawString(40, 34, disclaimer)
        self.drawRightString(555, 24, "CONFIDENTIAL — FOR INVESTIGATIVE USE ONLY")
        self.restoreState()


def generate_pdf_pack(data: Dict[str, Any], evidence_list: List[Dict[str, Any]]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#991B1B"),
        alignment=TA_LEFT,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#4B5563"),
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1F2937"),
        alignment=TA_JUSTIFY,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#111827"),
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
    )

    hash_cell_style = ParagraphStyle(
        "HashCell",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#1E3A8A"),
    )

    elements = []

    elements.append(Paragraph("FRAUDFIRSTAID EVIDENCE DOSSIER", title_style))
    elements.append(Paragraph("Incident Record & Cryptographic Evidence Pack for 1930 / Bank / cybercrime.gov.in", subtitle_style))
    elements.append(Spacer(1, 8))

    alert_text = (
        "<b>EMERGENCY PROTOCOL STATUS:</b> This document compiles victim declarations, "
        "transaction markers (UTR / UPI ID), and cryptographic SHA-256 integrity proofs. "
        "Submitted to facilitate urgent inter-bank freeze under the National Cyber Crime Reporting Portal framework."
    )
    alert_table = Table(
        [[Paragraph(alert_text, ParagraphStyle("Alert", parent=body_style, fontSize=8, leading=11, textColor=colors.HexColor("#9A3412")))]],
        colWidths=[515],
    )
    alert_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7ED")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FDBA74")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(alert_table)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("1. INCIDENT & TRANSACTION SUMMARY", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=6))

    summary_data = [
        [Paragraph("Victim Full Name:", table_cell_bold), Paragraph(str(data.get("name", "N/A")), table_cell_style),
         Paragraph("Contact Phone:", table_cell_bold), Paragraph(str(data.get("phone", "N/A")), table_cell_style)],
        [Paragraph("Incident Date & Time:", table_cell_bold), Paragraph(str(data.get("datetime", "N/A")), table_cell_style),
         Paragraph("Total Fraud Amount:", table_cell_bold), Paragraph(f"₹{data.get('amount', 0):,.2f}", table_cell_bold)],
        [Paragraph("Debited Bank Name:", table_cell_bold), Paragraph(str(data.get("bank_name", "N/A")), table_cell_style),
         Paragraph("Scam Classification:", table_cell_bold), Paragraph(str(data.get("scam_type", "N/A")), table_cell_style)],
        [Paragraph("12-Digit UTR / RRN:", table_cell_bold), Paragraph(f"<b>{data.get('utr', 'N/A')}</b>", table_cell_style),
         Paragraph("Suspect UPI ID / VPA:", table_cell_bold), Paragraph(f"<b>{data.get('upi_id', 'N/A')}</b>", table_cell_style)],
    ]

    t_summary = Table(summary_data, colWidths=[120, 140, 120, 135])
    t_summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(t_summary)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. SCAM TYPE DETAILS & MODUS OPERANDI", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=6))

    scam_specifics = data.get("scam_specifics", {})
    if scam_specifics:
        specifics_table_data = []
        for k, v in scam_specifics.items():
            label = k.replace("_", " ").title()
            specifics_table_data.append([
                Paragraph(f"<b>{label}</b>", table_cell_style),
                Paragraph(str(v or "Not specified"), table_cell_style),
            ])
        t_specifics = Table(specifics_table_data, colWidths=[160, 355])
        t_specifics.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_specifics)
        elements.append(Spacer(1, 8))

    desc_header = Paragraph("<b>Incident Narrative / Statement of Facts:</b>", table_cell_bold)
    desc_content = Paragraph(str(data.get("description", "No detailed description provided.")), body_style)
    desc_table = Table([[desc_header], [desc_content]], colWidths=[515])
    desc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(desc_table)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3. CHRONOLOGICAL TIMELINE", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=6))

    timeline_data = [
        [Paragraph("Time Point", table_cell_bold), Paragraph("Event / Action Taken", table_cell_bold), Paragraph("Status", table_cell_bold)],
        [
            Paragraph(f"T-0: {data.get('datetime', 'Incident')}", table_cell_style),
            Paragraph(f"Fraudulent debit of ₹{data.get('amount', 0):,.2f} executed via UTR {data.get('utr', '')} to UPI ID {data.get('upi_id', '')}.", table_cell_style),
            Paragraph("<font color='#DC2626'><b>Defrauded</b></font>", table_cell_style),
        ],
        [
            Paragraph("T + Golden Hour", table_cell_style),
            Paragraph("1930 Helpline reported; inter-bank freeze request initiated on CFCFRMS portal.", table_cell_style),
            Paragraph("<font color='#D97706'><b>Logged</b></font>", table_cell_style),
        ],
        [
            Paragraph("T + 12 Hours", table_cell_style),
            Paragraph(f"Bank dispute notice dispatched to {data.get('bank_name', 'Bank')} seeking lien marking under RBI guidelines.", table_cell_style),
            Paragraph("<font color='#2563EB'><b>Notified</b></font>", table_cell_style),
        ],
        [
            Paragraph("Post-Incident", table_cell_style),
            Paragraph(f"Evidence files hashed (SHA-256) and submitted to cybercrime.gov.in.", table_cell_style),
            Paragraph("<font color='#16A34A'><b>Documented</b></font>", table_cell_style),
        ],
    ]
    t_timeline = Table(timeline_data, colWidths=[115, 310, 90])
    t_timeline.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_timeline)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("4. CRYPTOGRAPHIC EVIDENCE INTEGRITY TABLE (SHA-256)", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=6))

    expl_text = (
        "<i>Note: Each digital artifact was hashed using standard SHA-256 algorithm upon intake. "
        "These cryptographic hashes serve as digital tamper-evident seals to prove file contents have not "
        "been altered since the recorded timestamp.</i>"
    )
    elements.append(Paragraph(expl_text, subtitle_style))
    elements.append(Spacer(1, 6))

    if evidence_list:
        ev_table_data = [
            [
                Paragraph("#", table_cell_bold),
                Paragraph("Evidence File Name", table_cell_bold),
                Paragraph("Size", table_cell_bold),
                Paragraph("Intake Timestamp", table_cell_bold),
                Paragraph("SHA-256 Cryptographic Checksum", table_cell_bold),
            ]
        ]
        for idx, ev in enumerate(evidence_list, 1):
            ev_table_data.append([
                Paragraph(str(idx), table_cell_style),
                Paragraph(f"<b>{ev.get('filename', 'file')}</b>", table_cell_style),
                Paragraph(f"{ev.get('size_kb', 0)} KB", table_cell_style),
                Paragraph(str(ev.get("timestamp", "N/A")), table_cell_style),
                Paragraph(str(ev.get("sha256", "N/A")), hash_cell_style),
            ])
        t_evidence = Table(ev_table_data, colWidths=[20, 110, 45, 100, 240])
        t_evidence.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0E7FF")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(t_evidence)
    else:
        no_ev = Paragraph("<i>No screenshot files were uploaded at the time of dossier compilation.</i>", body_style)
        elements.append(no_ev)

    elements.append(Spacer(1, 15))

    elements.append(Paragraph("5. VICTIM VERIFICATION & DECLARATION", h2_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=6))

    declaration_text = (
        "I hereby solemnly state that the facts, UTR number, amounts, and screenshots recorded herein "
        "are true and correct representations of the cyber financial fraud perpetrated against me. "
        "I submit this evidence dossier to aid in immediate police, bank, and regulatory actions."
    )
    elements.append(Paragraph(declaration_text, body_style))
    elements.append(Spacer(1, 20))

    sig_data = [
        [
            Paragraph("<b>Complainant Signature:</b> _______________________", table_cell_style),
            Paragraph("<b>Receiving Officer / Desk:</b> _______________________", table_cell_style),
        ],
        [
            Paragraph(f"Name: {data.get('name', '')}", table_cell_style),
            Paragraph("1930 Ack / Police Diary No: _______________________", table_cell_style),
        ],
        [
            Paragraph(f"Date: {data.get('datetime', '').split('T')[0] if 'T' in str(data.get('datetime', '')) else str(data.get('datetime', ''))}", table_cell_style),
            Paragraph("Seal / Stamp:", table_cell_style),
        ],
    ]
    t_sig = Table(sig_data, colWidths=[255, 260])
    t_sig.setStyle(TableStyle([
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(KeepTogether(t_sig))

    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
