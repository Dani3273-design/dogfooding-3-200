import csv
import random
from datetime import datetime, timedelta

PRODUCTS = [
    (1, "智能手机Pro Max"),
    (2, "无线蓝牙耳机"),
    (3, "智能手表运动版"),
    (4, "平板电脑12寸"),
    (5, "笔记本电脑轻薄本"),
    (6, "机械键盘RGB"),
    (7, "无线鼠标静音版"),
    (8, "4K高清显示器"),
    (9, "便携移动电源"),
    (10, "USB-C扩展坞"),
    (11, "智能音箱AI版"),
    (12, "游戏手柄无线版")
]

REVIEW_TEMPLATES = [
    "非常好，推荐购买",
    "产品质量不错，物流快",
    "性价比很高，值得购买",
    "使用体验一般，勉强能用",
    "不太满意，和描述有差距",
    "非常失望，不推荐",
    "做工精细，外观漂亮",
    "电池续航能力很强",
    "音质效果非常棒",
    "屏幕显示效果清晰",
    "运行速度很快，不卡顿",
    "手感舒适，操作简单",
    "客服态度好，解决问题快",
    "包装完好，没有损坏",
    "买给家人的，他们很喜欢",
    "第二次购买了，一如既往的好",
    "活动时买的，价格很实惠",
    "期待很久了，果然没失望",
    "功能齐全，满足日常需求",
    "发热量有点大，其他还好"
]


def generate_random_date(year, month):
    """生成指定年月的随机日期"""
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    start_date = datetime(year, month, 1)
    end_date = datetime(next_year, next_month, 1) - timedelta(days=1)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")


def generate_review_text(rating):
    """根据评分生成评论文本"""
    if random.random() < 0.4:
        return ""
    
    if rating >= 4:
        templates = REVIEW_TEMPLATES[:10]
    elif rating == 3:
        templates = REVIEW_TEMPLATES[5:15]
    else:
        templates = REVIEW_TEMPLATES[10:]
    
    base_text = random.choice(templates)
    if random.random() < 0.3:
        base_text += "！" * random.randint(1, 3)
    if random.random() < 0.2:
        base_text = "真的" + base_text
    
    return base_text[:100]


def generate_rating_for_product(product_id):
    """为产品生成评分，避免全5或全0分"""
    base_rating = 3 + (product_id % 3)
    
    if random.random() < 0.15:
        return 0, ""
    
    rating = max(1, min(5, base_rating + random.randint(-2, 1)))
    review_text = generate_review_text(rating)
    
    return rating, review_text


def generate_test_data():
    """生成600条测试数据"""
    print("Generating test data...")
    
    year = random.randint(2023, 2025)
    month = random.randint(1, 12)
    print(f"Random month: {year}年{month}月")
    
    records = []
    
    for i in range(600):
        product_id, product_name = random.choice(PRODUCTS)
        rating, review_text = generate_rating_for_product(product_id)
        purchase_date = generate_random_date(year, month)
        
        records.append({
            "rating": rating,
            "product_id": product_id,
            "product_name": product_name,
            "review_text": review_text,
            "purchase_record": f"ORD{year:04d}{month:02d}{i+1:04d}",
            "purchase_date": purchase_date
        })
    
    output_path = "test/rating_data.csv"
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["rating", "product_id", "product_name", 
                                               "review_text", "purchase_record", "purchase_date"])
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Generated 600 records at {output_path}")
    
    rated = sum(1 for r in records if r['rating'] > 0)
    print(f"Rated records: {rated}, Not rated: {600 - rated}")
    
    for r in range(1, 6):
        count = sum(1 for rec in records if rec['rating'] == r)
        avg_review_len = 0
        if count > 0:
            reviews = [len(rec['review_text']) for rec in records if rec['rating'] == r]
            avg_review_len = sum(reviews) / len(reviews)
        print(f"Rating {r}: {count} records, avg review length: {avg_review_len:.1f} chars")
    
    print("Test data generation completed!")


if __name__ == "__main__":
    generate_test_data()
