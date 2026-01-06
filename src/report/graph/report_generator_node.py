#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time     : 2025/7/17 11:17
@Author   : zhangshifeng
@File     : report_generator_node.py
@Description:
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use("Agg")


def generate_housing_data(city: str, months: int = 12):
    dates = [datetime.now() - timedelta(days=i * 30) for i in range(months)][::-1]
    base_price = {
        "北京": 60000,
        "上海": 70000,
        "深圳": 55000,
        "广州": 40000,
        "成都": 20000,
        "默认城市": 30000
    }.get(city, 30000)
    prices = [base_price + np.random.normal(0, 2000) for _ in range(months)]
    return pd.DataFrame({"Date": dates, "Price (CNY/㎡)": prices})


def plot_trend(df: pd.DataFrame, city: str):
    plt.figure(figsize=(10, 6))
    plt.plot(df["Date"], df["Price (CNY/㎡)"], marker='o', linestyle='-', color='b')
    plt.title(f"{city} 趋势图")
    plt.xlabel("日期")
    plt.ylabel("价格 (元/㎡)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    root = os.path.abspath(os.path.dirname(__file__))
    file_name = os.path.join(root, f"{city}_trend.png")
    plt.savefig(file_name)
    plt.close()
    return file_name


def generate_markdown_report(df: pd.DataFrame, city: str):
    markdown_table = df.to_markdown(index=False)
    image_path = plot_trend(df, city)
    root = os.path.abspath(os.path.dirname(__file__))
    md_file = os.path.join(root, f"{city}_report.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# {city} 趋势报告\n\n")
        f.write("## 走势图\n\n")
        f.write(f"![{city} 趋势]({image_path})\n\n")
        f.write("## 数据表\n\n")
        f.write(markdown_table)
    print(f"✅ 数据已保存为 {md_file} 和 {image_path}")
    return md_file, image_path
