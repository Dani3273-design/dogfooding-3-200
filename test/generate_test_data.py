"""
测试数据生成模块
用于生成产品评分分析程序所需的测试数据
"""

import random
import polars as pl
from datetime import datetime


# 产品列表定义
PRODUCTS = [
    {"id": "P001", "name": "智能手机X1"},
    {"id": "P002", "name": "无线耳机Pro"},
    {"id": "P003", "name": "平板电脑Air"},
    {"id": "P004", "name": "智能手表S3"},
    {"id": "P005", "name": "蓝牙音箱Mini"},
    {"id": "P006", "name": "移动电源20000"},
    {"id": "P007", "name": "机械键盘RGB"},
    {"id": "P008", "name": "游戏鼠标G1"},
    {"id": "P009", "name": "显示器27寸"},
    {"id": "P010", "name": "路由器AX6"},
]

# 评论文本模板库
COMMENT_TEMPLATES = {
    "short": [  # 0-10字
        "很好用",
        "不错",
        "满意",
        "一般般",
        "不推荐",
        "质量很好",
        "性价比高",
        "物流快",
        "包装好",
        "喜欢",
    ],
    "medium": [  # 10-30字
        "产品质量很好，使用体验不错，推荐购买",
        "性价比很高，物流速度很快，包装也很完整",
        "外观设计精美，功能齐全，值得购买",
        "使用了一段时间，感觉还不错，会继续关注",
        "价格便宜，质量也还可以，总体满意",
        "功能强大，操作简单，老人也能用",
        "做工精细，材质优良，非常耐用",
    ],
    "long": [  # 30字以上
        "这款产品真的超出我的预期，无论是外观设计还是功能体验都非常出色，强烈推荐给大家！",
        "买给家人的礼物，收到后非常满意。包装精美，产品质量也很好，物流速度也很快。",
        "用了快一个月了，整体感觉很不错。功能齐全，操作简单，性价比也很高，值得购买。",
        "对比了很多家最后选择了这款，果然没有让我失望。质量过硬，售后服务也很好。",
        "第一次购买这个品牌的产品，体验非常好。做工精细，用料扎实，下次还会回购。",
    ],
}


def generate_random_date():
    """
    生成随机日期（月份、年份随机）
    
    Returns:
        tuple: (year, month)
    """
    year = random.randint(2022, 2024)
    month = random.randint(1, 12)
    return year, month


def generate_random_rating(product_id):
    """
    生成随机评分，根据产品不同有不同的评分分布
    确保不存在全5分或全0分的产品
    
    Args:
        product_id: 产品ID
    
    Returns:
        int: 评分（0表示未评分，1-5表示实际评分）
    """
    # 用户评分概率（70%的概率会评分）
    if random.random() > 0.7:
        return 0
    
    # 根据产品ID设置不同的评分分布，确保符合基本规律
    # 不同产品有不同的评分倾向，但都在1-5之间分布
    product_bias = {
        "P001": [0.05, 0.1, 0.2, 0.35, 0.3],   # 较好产品
        "P002": [0.1, 0.15, 0.25, 0.3, 0.2],   # 一般产品
        "P003": [0.08, 0.12, 0.2, 0.3, 0.3],   # 较好产品
        "P004": [0.15, 0.2, 0.25, 0.25, 0.15], # 一般产品
        "P005": [0.1, 0.2, 0.3, 0.25, 0.15],   # 一般产品
        "P006": [0.12, 0.18, 0.25, 0.28, 0.17],# 一般产品
        "P007": [0.05, 0.1, 0.2, 0.35, 0.3],   # 较好产品
        "P008": [0.08, 0.15, 0.25, 0.27, 0.25],# 较好产品
        "P009": [0.1, 0.2, 0.3, 0.25, 0.15],   # 一般产品
        "P010": [0.12, 0.22, 0.28, 0.23, 0.15],# 一般产品
    }
    
    weights = product_bias.get(product_id, [0.1, 0.15, 0.25, 0.3, 0.2])
    return random.choices([1, 2, 3, 4, 5], weights=weights)[0]


def generate_random_comment(rating):
    """
    根据评分生成随机评论
    
    Args:
        rating: 评分（1-5）
    
    Returns:
        str: 评论文本
    """
    if rating == 0:
        return ""
    
    # 根据评分决定评论长度分布
    # 高分更容易写长评论，低分可能写短评论
    if rating >= 4:
        length_weights = [0.2, 0.4, 0.4]  # 短、中、长
    elif rating >= 3:
        length_weights = [0.3, 0.5, 0.2]
    else:
        length_weights = [0.5, 0.4, 0.1]
    
    length_type = random.choices(["short", "medium", "long"], weights=length_weights)[0]
    
    # 根据评分选择正面或负面评论
    if rating >= 4:
        # 正面评论
        return random.choice(COMMENT_TEMPLATES[length_type])
    elif rating == 3:
        # 中性评论，随机选择
        return random.choice(COMMENT_TEMPLATES[length_type])
    else:
        # 负面评论，修改模板
        negative_comments = {
            "short": ["不好用", "失望", "质量差", "不值", "有问题", "不推荐"],
            "medium": ["质量一般，不太满意，考虑退货", "性价比不高，使用体验一般", "外观还可以，但功能不太行"],
            "long": ["这款产品让我有点失望，质量没有想象中好，可能不会再购买了。", "使用体验不太好，有一些小问题，客服处理也不够及时。"],
        }
        return random.choice(negative_comments.get(length_type, ["一般"]))


def generate_test_data(record_count=600):
    """
    生成测试数据
    
    Args:
        record_count: 记录数量，默认600条
    
    Returns:
        pl.DataFrame: 包含所有测试数据的DataFrame
    """
    print(f"Generating {record_count} test records...")
    
    year, month = generate_random_date()
    print(f"Data period: {year}-{month:02d}")
    
    records = []
    
    for i in range(record_count):
        # 随机选择产品
        product = random.choice(PRODUCTS)
        
        # 生成评分
        rating = generate_random_rating(product["id"])
        
        # 生成评论
        comment = generate_random_comment(rating)
        
        # 生成消费记录ID
        purchase_id = f"PR{year}{month:02d}{i+1:06d}"
        
        record = {
            "purchase_id": purchase_id,
            "product_id": product["id"],
            "product_name": product["name"],
            "rating": rating,
            "comment": comment,
            "year": year,
            "month": month,
        }
        records.append(record)
    
    # 使用polars创建DataFrame
    df = pl.DataFrame(records)
    
    print(f"Test data generation completed. Total records: {len(df)}")
    
    # 统计信息
    rated_count = df.filter(pl.col("rating") > 0).shape[0]
    unrated_count = df.filter(pl.col("rating") == 0).shape[0]
    print(f"Rated records: {rated_count}, Unrated records: {unrated_count}")
    
    return df


def save_test_data(df, filepath):
    """
    保存测试数据到CSV文件
    
    Args:
        df: polars DataFrame
        filepath: 保存路径
    """
    df.write_csv(filepath)
    print(f"Test data saved to: {filepath}")


if __name__ == "__main__":
    # 生成测试数据
    test_data = generate_test_data(600)
    
    # 保存到文件
    output_path = "/Users/yiigaa/work/dogfooding-3-200/kimi/test/test_data.csv"
    save_test_data(test_data, output_path)
