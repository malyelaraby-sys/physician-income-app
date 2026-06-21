from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import os
import math

# ✅ USE STATIC FONT (VERY IMPORTANT)
font_path = os.path.join(os.getcwd(), "fonts", "NotoSansArabic-Regular.ttf")
pdfmetrics.registerFont(TTFont('Arabic', font_path))

# ✅ styles
normal_style = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=11)
bold_style = ParagraphStyle(name='Bold', fontName='Helvetica-Bold', fontSize=13)
arabic_style = ParagraphStyle(name='Arabic', fontName='Arabic', fontSize=12)

# ✅ arabic helper
def arabic(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

def generate_pdf(data, filename):

    output_dir = os.path.join(os.getcwd(), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    path = os.path.join(output_dir, filename)
    doc = SimpleDocTemplate(path, pagesize=A4)

    content = []

    # ✅ HEADER
    month = data.get("month", "")
    year = data.get("year", "")

    content.append(Paragraph("PHYSICIAN INCOME STATEMENT", bold_style))
    content.append(Spacer(1, 8))
    content.append(Paragraph(f"Period: {month} {year}", normal_style))
    content.append(Spacer(1, 20))

    # ✅ DOCTOR (FIXED RTL + PREFIX ✅)
    name_ar = arabic(f"د. {data.get('name', '')}")

    content.append(Paragraph("<b>Doctor:</b>", normal_style))
    content.append(Paragraph(name_ar, arabic_style))

    content.append(Spacer(1, 5))
    content.append(Paragraph(f"Specialty: {data.get('speciality', '')}", normal_style))
    content.append(Paragraph(f"SAP: {data.get('sap', '')}", normal_style))
    content.append(Spacer(1, 20))

    # ✅ TABLE
    table_data = [["Item", "Amount (EGP)"]]

    label_map = {
        "fixed": "Fixed Salary",
        "var_surgeon": "Variable Income",
        "bonus_out": "Bonus Out",
        "bonus_in": "Bonus In",
        "night_manager": "Night Manager",
        "seniors": "Senior Coverage"
    }

    for key, value in data.items():

        if key in ["name", "speciality", "total", "minimum_message", "month", "year", "sap", "minimum"]:
            continue

        # ✅ handle NaN safely
        if value is None:
            continue

        if isinstance(value, float) and (math.isnan(value) or value == 0):
            continue

        label = label_map.get(key, key.replace("_", " ").title())

        try:
            value = float(value)
            formatted = f"{value:,.2f}"
        except:
            formatted = str(value)

        table_data.append([label, formatted])

    # ✅ ensure table not empty
    if len(table_data) == 1:
        table_data.append(["No Data", "0.00"])

    content.append(Spacer(1, 10))

    table = Table(table_data, colWidths=[250, 150])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    content.append(table)
    content.append(Spacer(1, 20))

    # ✅ TOTAL
    try:
        total = float(data.get("total", 0))
    except:
        total = 0

    content.append(Paragraph(f"<b>Total Income: {total:,.2f} EGP</b>", normal_style))

    # ✅ FOOTER
    content.append(Spacer(1, 30))
    content.append(Paragraph("Thank you for your contribution", normal_style))
    content.append(Paragraph("Hospital Management", normal_style))

    doc.build(content)

    print("✅ Saved:", path)  # debug confirmation

    return path
