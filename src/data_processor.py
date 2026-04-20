import polars as pl
import os


def load_data(file_path):
    """
    加载产品评分数据
    :param file_path: 数据文件路径
    :return: polars DataFrame
    """
    print(f"Loading data from {file_path}")
    return pl.read_csv(file_path)


def calculate_rating_probability(df):
    """
    计算评分/不评分的概率
    :param df: 原始数据DataFrame
    :return: 评分和不评分的数量统计
    """
    print("Calculating rating probability")
    total_count = df.height
    rated_count = df.filter(pl.col("rating") != 0).height
    not_rated_count = df.filter(pl.col("rating") == 0).height
    
    return {
        "labels": ["已评分", "未评分"],
        "values": [rated_count, not_rated_count],
        "percentages": [rated_count / total_count * 100, not_rated_count / total_count * 100]
    }


def calculate_review_length_by_rating(df):
    """
    按评分计算评论文本长度分布
    :param df: 原始数据DataFrame
    :return: 各评分的评论长度统计
    """
    print("Calculating review length distribution by rating")
    rated_df = df.filter(pl.col("rating") != 0)
    
    result = {}
    
    for rating in range(1, 6):
        rating_df = rated_df.filter(pl.col("rating") == rating)
        if rating_df.height == 0:
            continue
            
        len_0_10 = rating_df.filter(pl.col("review_text").str.len_chars() <= 10).height
        len_10_30 = rating_df.filter((pl.col("review_text").str.len_chars() > 10) & 
                                     (pl.col("review_text").str.len_chars() <= 30)).height
        len_30_plus = rating_df.filter(pl.col("review_text").str.len_chars() > 30).height
        
        total = len_0_10 + len_10_30 + len_30_plus
        
        result[rating] = {
            "labels": ["0-10字", "10-30字", "30字以上"],
            "values": [len_0_10, len_10_30, len_30_plus],
            "percentages": [
                len_0_10 / total * 100 if total > 0 else 0,
                len_10_30 / total * 100 if total > 0 else 0,
                len_30_plus / total * 100 if total > 0 else 0
            ]
        }
    
    return result


def calculate_product_avg_rating(df):
    """
    计算产品平均评分，取前4名，其余合并为其他
    :param df: 原始数据DataFrame
    :return: 产品平均评分统计
    """
    print("Calculating product average rating")
    rated_df = df.filter(pl.col("rating") != 0)
    
    product_stats = rated_df.group_by("product_id", "product_name").agg(
        pl.col("rating").mean().alias("avg_rating"),
        pl.col("rating").count().alias("rating_count")
    ).sort("avg_rating", descending=True)
    
    top_4 = product_stats.head(4)
    others_count = product_stats.slice(4).height
    others_avg_rating = product_stats.slice(4)["avg_rating"].mean() if others_count > 0 else 0
    
    labels = top_4["product_name"].to_list() + (["其他产品"] if others_count > 0 else [])
    values = top_4["avg_rating"].to_list() + ([others_avg_rating] if others_count > 0 else [])
    
    return {
        "labels": labels,
        "values": values,
        "top_products": top_4.to_dicts()
    }


def get_data_summary(df):
    """
    获取数据摘要信息
    :param df: 原始数据DataFrame
    :return: 数据摘要字典
    """
    total_records = df.height
    rated_records = df.filter(pl.col("rating") != 0).height
    avg_rating = df.filter(pl.col("rating") != 0)["rating"].mean()
    unique_products = df["product_id"].n_unique()
    
    return {
        "total_records": total_records,
        "rated_records": rated_records,
        "avg_rating": avg_rating,
        "unique_products": unique_products
    }
