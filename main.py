import os
import shutil
from src.data_processor import (
    load_data,
    calculate_rating_probability,
    calculate_review_length_by_rating,
    calculate_product_avg_rating,
    get_data_summary
)
from src.chart_generator import create_all_charts
from src.pdf_reporter import create_pdf_report


def main():
    """
    主程序入口：产品评分数据分析
    流程：加载数据 -> 数据处理 -> 生成图表 -> 生成PDF报告 -> 清理临时文件
    """
    print("Starting product rating analysis program...")
    
    data_path = "test/rating_data.csv"
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        print("Please run test/generate_test_data.py first to generate test data.")
        return
    
    temp_chart_dir = "report/temp_charts"
    os.makedirs(temp_chart_dir, exist_ok=True)
    
    print("Step 1: Loading and processing data...")
    df = load_data(data_path)
    
    data_summary = get_data_summary(df)
    print(f"Data summary: {data_summary['total_records']} records, "
          f"{data_summary['rated_records']} rated, "
          f"avg rating: {data_summary['avg_rating']:.2f}")
    
    print("Step 2: Calculating statistics...")
    rating_prob_data = calculate_rating_probability(df)
    review_length_data = calculate_review_length_by_rating(df)
    product_rating_data = calculate_product_avg_rating(df)
    
    print("Step 3: Generating charts...")
    chart_paths = create_all_charts(
        rating_prob_data,
        review_length_data,
        product_rating_data,
        temp_chart_dir
    )
    
    print("Step 4: Generating PDF report...")
    pdf_output_path = "report/product_rating_report.pdf"
    create_pdf_report(
        pdf_output_path,
        data_summary,
        chart_paths,
        product_rating_data
    )
    
    print("Step 5: Cleaning up temporary files...")
    shutil.rmtree(temp_chart_dir)
    
    print("Analysis completed successfully!")
    print(f"Report generated at: {pdf_output_path}")


if __name__ == "__main__":
    main()
