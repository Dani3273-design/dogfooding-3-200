# -*- coding: utf-8 -*-
"""
测试数据生成模块
用于生成产品评分测试数据，仅用于程序测试
"""

import random
import json
from datetime import datetime
from pathlib import Path


# 产品列表
PRODUCTS = [
    {"product_id": "P001", "product_name": "智能手机"},
    {"product_id": "P002", "product_name": "无线耳机"},
    {"product_id": "P003", "product_name": "平板电脑"},
    {"product_id": "P004", "product_name": "智能手表"},
    {"product_id": "P005", "product_name": "蓝牙音箱"},
    {"product_id": "P006", "product_name": "移动电源"},
    {"product_id": "P007", "product_name": "键盘鼠标套装"},
    {"product_id": "P008", "product_name": "显示器"},
]

# 评论模板（按评分等级分类）
COMMENT_TEMPLATES = {
    1: [
        "质量太差了",
        "完全不能用",
        "浪费钱",
        "很差",
        "不推荐购买",
        "太失望了",
        "质量有问题",
        "退货了",
        "非常不满意",
        "差评",
    ],
    2: [
        "一般般吧",
        "不太满意",
        "有些小问题",
        "性价比不高",
        "勉强能用",
        "有点失望",
        "质量一般",
        "不太推荐",
        "有待改进",
        "还行吧",
    ],
    3: [
        "还可以",
        "一般般",
        "凑合用",
        "中规中矩",
        "没什么特别的",
        "正常水平",
        "不算太好也不算太差",
        "可以接受",
        "还行",
        "普通",
    ],
    4: [
        "挺好的",
        "不错的产品",
        "性价比高",
        "值得购买",
        "质量不错",
        "很满意",
        "推荐购买",
        "好用",
        "超出预期",
        "物有所值",
    ],
    5: [
        "非常好",
        "强烈推荐",
        "完美",
        "太棒了",
        "超出预期",
        "质量很好",
        "非常满意",
        "物超所值",
        "五星好评",
        "完美无缺",
    ],
}


def generate_comment(rating: int) -> str:
    """
    根据评分生成评论文本
    
    参数:
        rating: 评分等级 (1-5)
    
    返回:
        生成的评论文本
    """
    # 30%概率不写评论
    if random.random() < 0.3:
        return ""
    
    templates = COMMENT_TEMPLATES.get(rating, COMMENT_TEMPLATES[3])
    base_comment = random.choice(templates)
    
    # 随机添加额外文字，使评论长度多样化
    additions = [
        "，下次还会来买",
        "，物流很快",
        "，包装很好",
        "，客服态度不错",
        "，整体感觉还可以",
        "，希望耐用",
        "，推荐给朋友了",
        "",
    ]
    
    if random.random() < 0.5:
        addition = random.choice(additions)
        base_comment = base_comment + addition
    
    # 限制100字
    if len(base_comment) > 100:
        base_comment = base_comment[:100]
    
    return base_comment


def generate_single_record(record_id: int) -> dict:
    """
    生成单条评分记录
    
    参数:
        record_id: 记录ID
    
    返回:
        包含评分数据的字典
    """
    product = random.choice(PRODUCTS)
    
    # 生成消费记录ID
    purchase_id = f"ORD{random.randint(100000, 999999)}"
    
    # 随机决定是否评分（约70%概率评分）
    if random.random() < 0.7:
        # 用户评分
        # 根据正态分布生成评分，倾向于高评分
        rating = max(1, min(5, int(random.gauss(3.8, 1.2))))
        comment = generate_comment(rating)
    else:
        # 用户不评分
        rating = 0
        comment = ""
    
    return {
        "record_id": record_id,
        "rating": rating,
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "comment_text": comment,
        "purchase_id": purchase_id,
    }


def generate_test_data(num_records: int = 600, output_dir: str = "test") -> str:
    """
    生成测试数据并保存为JSON文件
    
    参数:
        num_records: 生成的记录数量
        output_dir: 输出目录
    
    返回:
        生成的数据文件路径
    """
    # 随机生成年份和月份
    year = random.randint(2022, 2024)
    month = random.randint(1, 12)
    
    print(f"Generating {num_records} test records for {year}-{month:02d}...")
    
    records = []
    for i in range(1, num_records + 1):
        record = generate_single_record(i)
        records.append(record)
    
    # 统计各产品评分分布，确保没有全5分或全0分的产品
    product_ratings = {}
    for record in records:
        pid = record["product_id"]
        if pid not in product_ratings:
            product_ratings[pid] = []
        if record["rating"] > 0:
            product_ratings[pid].append(record["rating"])
    
    # 检查并调整异常数据
    for pid, ratings in product_ratings.items():
        if len(ratings) > 0:
            avg = sum(ratings) / len(ratings)
            # 如果平均分过高或过低，调整一些记录
            if avg >= 4.9 or avg <= 1.1:
                # 找到该产品的记录并调整
                for record in records:
                    if record["product_id"] == pid and record["rating"] > 0:
                        if avg >= 4.9:
                            record["rating"] = random.randint(3, 4)
                        elif avg <= 1.1:
                            record["rating"] = random.randint(2, 4)
                        record["comment_text"] = generate_comment(record["rating"])
                        break
    
    # 构建数据结构
    data = {
        "year": year,
        "month": month,
        "total_records": num_records,
        "records": records,
    }
    
    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_path = output_path / f"test_data_{year}{month:02d}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Test data saved to: {file_path}")
    print(f"Year: {year}, Month: {month}")
    
    # 打印统计信息
    rated_count = sum(1 for r in records if r["rating"] > 0)
    print(f"Rated records: {rated_count}, Unrated records: {num_records - rated_count}")
    
    return str(file_path)


if __name__ == "__main__":
    generate_test_data()
