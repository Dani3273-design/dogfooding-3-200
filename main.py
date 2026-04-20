# -*- coding: utf-8 -*-
"""
产品评分分析程序 - 主入口
"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.data_processor import load_data, process_all_data
from src.report_generator import generate_pdf_report


def main():
    """
    主程序入口函数
    执行流程：加载数据 -> 分析处理 -> 生成报告
    """
    print("=" * 50)
    print("Product Rating Analysis Program")
    print("=" * 50)
    
    # 查找测试数据文件
    test_dir = Path("test")
    data_files = list(test_dir.glob("test_data_*.json"))
    
    if not data_files:
        print("Error: No test data file found in test/ directory")
        print("Please run test/generate_test_data.py first to generate test data")
        return 1
    
    # 使用最新的数据文件
    data_file = sorted(data_files)[-1]
    print(f"Using data file: {data_file}")
    
    # 加载数据
    df, year, month = load_data(str(data_file))
    
    # 数据分析处理
    analysis_result = process_all_data(df)
    
    # 生成PDF报告
    pdf_path = generate_pdf_report(analysis_result, year, month, "report")
    
    print("\n" + "=" * 50)
    print("Analysis Complete!")
    print(f"Report saved to: {pdf_path}")
    print("=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
