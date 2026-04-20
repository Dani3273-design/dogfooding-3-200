"""
产品评分分析程序主入口

功能说明：
1. 加载产品评分数据
2. 分析评分分布、评论长度分布、产品平均评分
3. 生成可视化图表和PDF报告

使用方法：
    python main.py

程序会自动生成测试数据并输出分析报告
"""

import os
import sys

# 添加src和test目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "test"))

from generate_test_data import generate_test_data, save_test_data
from data_processor import process_data
from report_generator import generate_report


def main():
    """
    主函数，协调数据生成、处理和报告生成流程
    """
    print("=" * 50)
    print("Product Rating Analysis Program")
    print("=" * 50)
    
    # 定义文件路径
    test_data_path = "/Users/yiigaa/work/dogfooding-3-200/kimi/test/test_data.csv"
    report_output_path = "/Users/yiigaa/work/dogfooding-3-200/kimi/report/rating_analysis_report.pdf"
    
    # 步骤1：生成测试数据
    print("\n[Step 1] Generating test data...")
    test_data = generate_test_data(record_count=600)
    save_test_data(test_data, test_data_path)
    
    # 步骤2：处理数据
    print("\n[Step 2] Processing data...")
    analysis_result = process_data(test_data_path)
    
    # 步骤3：生成报告
    print("\n[Step 3] Generating report...")
    generate_report(analysis_result, report_output_path)
    
    # 完成
    print("\n" + "=" * 50)
    print("Analysis completed successfully!")
    print(f"Report saved to: {report_output_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
