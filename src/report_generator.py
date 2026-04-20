"""
报告生成模块
负责生成图表并输出PDF报告
"""

import os
from datetime import datetime

import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak


def register_chinese_font():
    """
    注册中文字体，解决PDF中文显示问题
    尝试多个常见中文字体
    """
    # 常见中文字体路径列表
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
        "/System/Library/Fonts/STHeiti Light.ttc",  # macOS 黑体
        "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS 冬青黑体
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux 文泉驿正黑
        "C:/Windows/Fonts/simhei.ttf",  # Windows 黑体
        "C:/Windows/Fonts/simsun.ttc",  # Windows 宋体
        "C:/Windows/Fonts/msyh.ttc",  # Windows 微软雅黑
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                print(f"Chinese font registered: {font_path}")
                return "ChineseFont"
            except Exception as e:
                print(f"Failed to register font {font_path}: {e}")
                continue
    
    # 如果都失败了，使用默认字体
    print("Warning: No Chinese font found, using default Helvetica")
    return "Helvetica"


def create_rating_distribution_pie(rating_dist):
    """
    创建评分/不评分分布饼状图
    
    Args:
        rating_dist: 评分分布字典
    
    Returns:
        plotly.Figure: 饼状图
    """
    labels = ["已评分", "未评分"]
    values = [rating_dist["rated"], rating_dist["unrated"]]
    colors_list = ["#4CAF50", "#FFC107"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors_list,
        textinfo="label+percent",
        textfont_size=14,
        insidetextorientation="radial",
    )])
    
    fig.update_layout(
        title=dict(
            text="用户评分意愿分布",
            font=dict(size=18),
            x=0.5,
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
        ),
        width=600,
        height=500,
        margin=dict(t=80, b=80, l=50, r=50),
    )
    
    return fig


def create_comment_length_pie(comment_length_dist):
    """
    创建各评分等级的评论长度分布饼状图
    每个评分单独一个饼状图，使用子图布局
    
    Args:
        comment_length_dist: 评论长度分布字典
    
    Returns:
        plotly.Figure: 包含多个子图的饼状图
    """
    # 创建2x3的子图布局
    fig = make_subplots(
        rows=2,
        cols=3,
        specs=[[{"type": "domain"}, {"type": "domain"}, {"type": "domain"}],
               [{"type": "domain"}, {"type": "domain"}, {"type": "domain"}]],
        subplot_titles=[f"评分 {i}" for i in range(1, 6)] + [""],
    )
    
    labels = ["0-10字", "10-30字", "30字以上"]
    colors_list = ["#FF6B6B", "#4ECDC4", "#45B7D1"]
    
    positions = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2)]
    
    for idx, (rating, pos) in enumerate(zip(range(1, 6), positions)):
        dist = comment_length_dist[rating]
        values = [dist["short"], dist["medium"], dist["long"]]
        
        # 如果该评分没有数据，显示空
        if sum(values) == 0:
            values = [1, 0, 0]
            labels_empty = ["无数据", "", ""]
        else:
            labels_empty = labels
        
        fig.add_trace(
            go.Pie(
                labels=labels_empty,
                values=values,
                name=f"评分 {rating}",
                marker_colors=colors_list,
                textinfo="label+percent" if sum(values) > 0 else "text",
                text=[f"{v}" for v in values] if sum(values) > 0 else ["无数据", "", ""],
                hole=0.3,
                showlegend=(idx == 0),  # 只在第一个图显示图例
            ),
            row=pos[0],
            col=pos[1],
        )
    
    fig.update_layout(
        title=dict(
            text="各评分等级的评论长度分布",
            font=dict(size=18),
            x=0.5,
        ),
        width=900,
        height=700,
        margin=dict(t=100, b=50, l=50, r=50),
    )
    
    # 更新子图标题样式
    for annotation in fig["layout"]["annotations"]:
        annotation["font"] = dict(size=14)
    
    return fig


def create_product_rating_pie(top_products, other_stats):
    """
    创建产品平均评分饼状图
    显示前4产品和"其他产品"
    
    Args:
        top_products: 前N产品DataFrame
        other_stats: 其他产品统计
    
    Returns:
        plotly.Figure: 饼状图
    """
    labels = []
    values = []
    
    # 添加前4产品
    for row in top_products.iter_rows(named=True):
        labels.append(f"{row['product_name']}\n(avg: {row['avg_rating']:.2f})")
        values.append(row["avg_rating"])
    
    # 添加其他产品
    if other_stats["rating_count"] > 0:
        labels.append(f"其他产品\n(avg: {other_stats['avg_rating']:.2f})")
        values.append(other_stats["avg_rating"])
    
    colors_list = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors_list[:len(labels)],
        textinfo="label+percent",
        textfont_size=12,
        insidetextorientation="radial",
    )])
    
    fig.update_layout(
        title=dict(
            text="产品平均评分分布（前4产品+其他）",
            font=dict(size=18),
            x=0.5,
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
        ),
        width=700,
        height=600,
        margin=dict(t=80, b=100, l=50, r=50),
    )
    
    return fig


def save_chart_as_image(fig, filepath):
    """
    将plotly图表保存为图片
    
    Args:
        fig: plotly图表对象
        filepath: 保存路径
    """
    pio.write_image(fig, filepath, scale=2)
    print(f"Chart saved: {filepath}")


def generate_pdf_report(analysis_result, output_path):
    """
    生成PDF报告
    
    Args:
        analysis_result: 分析结果字典
        output_path: PDF输出路径
    """
    print("Generating PDF report...")
    
    # 注册中文字体
    chinese_font = register_chinese_font()
    
    # 创建PDF文档
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )
    
    # 创建样式
    styles = getSampleStyleSheet()
    
    # 自定义中文样式
    title_style = ParagraphStyle(
        "ChineseTitle",
        parent=styles["Heading1"],
        fontName=chinese_font,
        fontSize=24,
        alignment=1,  # 居中
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        "ChineseHeading",
        parent=styles["Heading2"],
        fontName=chinese_font,
        fontSize=16,
        spaceAfter=12,
        spaceBefore=12,
    )
    
    body_style = ParagraphStyle(
        "ChineseBody",
        parent=styles["BodyText"],
        fontName=chinese_font,
        fontSize=11,
        leading=16,
    )
    
    # 构建PDF内容
    story = []
    
    # 报告标题
    year = analysis_result["year"]
    month = analysis_result["month"]
    story.append(Paragraph(f"产品评分分析报告", title_style))
    story.append(Paragraph(f"统计周期：{year}年{month}月", body_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # 数据概览
    story.append(Paragraph("一、数据概览", heading_style))
    total = analysis_result["rating_distribution"]["total"]
    rated = analysis_result["rating_distribution"]["rated"]
    unrated = analysis_result["rating_distribution"]["unrated"]
    
    overview_data = [
        ["指标", "数值"],
        ["总记录数", str(total)],
        ["已评分记录", str(rated)],
        ["未评分记录", str(unrated)],
        ["评分率", f"{rated/total*100:.1f}%"],
    ]
    
    overview_table = Table(overview_data, colWidths=[2.5 * inch, 2 * inch])
    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), chinese_font),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("FONTNAME", (0, 1), (-1, -1), chinese_font),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # 评分意愿分布图
    story.append(Paragraph("二、用户评分意愿分布", heading_style))
    story.append(Paragraph("下图展示了用户选择评分与未评分的比例分布：", body_style))
    story.append(Spacer(1, 0.1 * inch))
    
    # 生成并添加图表
    rating_pie = create_rating_distribution_pie(analysis_result["rating_distribution"])
    rating_chart_path = "/tmp/rating_distribution.png"
    save_chart_as_image(rating_pie, rating_chart_path)
    story.append(Image(rating_chart_path, width=5 * inch, height=4.2 * inch))
    story.append(Spacer(1, 0.2 * inch))
    
    # 评论长度分布
    story.append(PageBreak())
    story.append(Paragraph("三、各评分等级评论长度分析", heading_style))
    story.append(Paragraph("以下图表展示了不同评分等级（1-5分）对应的评论长度分布情况：", body_style))
    story.append(Spacer(1, 0.1 * inch))
    
    comment_pie = create_comment_length_pie(analysis_result["comment_length_distribution"])
    comment_chart_path = "/tmp/comment_length_distribution.png"
    save_chart_as_image(comment_pie, comment_chart_path)
    story.append(Image(comment_chart_path, width=6.5 * inch, height=5 * inch))
    
    # 添加说明
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("说明：", heading_style))
    story.append(Paragraph("• 0-10字：简短评论，通常为简单评价", body_style))
    story.append(Paragraph("• 10-30字：中等长度评论，包含一定细节", body_style))
    story.append(Paragraph("• 30字以上：详细评论，包含较多使用体验描述", body_style))
    
    # 产品平均评分
    story.append(PageBreak())
    story.append(Paragraph("四、产品平均评分排名", heading_style))
    story.append(Paragraph("下图展示了评分前4的产品及其平均评分，其他产品合并统计：", body_style))
    story.append(Spacer(1, 0.1 * inch))
    
    product_pie = create_product_rating_pie(
        analysis_result["top_products"],
        analysis_result["other_stats"]
    )
    product_chart_path = "/tmp/product_rating_distribution.png"
    save_chart_as_image(product_pie, product_chart_path)
    story.append(Image(product_chart_path, width=5.5 * inch, height=4.7 * inch))
    
    # 产品详细数据表
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("产品评分详细数据：", heading_style))
    
    table_data = [["产品名称", "平均评分", "评分数量"]]
    for row in analysis_result["top_products"].iter_rows(named=True):
        table_data.append([
            row["product_name"],
            f"{row['avg_rating']:.2f}",
            str(row["rating_count"]),
        ])
    
    # 添加其他产品行
    other = analysis_result["other_stats"]
    if other["rating_count"] > 0:
        table_data.append([
            "其他产品",
            f"{other['avg_rating']:.2f}",
            str(other["rating_count"]),
        ])
    
    product_table = Table(table_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
    product_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), chinese_font),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("FONTNAME", (0, 1), (-1, -1), chinese_font),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(product_table)
    
    # 报告结尾
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("— 报告结束 —", ParagraphStyle(
        "End",
        parent=body_style,
        alignment=1,
        fontName=chinese_font,
    )))
    
    # 生成PDF
    doc.build(story)
    print(f"PDF report generated: {output_path}")
    
    # 清理临时文件
    for temp_file in [rating_chart_path, comment_chart_path, product_chart_path]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"Cleaned up: {temp_file}")


def generate_report(analysis_result, output_path):
    """
    报告生成主函数
    
    Args:
        analysis_result: 分析结果字典
        output_path: PDF输出路径
    """
    print("Starting report generation...")
    generate_pdf_report(analysis_result, output_path)
    print("Report generation completed")
