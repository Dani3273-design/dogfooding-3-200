# -*- coding: utf-8 -*-
"""
数据处理模块
使用polars进行产品评分数据的处理和分析
"""

import json
from typing import Dict, List, Tuple, Any
from pathlib import Path

import polars as pl


def load_data(file_path: str) -> Tuple[pl.DataFrame, int, int]:
    """
    从JSON文件加载数据并转换为polars DataFrame
    
    参数:
        file_path: JSON数据文件路径
    
    返回:
        (DataFrame, 年份, 月份) 元组
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    year = data.get("year", 2024)
    month = data.get("month", 1)
    records = data.get("records", [])
    
    # 使用polars创建DataFrame
    df = pl.DataFrame(records)
    
    print(f"Loaded {len(df)} records from {file_path}")
    
    return df, year, month


def calculate_rating_probability(df: pl.DataFrame) -> Dict[str, Any]:
    """
    计算评分/不评分的概率分布
    
    参数:
        df: 包含评分数据的DataFrame
    
    返回:
        包含评分概率分布的字典
    """
    total = len(df)
    rated_count = df.filter(pl.col("rating") > 0).height
    unrated_count = df.filter(pl.col("rating") == 0).height
    
    result = {
        "total": total,
        "rated_count": rated_count,
        "unrated_count": unrated_count,
        "rated_ratio": rated_count / total if total > 0 else 0,
        "unrated_ratio": unrated_count / total if total > 0 else 0,
    }
    
    print(f"Rating probability: Rated={rated_count}({result['rated_ratio']:.1%}), "
          f"Unrated={unrated_count}({result['unrated_ratio']:.1%})")
    
    return result


def categorize_comment_length(comment: str) -> str:
    """
    将评论长度分类
    
    参数:
        comment: 评论文本
    
    返回:
        长度分类标签
    """
    if not comment:
        return "无评论"
    length = len(comment)
    if length <= 10:
        return "0-10字"
    elif length <= 30:
        return "10-30字"
    else:
        return "30字以上"


def calculate_comment_length_distribution(df: pl.DataFrame) -> Dict[int, Dict[str, int]]:
    """
    计算各评分等级下评论长度分布
    仅针对有评分的数据（评分1-5）
    
    参数:
        df: 包含评分数据的DataFrame
    
    返回:
        按评分等级分组的评论长度分布字典
    """
    # 筛选有评分的记录
    rated_df = df.filter(pl.col("rating") > 0)
    
    # 添加评论长度分类列
    # 使用polars的map_elements应用自定义函数
    rated_df = rated_df.with_columns(
        pl.col("comment_text")
        .map_elements(lambda x: categorize_comment_length(x), return_dtype=pl.Utf8)
        .alias("comment_length_category")
    )
    
    result = {}
    
    # 按评分等级分组统计
    for rating in range(1, 6):
        rating_df = rated_df.filter(pl.col("rating") == rating)
        
        # 统计各长度分类的数量
        length_counts = {
            "0-10字": 0,
            "10-30字": 0,
            "30字以上": 0,
        }
        
        for row in rating_df.iter_rows(named=True):
            category = row["comment_length_category"]
            if category in length_counts:
                length_counts[category] += 1
        
        total = sum(length_counts.values())
        
        result[rating] = {
            "counts": length_counts,
            "total": total,
            "ratios": {
                k: v / total if total > 0 else 0 
                for k, v in length_counts.items()
            }
        }
        
        print(f"Rating {rating}: Total={total}, "
              f"0-10字={length_counts['0-10字']}, "
              f"10-30字={length_counts['10-30字']}, "
              f"30字以上={length_counts['30字以上']}")
    
    return result


def calculate_product_average_rating(df: pl.DataFrame) -> Dict[str, Any]:
    """
    计算产品平均评分，取前4名产品，其余合并为"其他产品"
    
    参数:
        df: 包含评分数据的DataFrame
    
    返回:
        包含产品平均评分分布的字典
    """
    # 筛选有评分的记录
    rated_df = df.filter(pl.col("rating") > 0)
    
    # 按产品分组计算平均评分
    product_stats = (
        rated_df
        .group_by(["product_id", "product_name"])
        .agg([
            pl.col("rating").mean().alias("avg_rating"),
            pl.col("rating").count().alias("rating_count"),
        ])
        .sort("avg_rating", descending=True)
    )
    
    # 转换为列表处理
    products = product_stats.to_dicts()
    
    # 取前4名
    top_4 = products[:4]
    
    # 计算其他产品的平均评分
    other_products = products[4:]
    
    result = {
        "top_products": [],
        "other_products": None,
    }
    
    for p in top_4:
        result["top_products"].append({
            "product_id": p["product_id"],
            "product_name": p["product_name"],
            "avg_rating": round(p["avg_rating"], 2),
            "rating_count": p["rating_count"],
        })
    
    if other_products:
        # 计算其他产品的加权平均评分
        total_count = sum(p["rating_count"] for p in other_products)
        if total_count > 0:
            weighted_sum = sum(p["avg_rating"] * p["rating_count"] for p in other_products)
            other_avg = weighted_sum / total_count
            result["other_products"] = {
                "product_name": "其他产品",
                "avg_rating": round(other_avg, 2),
                "rating_count": total_count,
                "product_count": len(other_products),
            }
    
    # 打印结果
    print("\nProduct Average Ratings:")
    for p in result["top_products"]:
        print(f"  {p['product_name']}: {p['avg_rating']:.2f} ({p['rating_count']} ratings)")
    if result["other_products"]:
        print(f"  其他产品: {result['other_products']['avg_rating']:.2f} "
              f"({result['other_products']['rating_count']} ratings)")
    
    return result


def process_all_data(df: pl.DataFrame) -> Dict[str, Any]:
    """
    执行所有数据分析处理
    
    参数:
        df: 包含评分数据的DataFrame
    
    返回:
        包含所有分析结果的字典
    """
    print("\n=== Starting Data Analysis ===\n")
    
    result = {
        "rating_probability": calculate_rating_probability(df),
        "comment_length_distribution": calculate_comment_length_distribution(df),
        "product_ratings": calculate_product_average_rating(df),
    }
    
    print("\n=== Data Analysis Complete ===\n")
    
    return result
