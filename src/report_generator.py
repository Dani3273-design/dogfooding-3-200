# -*- coding: utf-8 -*-
"""
报告生成模块
使用plotly生成图表并输出PDF报告
"""

import os
from typing import Dict, Any, List
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


# 颜色配置
COLORS = [
    "#FF6B6B",  # 红色
    "#4ECDC4",  # 青色
    "#45B7D1",  # 蓝色
    "#96CEB4",  # 绿色
    "#FFEAA7",  # 黄色
    "#DDA0DD",  # 紫色
    "#98D8C8",  # 薄荷绿
    "#F7DC6F",  # 金色
]


def create_rating_probability_chart(data: Dict[str, Any]) -> go.Figure:
    """
    创建评分/不评分概率饼状图
    
    参数:
        data: 包含评分概率数据的字典
    
    返回:
        plotly Figure对象
    """
    labels = ["已评分", "未评分"]
    values = [data["rated_count"], data["unrated_count"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.35,
        marker_colors=[COLORS[2], COLORS[0]],
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(size=16, family="SimHei"),
        pull=[0.02, 0.02],
        insidetextorientation="radial",
        outsidetextfont=dict(size=14, family="SimHei"),
    )])
    
    fig.update_layout(
        title=dict(
            text="用户评分参与率",
            font=dict(size=20, family="SimHei"),
            x=0.5,
            y=0.95,
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=14, family="SimHei"),
            x=0.85,
            y=0.5,
            xanchor="left",
        ),
        paper_bgcolor="white",
        width=700,
        height=500,
        margin=dict(l=80, r=80, t=80, b=80),
    )
    
    return fig


def create_comment_length_charts(data: Dict[int, Dict[str, Any]]) -> List[go.Figure]:
    """
    为每个评分等级创建评论长度分布饼状图
    图表和文字放大1.5倍，且显示所有分类（包括0值）
    
    参数:
        data: 按评分等级分组的评论长度分布数据
    
    返回:
        plotly Figure对象列表
    """
    figures = []
    
    # 固定的标签顺序
    fixed_labels = ["0-10字", "10-30字", "30字以上"]
    
    for rating in range(1, 6):
        rating_data = data[rating]
        counts = rating_data["counts"]
        
        # 按固定顺序获取值，确保所有分类都显示
        values = [counts.get(label, 0) for label in fixed_labels]
        
        # 计算总数用于显示百分比
        total = sum(values)
        
        # 如果所有值都为0，显示占位数据
        if total == 0:
            values = [1, 0, 0]
            total = 1
        
        fig = go.Figure(data=[go.Pie(
            labels=fixed_labels,
            values=values,
            hole=0.35,
            marker_colors=COLORS[:3],
            textinfo="label+percent",
            textposition="outside",
            textfont=dict(size=18, family="SimHei"),
            pull=[0.02, 0.02, 0.02],
            insidetextorientation="radial",
            outsidetextfont=dict(size=16, family="SimHei"),
        )])
        
        fig.update_layout(
            title=dict(
                text=f"{rating}分评论 - 评论长度分布 (共{rating_data['total']}条)",
                font=dict(size=22, family="SimHei"),
                x=0.5,
                y=0.95,
            ),
            showlegend=True,
            legend=dict(
                font=dict(size=16, family="SimHei"),
                x=0.78,
                y=0.5,
                xanchor="left",
            ),
            paper_bgcolor="white",
            width=600,
            height=450,
            margin=dict(l=60, r=60, t=80, b=60),
        )
        
        figures.append(fig)
    
    return figures


def create_product_rating_chart(data: Dict[str, Any]) -> go.Figure:
    """
    创建产品平均评分饼状图
    
    参数:
        data: 包含产品评分数据的字典
    
    返回:
        plotly Figure对象
    """
    labels = []
    values = []
    
    for p in data["top_products"]:
        labels.append(f"{p['product_name']}")
        values.append(p["avg_rating"])
    
    if data["other_products"]:
        other = data["other_products"]
        labels.append("其他产品")
        values.append(other["avg_rating"])
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.35,
        marker_colors=COLORS[:len(labels)],
        textinfo="label+value",
        textposition="outside",
        textfont=dict(size=14, family="SimHei"),
        pull=[0.02] * len(labels),
        insidetextorientation="radial",
        outsidetextfont=dict(size=13, family="SimHei"),
    )])
    
    # 调整布局，将图例放在右侧，避免与饼图文字重叠
    fig.update_layout(
        title=dict(
            text="产品平均评分分布（前4名及其他）",
            font=dict(size=20, family="SimHei"),
            x=0.5,
            y=0.95,
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=13, family="SimHei"),
            x=1.05,  # 将图例移到图表右侧外部
            y=0.5,
            xanchor="left",
        ),
        paper_bgcolor="white",
        width=850,  # 增加宽度以容纳右侧图例
        height=550,
        margin=dict(l=60, r=120, t=80, b=60),  # 增加右边距
    )
    
    return fig


def save_chart_as_image(fig: go.Figure, output_path: str) -> str:
    """
    将图表保存为图片文件
    
    参数:
        fig: plotly Figure对象
        output_path: 输出文件路径
    
    返回:
        保存的文件路径
    """
    pio.write_image(fig, output_path, scale=2)
    return output_path


def generate_pdf_report(
    analysis_result: Dict[str, Any],
    year: int,
    month: int,
    output_dir: str = "report"
) -> str:
    """
    生成PDF报告
    
    参数:
        analysis_result: 数据分析结果
        year: 年份
        month: 月份
        output_dir: 输出目录
    
    返回:
        生成的PDF文件路径
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.colors import HexColor
    
    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 图片临时目录
    temp_img_dir = output_path / "temp_images"
    temp_img_dir.mkdir(parents=True, exist_ok=True)
    
    # 注册中文字体
    font_paths = [
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
    ]
    
    font_name = "ChineseFont"
    font_registered = False
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                font_registered = True
                print(f"Font registered: {font_path}")
                break
            except Exception as e:
                print(f"Failed to register font {font_path}: {e}")
                continue
    
    if not font_registered:
        print("Warning: No Chinese font found, using default font")
        font_name = "Helvetica"
    
    # PDF文件路径
    pdf_path = output_path / f"product_rating_report_{year}{month:02d}.pdf"
    
    # 创建PDF
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    # 设置标题
    c.setFont(font_name, 24)
    c.drawCentredString(width / 2, height - 2 * cm, "产品评分分析报告")
    
    c.setFont(font_name, 14)
    c.drawCentredString(width / 2, height - 3.5 * cm, f"报告期间：{year}年{month}月")
    
    # 添加分隔线
    c.setStrokeColor(HexColor("#45B7D1"))
    c.setLineWidth(2)
    c.line(2 * cm, height - 4.2 * cm, width - 2 * cm, height - 4.2 * cm)
    
    # 第一部分：评分参与率
    c.setFont(font_name, 16)
    c.drawString(2 * cm, height - 5.5 * cm, "一、用户评分参与率分析")
    
    # 生成评分概率图
    rating_prob_fig = create_rating_probability_chart(
        analysis_result["rating_probability"]
    )
    rating_prob_img = temp_img_dir / "rating_probability.png"
    save_chart_as_image(rating_prob_fig, str(rating_prob_img))
    
    # 插入图片 - 保持原始宽高比 (700x500)
    img_width = 14 * cm
    img_height = 10 * cm
    c.drawImage(
        str(rating_prob_img), 
        (width - img_width) / 2,  # 居中
        height - 6 * cm - img_height, 
        width=img_width, 
        height=img_height,
        preserveAspectRatio=True,
        mask="auto"
    )
    
    # 添加说明文字
    c.setFont(font_name, 11)
    prob_data = analysis_result["rating_probability"]
    text_y = height - 17 * cm
    c.drawString(2 * cm, text_y, f"总记录数：{prob_data['total']}条")
    c.drawString(2 * cm, text_y - 0.7 * cm, f"已评分：{prob_data['rated_count']}条 ({prob_data['rated_ratio']:.1%})")
    c.drawString(2 * cm, text_y - 1.4 * cm, f"未评分：{prob_data['unrated_count']}条 ({prob_data['unrated_ratio']:.1%})")
    
    # 第二部分：评论长度分布
    c.showPage()
    c.setFont(font_name, 16)
    c.drawString(2 * cm, height - 2 * cm, "二、评论意愿分析（按评分等级）")
    
    # 生成评论长度分布图
    comment_figs = create_comment_length_charts(
        analysis_result["comment_length_distribution"]
    )
    
    # 每页放3个图表，布局：上方2个，下方1个居中
    # 图表原始尺寸 600x450
    img_width = 8 * cm
    img_height = 6 * cm
    
    for i, fig in enumerate(comment_figs):
        # 每3个图表换一页
        if i > 0 and i % 3 == 0:
            c.showPage()
            c.setFont(font_name, 16)
            c.drawString(2 * cm, height - 2 * cm, "二、评论意愿分析（续）")
        
        # 计算位置：每页3个图表
        # 第一行：图表1（左）、图表2（右）
        # 第二行：图表3（居中）
        pos_in_page = i % 3
        
        if pos_in_page == 0:
            # 第一个图表：左上
            x_pos = 1.5 * cm
            y_pos = height - 4 * cm - img_height
        elif pos_in_page == 1:
            # 第二个图表：右上
            x_pos = width - img_width - 1.5 * cm
            y_pos = height - 4 * cm - img_height
        else:
            # 第三个图表：下方居中
            x_pos = (width - img_width) / 2
            y_pos = height - 4 * cm - img_height - 7 * cm
        
        img_path = temp_img_dir / f"comment_length_{i + 1}.png"
        save_chart_as_image(fig, str(img_path))
        
        c.drawImage(
            str(img_path), 
            x_pos, 
            y_pos, 
            width=img_width, 
            height=img_height,
            preserveAspectRatio=True,
            mask="auto"
        )
    
    # 第三部分：产品平均评分
    c.showPage()
    c.setFont(font_name, 16)
    c.drawString(2 * cm, height - 2 * cm, "三、产品平均评分分析")
    
    # 生成产品评分图
    product_fig = create_product_rating_chart(
        analysis_result["product_ratings"]
    )
    product_img = temp_img_dir / "product_rating.png"
    save_chart_as_image(product_fig, str(product_img))
    
    # 插入图片 - 保持原始宽高比 (850x550)
    img_width = 16 * cm
    img_height = 10.5 * cm
    c.drawImage(
        str(product_img), 
        (width - img_width) / 2, 
        height - 4 * cm - img_height, 
        width=img_width, 
        height=img_height,
        preserveAspectRatio=True,
        mask="auto"
    )
    
    # 添加产品详情表格
    c.setFont(font_name, 12)
    table_y = height - 16 * cm
    
    c.drawString(2 * cm, table_y, "产品评分详情：")
    
    c.setFont(font_name, 11)
    table_y -= 1 * cm
    
    # 表头
    c.drawString(2 * cm, table_y, "产品名称")
    c.drawString(6 * cm, table_y, "平均评分")
    c.drawString(9 * cm, table_y, "评分数量")
    
    table_y -= 0.6 * cm
    c.line(2 * cm, table_y, 12 * cm, table_y)
    table_y -= 0.6 * cm
    
    # 表格内容
    for p in analysis_result["product_ratings"]["top_products"]:
        c.drawString(2 * cm, table_y, p["product_name"])
        c.drawString(6 * cm, table_y, f"{p['avg_rating']:.2f}")
        c.drawString(9 * cm, table_y, str(p["rating_count"]))
        table_y -= 0.6 * cm
    
    if analysis_result["product_ratings"]["other_products"]:
        other = analysis_result["product_ratings"]["other_products"]
        c.drawString(2 * cm, table_y, "其他产品")
        c.drawString(6 * cm, table_y, f"{other['avg_rating']:.2f}")
        c.drawString(9 * cm, table_y, str(other["rating_count"]))
    
    # 添加报告尾部
    c.setFont(font_name, 10)
    c.drawCentredString(width / 2, 2 * cm, "--- 报告结束 ---")
    
    # 保存PDF
    c.save()
    
    # 清理临时图片
    for img_file in temp_img_dir.glob("*.png"):
        img_file.unlink()
    temp_img_dir.rmdir()
    
    print(f"PDF report saved to: {pdf_path}")
    
    return str(pdf_path)
