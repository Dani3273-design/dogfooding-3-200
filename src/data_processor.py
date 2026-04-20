"""
数据处理模块
负责读取、清洗和分析产品评分数据
"""

import polars as pl


def load_data(filepath):
    """
    从CSV文件加载数据
    
    Args:
        filepath: CSV文件路径
    
    Returns:
        pl.DataFrame: 加载的数据
    """
    print(f"Loading data from: {filepath}")
    df = pl.read_csv(filepath)
    print(f"Loaded {len(df)} records")
    return df


def analyze_rating_distribution(df):
    """
    分析评分/不评分的分布情况
    
    Args:
        df: 原始数据DataFrame
    
    Returns:
        dict: 包含评分和不评分数量的字典
    """
    # 统计评分和不评分的数量
    rated_count = df.filter(pl.col("rating") > 0).shape[0]
    unrated_count = df.filter(pl.col("rating") == 0).shape[0]
    
    result = {
        "rated": rated_count,
        "unrated": unrated_count,
        "total": len(df),
    }
    
    print(f"Rating distribution - Rated: {rated_count}, Unrated: {unrated_count}")
    return result


def analyze_comment_length_by_rating(df):
    """
    分析各评分等级的评论长度分布
    只针对做了评分的数据（rating > 0）
    
    Args:
        df: 原始数据DataFrame
    
    Returns:
        dict: 各评分等级的评论长度分布
    """
    # 过滤出有评分的数据
    rated_df = df.filter(pl.col("rating") > 0)
    
    # 计算每条评论的长度
    rated_df = rated_df.with_columns(
        pl.col("comment").str.len_chars().alias("comment_length")
    )
    
    result = {}
    
    # 对每个评分等级（1-5）分别统计
    for rating in range(1, 6):
        rating_df = rated_df.filter(pl.col("rating") == rating)
        
        if len(rating_df) == 0:
            result[rating] = {"short": 0, "medium": 0, "long": 0, "total": 0}
            continue
        
        # 统计评论长度分布
        # 0-10字：short，10-30字：medium，30字以上：long
        short_count = rating_df.filter(pl.col("comment_length") <= 10).shape[0]
        medium_count = rating_df.filter(
            (pl.col("comment_length") > 10) & (pl.col("comment_length") <= 30)
        ).shape[0]
        long_count = rating_df.filter(pl.col("comment_length") > 30).shape[0]
        
        result[rating] = {
            "short": short_count,
            "medium": medium_count,
            "long": long_count,
            "total": len(rating_df),
        }
        
        print(f"Rating {rating} - Short(0-10): {short_count}, Medium(10-30): {medium_count}, Long(30+): {long_count}")
    
    return result


def analyze_product_average_rating(df):
    """
    分析各产品的平均评分
    只统计有评分的数据
    
    Args:
        df: 原始数据DataFrame
    
    Returns:
        pl.DataFrame: 产品平均评分排名
    """
    # 过滤出有评分的数据
    rated_df = df.filter(pl.col("rating") > 0)
    
    # 按产品分组计算平均评分和评分数量
    product_stats = rated_df.group_by(["product_id", "product_name"]).agg([
        pl.col("rating").mean().alias("avg_rating"),
        pl.col("rating").count().alias("rating_count"),
    ])
    
    # 按平均评分降序排序
    product_stats = product_stats.sort("avg_rating", descending=True)
    
    print(f"Analyzed {len(product_stats)} products")
    
    return product_stats


def get_top_products(product_stats, top_n=4):
    """
    获取评分前N的产品
    
    Args:
        product_stats: 产品统计DataFrame
        top_n: 前N个产品数量
    
    Returns:
        tuple: (前N个产品DataFrame, 其他产品合并统计)
    """
    # 获取前N个产品
    top_products = product_stats.head(top_n)
    
    # 计算其他产品的合并统计
    if len(product_stats) > top_n:
        other_products = product_stats.tail(len(product_stats) - top_n)
        other_avg = other_products["avg_rating"].mean()
        other_count = other_products["rating_count"].sum()
    else:
        other_avg = 0
        other_count = 0
    
    other_stats = {
        "product_name": "其他产品",
        "avg_rating": other_avg,
        "rating_count": other_count,
    }
    
    print(f"Top {top_n} products selected, others aggregated")
    
    return top_products, other_stats


def process_data(filepath):
    """
    主处理函数，执行所有数据分析
    
    Args:
        filepath: 数据文件路径
    
    Returns:
        dict: 包含所有分析结果的字典
    """
    print("Starting data processing...")
    
    # 加载数据
    df = load_data(filepath)
    
    # 分析评分分布
    rating_dist = analyze_rating_distribution(df)
    
    # 分析评论长度分布
    comment_length_dist = analyze_comment_length_by_rating(df)
    
    # 分析产品平均评分
    product_stats = analyze_product_average_rating(df)
    
    # 获取前4产品和其他
    top_products, other_stats = get_top_products(product_stats, top_n=4)
    
    # 获取数据时间信息
    year = df["year"][0]
    month = df["month"][0]
    
    result = {
        "raw_data": df,
        "rating_distribution": rating_dist,
        "comment_length_distribution": comment_length_dist,
        "product_stats": product_stats,
        "top_products": top_products,
        "other_stats": other_stats,
        "year": year,
        "month": month,
    }
    
    print("Data processing completed")
    return result
