from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# --- 字型設定 ---
FONT_PATH = "assets/NotoSansTC-Regular.ttf"   # 換成 .ttf
FONT_NAME = "NotoSansTC"

try:
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    else:
        # 如果沒找到 ttf，就 fallback 到 ReportLab 內建的中文字型
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        FONT_NAME = "STSong-Light"
except:
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    FONT_NAME = "STSong-Light"


def build_tax_pdf(data: dict, tips: list[str]) -> tuple[bytes, str]:
    """
    生成 PDF 報告（含稅法規則說明）
    """

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleTW", parent=styles["Title"], fontName=FONT_NAME, leading=22))
    styles.add(ParagraphStyle(name="H2TW", parent=styles["Heading2"], fontName=FONT_NAME))
    styles.add(ParagraphStyle(name="BodyTW", parent=styles["BodyText"], fontName=FONT_NAME, leading=16))

    elements = []
    # 🔑 確保標題正確顯示年度
    title = f"個人綜所稅試算及節稅建議報告（{data.get('income_year','-')} 所得，{data.get('filing_year','-')} 申報）"
    elements.append(Paragraph(title, styles["TitleTW"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(datetime.now().strftime("產出時間：%Y-%m-%d %H:%M"), styles["BodyTW"]))
    elements.append(Spacer(1, 12))

    # --- 稅額表格 ---
    table_data = [
        ["項目", "金額 (NT$)"],
        ["綜合所得總額", f"{data['total_income']:,}"],
        ["免稅額", f"{data['exemption']:,}"],
        ["一般扣除（取高）", f"{data['general_deduction']:,}"],
        ["特別扣除", f"{data['special']:,}"],
        ["綜合所得淨額", f"{data['net_income']:,}"],
        ["應納稅額", f"{data['tax_payable']:,}"],
        ["應補稅", f"{data['final_tax']:,}"],
        ["可退稅", f"{data['refund']:,}"],
    ]
    table = Table(table_data, colWidths=[120, 120])
    table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), FONT_NAME),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (1,1), (1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 14))

    # --- 節稅建議 ---
    elements.append(Paragraph("。節稅建議（含潛在節稅效果）", styles["H2TW"]))

    if tips and len(tips) > 0:
        for t in tips:
            clean_tip = str(t).replace("✅", "").replace("⚠️", "").replace("ℹ️", "")
            data_box = [[Paragraph(clean_tip, styles["BodyTW"])]]
            tip_table = Table(data_box, colWidths=[440])
            tip_table.setStyle(TableStyle([
                ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
                ("BACKGROUND", (0,0), (-1,-1), colors.whitesmoke),
                ("LEFTPADDING", (0,0), (-1,-1), 6),
                ("RIGHTPADDING", (0,0), (-1,-1), 6),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ]))
            elements.append(tip_table)
            elements.append(Spacer(1, 6))
    else:
        elements.append(Paragraph("• 沒有額外建議", styles["BodyTW"]))



    # --- 備註 ---
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("※ 本報告僅供試算與學術展示，實際申報以財政部公告規定為準。", styles["BodyTW"]))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    filename = f"tax_report_{data.get('income_year','-')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return pdf_bytes, filename
