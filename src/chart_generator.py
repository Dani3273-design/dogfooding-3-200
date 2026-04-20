import plotly.graph_objects as go
import plotly.io as pio


def create_rating_pie_chart(rating_data, output_path):
    """
    创建评分/不评分概率饼状图
    :param rating_data: 评分统计数据
    :param output_path: 输出图片路径
    """
    print(f"Creating rating pie chart: {output_path}")
    
    colors = ['#2ECC71', '#E74C3C']
    
    fig = go.Figure(data=[go.Pie(
        labels=rating_data["labels"],
        values=rating_data["values"],
        textinfo='label+percent',
        marker=dict(colors=colors),
        hole=0.3
    )])
    
    fig.update_layout(
        title={
            'text': "用户评分分布",
            'font': {'size': 20, 'family': 'SimHei'},
            'x': 0.5
        },
        font={'family': 'SimHei', 'size': 14},
        width=600,
        height=500
    )
    
    pio.write_image(fig, output_path, scale=2)


def create_review_length_pie_charts(review_length_data, output_dir):
    """
    按评分创建评论文本长度分布饼状图
    :param review_length_data: 各评分的评论长度数据
    :param output_dir: 输出目录
    :return: 生成的图片路径列表
    """
    print("Creating review length pie charts")
    colors = ['#3498DB', '#F39C12', '#9B59B6']
    image_paths = []
    
    for rating, data in review_length_data.items():
        fig = go.Figure(data=[go.Pie(
            labels=data["labels"],
            values=data["values"],
            textinfo='label+percent',
            marker=dict(colors=colors),
            hole=0.3
        )])
        
        fig.update_layout(
            title={
                'text': f"{rating}星评分 - 评论文本长度分布",
                'font': {'size': 20, 'family': 'SimHei'},
                'x': 0.5
            },
            font={'family': 'SimHei', 'size': 14},
            width=600,
            height=500
        )
        
        output_path = f"{output_dir}/review_length_rating_{rating}.png"
        pio.write_image(fig, output_path, scale=2)
        image_paths.append(output_path)
    
    return image_paths


def create_product_rating_pie_chart(product_rating_data, output_path):
    """
    创建产品平均评分饼状图
    :param product_rating_data: 产品评分数据
    :param output_path: 输出图片路径
    """
    print(f"Creating product rating pie chart: {output_path}")
    
    colors = ['#E74C3C', '#F39C12', '#F1C40F', '#2ECC71', '#95A5A6']
    
    fig = go.Figure(data=[go.Pie(
        labels=product_rating_data["labels"],
        values=product_rating_data["values"],
        textinfo='label+value',
        texttemplate='%{label}: %{value:.2f}分',
        marker=dict(colors=colors[:len(product_rating_data["labels"])]),
        hole=0.3
    )])
    
    fig.update_layout(
        title={
            'text': "产品平均评分排行（Top4 + 其他）",
            'font': {'size': 20, 'family': 'SimHei'},
            'x': 0.5
        },
        font={'family': 'SimHei', 'size': 14},
        width=700,
        height=500
    )
    
    pio.write_image(fig, output_path, scale=2)


def create_all_charts(rating_prob_data, review_length_data, product_rating_data, output_dir):
    """
    创建所有图表
    :param rating_prob_data: 评分概率数据
    :param review_length_data: 评论长度分布数据
    :param product_rating_data: 产品评分数据
    :param output_dir: 输出目录
    :return: 所有图表路径列表
    """
    print("Generating all charts...")
    
    chart_paths = []
    
    rating_pie_path = f"{output_dir}/rating_probability.png"
    create_rating_pie_chart(rating_prob_data, rating_pie_path)
    chart_paths.append(rating_pie_path)
    
    review_length_paths = create_review_length_pie_charts(review_length_data, output_dir)
    chart_paths.extend(review_length_paths)
    
    product_rating_path = f"{output_dir}/product_avg_rating.png"
    create_product_rating_pie_chart(product_rating_data, product_rating_path)
    chart_paths.append(product_rating_path)
    
    return chart_paths
