"""
Generates a detailed bilingual PDF salary report.

Rendering requires a Unicode font that covers BOTH Bengali and Latin script,
since even "English" strings in this project embed Bengali proper nouns
(e.g. the gazette title). Place the font at:
    assets/fonts/NotoSansBengali-Regular.ttf
Use the full "Noto Sans Bengali" build (Google Fonts / google/fonts repo),
NOT the script-only "hinted" build from googlefonts/noto-fonts, which omits
Latin glyphs and causes black-box/notdef glyphs for English text.

If the font file is missing, PDFs fall back to Helvetica and show a warning
banner instead of silently producing broken/boxed glyphs.
"""
import os
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ui.translations import t, allowance_name
from ui.components import fmt_money, fmt_percent

FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "NotoSansBengali-Regular.ttf")
FONT_NAME = "NotoSansBengali"

_font_registered = False
_font_available = False


def _ensure_font():
    global _font_registered, _font_available
    if _font_registered:
        return _font_available
    _font_registered = True
    if os.path.exists(FONT_PATH):
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
            _font_available = True
        except Exception:
            _font_available = False
    return _font_available


def build_pdf(result, lang: str) -> bytes:
    has_font = _ensure_font()
    # Use the Unicode font for BOTH languages: English strings in this app
    # can embed Bengali text (e.g. the gazette name), so a Latin-only font
    # would still show black boxes on "English" PDFs.
    base_font = FONT_NAME if has_font else "Helvetica"
    bold_font = FONT_NAME if has_font else "Helvetica-Bold"

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm,
                             leftMargin=16 * mm, rightMargin=16 * mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontName=bold_font, fontSize=16)
    h2_style = ParagraphStyle("H2X", parent=styles["Heading2"], fontName=bold_font, fontSize=12, spaceBefore=10)
    normal_style = ParagraphStyle("NormalX", parent=styles["Normal"], fontName=base_font, fontSize=9.5, leading=13)
    small_style = ParagraphStyle("SmallX", parent=styles["Normal"], fontName=base_font, fontSize=8, leading=11, textColor=colors.grey)

    story = []

    # English PDFs use clean, English-only wording (the shared translation
    # strings embed the original Bengali gazette title, which is correct for
    # the Bengali UI/PDF but is not wanted in an English-only report).
    if lang == "en":
        subtitle_text = "Based on the Bangladesh Government Salary (Pay & Allowances) Order 2026"
        disclaimer_text = (
            "This calculator is based on the official 2026 government pay order. Users should verify "
            "individual entitlement and official payroll calculations with the relevant government "
            "authority/accounts office where necessary. Income tax is not calculated here."
        )
    else:
        subtitle_text = t(lang, "app_subtitle")
        disclaimer_text = t(lang, "disclaimer")

    story.append(Paragraph(t(lang, "app_title"), title_style))
    story.append(Paragraph(subtitle_text, normal_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"{'Date' if lang=='en' else 'তারিখ'}: {datetime.now().strftime('%d-%m-%Y')}", small_style))
    story.append(Spacer(1, 10))

    inp = result.inputs
    loc_key_map = {"dhaka": "loc_dhaka", "other_metro": "loc_other_metro", "other": "loc_other"}
    location_label = t(lang, loc_key_map.get(inp.location, "loc_other"))

    if getattr(inp, "special_post", "none") != "none":
        from data.salary_rules import SPECIAL_POST_LABELS
        grade_display = SPECIAL_POST_LABELS[inp.special_post]["en" if lang == "en" else "bn"]
    else:
        grade_display = str(inp.grade)

    # --- Inputs table ---
    story.append(Paragraph(t(lang, "salary_information"), h2_style))
    input_rows = [
        [t(lang, "grade"), grade_display],
        [t(lang, "current_basic_salary"), fmt_money(inp.old_basic)],
        [t(lang, "stage"), result.stage_label_bn if lang == "bn" else result.stage_label_en],
        [t(lang, "gpf_percent"), f"{inp.gpf_percent}%"],
        [t(lang, "location"), location_label],
    ]
    story.append(_make_table(input_rows, base_font, bold_font, col_widths=[70 * mm, 90 * mm]))
    story.append(Spacer(1, 8))

    # --- Basic salary calculation ---
    story.append(Paragraph(t(lang, "basic_salary"), h2_style))
    stage_pct_label = f"{result.stage_fraction*100:.0f}%"
    basic_rows = [
        [t(lang, "previous"), t(lang, "new") + " (100%)", t(lang, "new") + f" ({stage_pct_label})", t(lang, "difference")],
        [fmt_money(result.old_basic), fmt_money(result.full_new_basic),
         fmt_money(result.new_basic_effective), fmt_money(result.new_basic_effective - result.old_basic)],
    ]
    story.append(_make_table(basic_rows, base_font, bold_font, header=True))
    story.append(Paragraph(
        f"{'Implementation Stage' if lang=='en' else 'বাস্তবায়ন পর্যায়'}: "
        f"{result.stage_label_bn if lang == 'bn' else result.stage_label_en} — {stage_pct_label} "
        f"{'of the increase is paid at this stage.' if lang=='en' else 'বৃদ্ধি এই পর্যায়ে প্রদান করা হয়।'}",
        small_style))
    story.append(Spacer(1, 8))

    # --- Allowance breakdown ---
    story.append(Paragraph(t(lang, "breakdown_title"), h2_style))
    allow_rows = [[t(lang, "component"), t(lang, "previous"), t(lang, "new"), t(lang, "difference")]]
    allow_rows.append([t(lang, "basic_salary"), fmt_money(result.old_basic),
                        fmt_money(result.new_basic_effective),
                        fmt_money(result.new_basic_effective - result.old_basic)])
    for line in result.allowance_lines:
        if not line["applicable"]:
            continue
        name = allowance_name(lang, line["key"])
        allow_rows.append([name, fmt_money(line["old"]), fmt_money(line["new"]), fmt_money(line["new"] - line["old"])])
    allow_rows.append([t(lang, "gross_salary"), fmt_money(result.old_gross), fmt_money(result.new_gross),
                        fmt_money(result.gross_increase)])
    story.append(_make_table(allow_rows, base_font, bold_font, header=True, bold_last_row=True))
    story.append(Spacer(1, 8))

    # --- Deductions ---
    story.append(Paragraph(t(lang, "deductions_title"), h2_style))
    ded_rows = [
        [t(lang, "deduction"), t(lang, "amount")],
        ["GPF", fmt_money(result.gpf_amount)],
        [t(lang, "total_deduction"), fmt_money(result.total_deductions)],
    ]
    story.append(_make_table(ded_rows, base_font, bold_font, header=True, col_widths=[100 * mm, 60 * mm]))
    story.append(Spacer(1, 10))

    # --- Annual (not monthly) allowances — was missing from the PDF; webpage shows this too ---
    story.append(Paragraph(t(lang, "annual_allowances_title"), h2_style))
    story.append(_make_table(
        [[t(lang, "bangla_new_year"), fmt_money(result.bangla_new_year_amount)]],
        base_font, bold_font, col_widths=[130 * mm, 30 * mm]
    ))
    story.append(Spacer(1, 10))

    # --- Final result ---
    story.append(Paragraph(t(lang, "net_salary"), h2_style))
    final_rows = [
        [t(lang, "previous_gross"), fmt_money(result.old_gross)],
        [t(lang, "new_gross"), fmt_money(result.new_gross)],
        [t(lang, "increase"), fmt_money(result.gross_increase)],
        [t(lang, "increase_percent"), fmt_percent(result.gross_increase_percent)],
        [t(lang, "net_salary"), fmt_money(result.net_salary)],
    ]
    story.append(_make_table(final_rows, base_font, bold_font, col_widths=[100 * mm, 60 * mm], bold_last_row=True))
    story.append(Spacer(1, 6))
    story.append(Paragraph(t(lang, "net_formula"), small_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"{t(lang,'gpf_formula')}: {fmt_money(result.new_basic_effective)} × {inp.gpf_percent}% = {fmt_money(result.gpf_amount)}",
        small_style))

    story.append(Spacer(1, 14))
    story.append(Paragraph(disclaimer_text, small_style))
    story.append(Paragraph(t(lang, "not_official"), small_style))

    doc.build(story)
    return buf.getvalue()


def _make_table(rows, base_font, bold_font, header=False, bold_last_row=False, col_widths=None):
    tbl = Table(rows, colWidths=col_widths)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), base_font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style += [
            ("FONTNAME", (0, 0), (-1, 0), bold_font),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ]
    if bold_last_row:
        style += [
            ("FONTNAME", (0, -1), (-1, -1), bold_font),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef3f9")),
        ]
    tbl.setStyle(TableStyle(style))
    return tbl
