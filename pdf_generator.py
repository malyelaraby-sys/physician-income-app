from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import arabic_reshaper
from bidi.algorithm import get_display
import os
import math

# ✅ Arabic font
font_path = os.path.join(os.getcwd(), "fonts", "NotoSansArabic-Regular.ttf")
pdfmetrics.registerFont(TTFont('Arabic', font_path))

# ✅ Styles
normal_style = ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=11)
bold_style = ParagraphStyle(name='Bold', fontName='Helvetica-Bold', fontSize=14)
arabic_style = ParagraphStyle(name='Arabic', fontName='Arabic', fontSize=12)

# ✅ Arabic helper
def arabic(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

# ✅ Maintain image aspect ratio
def get_image(path, max_width, max_height):
    try:
        img = ImageReader(path)
        iw, ih = img.getSize()

        aspect = ih / float(iw)

        # scale width
        if iw > max_width:
            iw = max_width
            ih = iw * aspect

        # scale height if still too big
        if ih > max_height:
            ih = max_height
            iw = ih / aspect

        return Image(path, width=iw, height=ih)

    except:
        return Paragraph("", normal_style)

# ✅ Watermark
def add_watermark(canvas_obj, doc):
    try:
        width, height = A4
        canvas_obj.saveState()

        canvas_obj.setFillAlpha(0.08)

        canvas_obj.drawImage(
            os.path.join("assets", "watermark.png"),
            width - 280,
            40,
            width=240,
            height=240,
            preserveAspectRatio=True,
            mask='auto'
        )

        canvas_obj.restoreState()
    except:
        pass

def generate_pdf(data, filename):

    output_dir = os.path.join(os.getcwd(), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    path = os.path.join(output_dir, filename)
    doc = SimpleDocTemplate(path, pagesize=A4)

    content = []

    # ✅ HEADER (properly scaled logos)
    logo_left = get_image(os.path.join("assets", "logo.png"), 140, 70)
    logo_right = get_image(os.path.join("assets", "accreditation.png"), 120, 70)

    header = Table([[logo_left, "", logo_right]], colWidths=[180, 200, 140])
    content.append(header)
    content.append(Spacer(1, 15))

    # ✅ TITLE
    content.append(Paragraph("PHYSICIAN INCOME STATEMENT", bold_style))
    content.append(Spacer(1, 8))

    month = data.get("month", "")
    year = data.get("year", "")

    content.append(Paragraph(f"Period: {month} {year}", normal_style))
    content.append(Spacer(1, 20))

    # ✅ DOCTOR INFO
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
        if key in ["name", "speciality", "total", "month", "year", "sap"]:
            continue

        if value is None:
            continue

        if isinstance(value, float) and (math.isnan(value) or value == 0):
            continue

        label = label_map.get(key, key.replace("_", " ").title())

        try:
            formatted = f"{float(value):,.2f}"
        except:
            formatted = str(value)

        table_data.append([label, formatted])

    if len(table_data) == 1:
        table_data.append(["No Data", "0.00"])

    table = Table(table_data, colWidths=[260, 140])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    content.append(table)
    content.append(Spacer(1, 25))

    # ✅ TOTAL (highlighted)
    total = data.get("total", 0)

    try:
        total = float(total)
    except:
        total = 0

    total_table = Table(
        [[f"Total Income: {total:,.2f} EGP"]],
        colWidths=[400]
    )

    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    content.append(total_table)
    content.append(Spacer(1, 30))

    # ✅ FOOTER
    footer_text = """
    Main Branch: Cairo | Second Branch: Giza | Hotline: 12345 | www.yourhospital.com
    """

    content.append(Paragraph(footer_text, normal_style))

    # ✅ BUILD
    doc.build(content, onFirstPage=add_watermark, onLaterPages=add_watermark)

    return path