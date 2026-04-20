from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import os


def register_chinese_font():
    """
    注册中文字体，解决PDF中文乱码问题
    """
    font_path = "/System/Library/Fonts/PingFang.ttc"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('PingFang', font_path))
            return "PingFang"
        except:
            pass
    
    font_path = "/System/Library/Fonts/STHeiti Light.ttc"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('STHeiti', font_path))
            return "STHeiti"
        except:
            pass
    
    return "Helvetica"


def create_pdf_report(output_path, data_summary, chart_paths, product_rating_data):
    """
    生成中文PDF报告
    :param output_path: 输出PDF路径
    :param data_summary: 数据摘要
    :param chart_paths: 图表文件路径列表
    :param product_rating_data: 产品评分数据
    """
    print(f"Generating PDF report: {output_path}")
    
    font_name = register_chinese_font()
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName=font_name,
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        spaceAfter=15,
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        spaceAfter=10
    )
    
    story = []
    
    story.append(Paragraph("产品评分分析报告", title_style))
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("一、数据概览", heading_style))
    
    summary_data = [
        ["指标", "数值"],
        ["总记录数", str(data_summary["total_records"])],
        ["有效评分数", str(data_summary["rated_records"])],
        ["平均评分", f"{data_summary['avg_rating']:.2f}"],
        ["产品总数", str(data_summary["unique_products"])]
    ]
    
    summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("二、用户评分分布", heading_style))
    story.append(Paragraph("下图展示了用户评分与未评分的比例分布：", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    rating_chart = Image(chart_paths[0], width=14*cm, height=11.5*cm)
    story.append(rating_chart)
    story.append(PageBreak())
    
    story.append(Paragraph("三、评论长度意愿分析", heading_style))
    story.append(Paragraph("按不同评分级别分析用户撰写评论文本的长度分布（仅统计已评分数据）：", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    for i in range(1, 6):
        chart_path = f"report/temp_charts/review_length_rating_{i}.png"
        if os.path.exists(chart_path) and chart_path in chart_paths:
            story.append(Spacer(1, 0.3*cm))
            img = Image(chart_path, width=12*cm, height=10*cm)
            story.append(img)
    
    story.append(PageBreak())
    
    story.append(Paragraph("四、产品平均评分排行", heading_style))
    story.append(Paragraph("评分最高的前4款产品与平均评分，其余产品合并统计：", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    product_chart_path = "report/temp_charts/product_avg_rating.png"
    if os.path.exists(product_chart_path):
        product_chart = Image(product_chart_path, width=15*cm, height=11*cm)
        story.append(product_chart)
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Top 4 产品详细信息：", normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    top_products = product_rating_data["top_products"]
    product_table_data = [["排名", "产品名称", "平均评分", "评价人数"]]
    
    for idx, product in enumerate(top_products, 1):
        product_table_data.append([
            str(idx),
            product["product_name"],
            f"{product['avg_rating']:.2f}",
            str(product["rating_count"])
        ])
    
    product_table = Table(product_table_data, colWidths=[2*cm, 6*cm, 3*cm, 3*cm])
    product_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(product_table)
    
    doc.build(story)
    print(f"PDF report generated successfully: {output_path}")
