# 产品评分分析程序

## 项目简介

本程序用于分析产品评分数据，生成可视化图表并输出PDF格式的分析报告。

## 功能特性

1. **评分参与率分析**：统计用户评分/不评分的比例，输出饼状图
2. **评论意愿分析**：针对已评分数据，按评分等级（1-5分）分别统计评论长度分布
   - 0-10字
   - 10-30字
   - 30字以上
3. **产品平均评分分析**：计算各产品平均评分，展示前4名产品及"其他产品"的评分分布
4. **PDF报告输出**：生成中文PDF报告，包含所有分析图表

## 目录结构

```
.
├── main.py              # 主程序入口
├── requirements.txt     # 依赖文件
├── README.md           # 项目说明文档
├── test/               # 测试数据目录
│   └── generate_test_data.py  # 测试数据生成脚本
├── report/             # 报告输出目录
│   └── *.pdf          # 生成的PDF报告
└── src/                # 源码目录
    ├── __init__.py
    ├── data_processor.py    # 数据处理模块
    └── report_generator.py  # 报告生成模块
```

## 环境要求

- Python 3.9+
- 操作系统：macOS / Linux / Windows

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 生成测试数据

```bash
python test/generate_test_data.py
```

此命令将在 `test/` 目录下生成测试数据文件，包含600条随机评分记录。

### 2. 运行分析程序

```bash
python main.py
```

程序将自动：
- 读取 `test/` 目录下的测试数据
- 执行数据分析
- 在 `report/` 目录生成PDF报告

### 3. 查看报告

报告文件命名格式：`product_rating_report_YYYYMM.pdf`

## 数据格式说明

测试数据为JSON格式，包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| record_id | int | 记录ID |
| rating | int | 评分（0表示未评分，1-5表示评分等级） |
| product_id | string | 产品ID |
| product_name | string | 产品名称 |
| comment_text | string | 评论文本（最多100字） |
| purchase_id | string | 消费记录ID |

## 技术栈

- **数据处理**：Polars（高性能DataFrame库）
- **图表生成**：Plotly（交互式图表库）
- **PDF生成**：ReportLab（PDF文档生成库）
- **图片导出**：Kaleido（Plotly静态图片导出）

## 注意事项

1. 程序输出文本采用英文，报告内容为中文
2. PDF报告生成需要系统中安装中文字体
3. 重复运行程序会覆盖同名PDF报告
4. 测试数据生成仅用于程序测试，不属于分析程序功能

## 代码规范

- 采用蛇形命名规范（snake_case）
- 函数和重点API添加中文注释
