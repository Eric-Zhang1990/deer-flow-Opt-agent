#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time     : 2025/7/26 14:52
@Author   : zhangshifeng
@File     : echarts_tools.py
@Description:
"""
import os
import re
import json
from typing import List

root = os.getenv("root")


def get_incremental_filename(base_filename):
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, base_filename)
    if not os.path.exists(path):
        return path  # 文件不存在，直接返回原始名字

    name, ext = os.path.splitext(base_filename)
    index = 1
    while True:
        new_path = os.path.join(root, f"{name}({index}){ext}")
        if not os.path.exists(new_path):
            return new_path
        index += 1


def natural_sort_key(s):
    # 提取文件名中的数字，没有数字的文件视为编号0
    match = re.search(r'(\d+)', s)
    num = int(match.group(1)) if match else 0
    prefix = re.sub(r'\(\d+\)', '', s).lower()  # 把 (数字) 去掉，保持前缀一致
    return (prefix, num)


def list_files_sorted(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort(key=natural_sort_key, reverse=False)
    return files


def generate_echarts_config(title, chart_type, x_data=None, series_list=None, radar_indicators=None):
    """
    通用ECharts配置生成函数
    :param title: 图表标题 (str)
    :param chart_type: 图表类型 ("line" / "bar" / "pie" / "radar")
    :param x_data: X轴数据 (list), 仅 line/bar 使用
    :param series_list: 列表，每个元素是 dict，如 {"name": "系列1", "data": [..]}，pie时data是value-name结构
    :param radar_indicators: 雷达图指标列表 [{"name": "指标1", "max": 100}, ...]
    :return: 格式化字符串 (```echarts 包裹)
    """
    config = {
        "legend": {
            "top": 10,
            "left": "center",
            "type": "scroll",
            "orient": "horizontal",
            "itemGap": 10,
            "width": "80%"
        },
        "grid": {
            "top": 100,
            "left": "10%",
            "right": "10%",
            "bottom": "10%"
        },
        "title": {"text": title},
        "tooltip": {},
        # "legend": {"top": "top"},
        "series": []
    }

    if chart_type in ["line", "bar"]:
        # Legend data
        legend_data = [s["name"] for s in series_list]
        config["legend"]["data"] = legend_data
        # X轴与Y轴
        config["xAxis"] = {"type": "category", "data": x_data}
        config["yAxis"] = {"type": "value"}
        # Series
        for s in series_list:
            config["series"].append({
                "name": s["name"],
                "type": chart_type,
                "data": s["data"]
            })

    elif chart_type == "pie":
        # Legend data
        legend_data = [s["name"] for s in series_list]
        config["legend"]["data"] = legend_data
        # Series
        pie_data = [{"name": s["name"], "value": s["data"]} for s in series_list]
        config["series"].append({
            "name": title,
            "type": "pie",
            "radius": "50%",
            "data": pie_data
        })

    elif chart_type == "radar":
        # Legend data
        legend_data = [s["name"] for s in series_list]
        config["legend"]["data"] = legend_data
        # Radar indicators
        config["radar"] = {"indicator": radar_indicators}
        # Series
        radar_data = []
        for s in series_list:
            radar_data.append({
                "name": s["name"],
                "value": s["data"]
            })
        config["series"].append({
            "name": title,
            "type": "radar",
            "data": radar_data
        })

    # 格式化为 JSON 风格字符串
    result = "```echarts\n" + json.dumps(config, ensure_ascii=False, indent=2) + "\n```"
    return result


def generate_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """
    根据输入的表头和数据行生成 Markdown 表格格式。

    Args:
        headers (List[str]): 表头列表
        rows (List[List[str]]): 每行数据，二维列表

    Returns:
        str: Markdown 表格字符串
    """
    # 构建表头行
    header_line = "| " + " | ".join(headers) + " |"
    # 构建分隔线
    separator_line = "|:" + ":|:".join(["---"] * len(headers)) + ":|"
    # 构建数据行
    data_lines = ["| " + " | ".join(row) + " |" for row in rows]

    # 拼接完整表格
    markdown_table = "\n".join([header_line, separator_line] + data_lines)
    return markdown_table


def get_vpp_alloc_plan(result={}):
    interpretation = result.get("interpretation", {})
    response_allocation = interpretation.get("response_allocation", [])
    report_content = interpretation.get("interpretation", "")
    formulation = result.get("formulation", {})
    device_names = formulation.get("device_names_cn", [])
    response_cost = formulation.get("response_cost", [])
    credit_scores = formulation.get("credit_scores", [])
    response_capacity = formulation.get("response_capacity", [])

    headers = ["响应资源", "可响应容量(MW)", "响应量(MW)", "响应成本(万元/MW)", "信用分"]
    rows = []
    total = 0
    for variable in response_allocation:
        name = variable["name"]
        value = variable["value"]
        cost = response_cost[device_names.index(name)]
        cost = str(round(cost, 2))
        score = credit_scores[device_names.index(name)]
        score = str(round(score, 2))
        capacity = response_capacity[device_names.index(name)]
        capacity = str(round(capacity, 2))
        total += value
        value = str(round(value, 2))
        rows.append([name, capacity, value, cost, score])
    markdown_table = generate_markdown_table(headers, rows)

    baseline_curve = ""
    plans_curve = ""
    plans = result.get("plans", [])
    if plans:
        x_data = []
        series_list = []
        baseline_list = []
        vpp_plans = plans[-1].get("VPP_Response_Plan", [])
        total_profit = 0
        for vpp_plan in vpp_plans:
            name = vpp_plan["device_name"]
            response_info = vpp_plan["response_info"]
            baseline = response_info["baseline"]
            x_data = baseline["time"]
            baseline_values = baseline["value"]
            each = {"name": name + "_baseline", "data": baseline_values}
            baseline_list.append(each)
            series_list.append(each)
            response_plan = response_info["response_plan"]
            response_plan_values = response_plan["value"]
            each = {"name": name + "_plan", "data": response_plan_values}
            series_list.append(each)
            response_profit = response_info["response_profit"]
            total_profit += response_profit
        baseline_curve = generate_echarts_config("基线曲线", chart_type="line", x_data=x_data, series_list=baseline_list)
        plans_curve = generate_echarts_config("基线-计划对比曲线", chart_type="line", x_data=x_data, series_list=series_list)
    else:
        print("没有生成计划信息")

    path = get_incremental_filename("result.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    markdown_bar_reporter = ""
    markdown_table_reporter = ""
    sorted_files = list_files_sorted(root)
    if len(sorted_files) > 1:
        headers = ["响应资源"]
        rows = []
        rows_list = []
        profit_headers = ["", "总收益(元)"]
        total_profit_list = []
        for i, file in enumerate(sorted_files):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                result = json.load(f)
                interpretation = result.get("interpretation", {})
                response_allocation = interpretation.get("response_allocation", [])
                report_content = interpretation.get("interpretation", "")
                headers.append(f"响应量{i + 1}(MW)")
                each_row = {}
                for variable in response_allocation:
                    name = variable["name"]
                    value = variable["value"]
                    value = str(round(value, 2))
                    each_row[name] = value
                rows_list.append(each_row)
                # 对比收益
                total_profit = 0
                plans = result.get("plans", [])
                if plans:
                    vpp_plans = plans[-1].get("VPP_Response_Plan", [])
                    for vpp_plan in vpp_plans:
                        response_info = vpp_plan["response_info"]
                        response_profit = response_info["response_profit"]
                        total_profit += response_profit
                total_profit_list.append([f"第{i + 1}次总收益", str(total_profit)])
        # 确定最长字典的key顺序（按出现的顺序）
        longest_dict = max(rows_list, key=lambda d: len(d))
        key_order = list(longest_dict.keys())
        # 按这个顺序补全并重排
        result_ordered = []
        for d in rows_list:
            new_d = {}
            for k in key_order:
                new_d[k] = d.get(k, "0.0")
            result_ordered.append(new_d)
        rows_list = result_ordered
        merged_result = {}
        for row in rows_list:
            for key, value in row.items():
                merged_result.setdefault(key, []).append(value)
        for key, values in merged_result.items():
            rows.append([key] + values)

        x_data = list(merged_result.keys())
        series_names = []
        for idx in range(len(merged_result[x_data[0]])):
            series_name = f"plan{idx + 1}"
            series_names.append(series_name)
        series_list = []
        for idx, series_name in enumerate(series_names):
            series_data = []
            current_data = rows_list[idx]
            for x in x_data:
                value = float(current_data.get(x, '0.0'))
                series_data.append(value)
            series_list.append({"name": series_name, "data": series_data})
        markdown_bar_reporter = generate_echarts_config("资源分配", chart_type="bar", x_data=x_data, series_list=series_list)
        markdown_table_reporter = generate_markdown_table(profit_headers, total_profit_list)

    if markdown_bar_reporter or markdown_table_reporter:
        report_content = report_content + "\n" + markdown_table + "\n" + markdown_bar_reporter + "\n" + markdown_table_reporter
    if baseline_curve and not markdown_bar_reporter:
        report_content = report_content + "\n" + markdown_table + "\n" + baseline_curve + "\n" + markdown_table_reporter

    return markdown_table, plans_curve, report_content


if __name__ == "__main__":
    # from dotenv import load_dotenv
    # load_dotenv()
    # root = os.getenv("root")
    # markdown_bar_reporter = ""
    # markdown_table_reporter = ""
    # sorted_files = list_files_sorted(root)
    # if len(sorted_files) > 1:
    #     headers = ["响应资源"]
    #     rows = []
    #     rows_list = []
    #     profit_headers = ["", "总收益(元)"]
    #     total_profit_list = []
    #     for i, file in enumerate(sorted_files):
    #         file_path = os.path.join(root, file)
    #         with open(file_path, "r", encoding="utf-8") as f:
    #             result = json.load(f)
    #             interpretation = result.get("interpretation", {})
    #             response_allocation = interpretation.get("response_allocation", [])
    #             report_content = interpretation.get("interpretation", "")
    #             headers.append(f"响应量{i + 1}(MW)")
    #             each_row = {}
    #             for variable in response_allocation:
    #                 name = variable["name"]
    #                 value = variable["value"]
    #                 value = str(round(value, 2))
    #                 each_row[name] = value
    #             rows_list.append(each_row)
    #             # 对比收益
    #             total_profit = 0
    #             plans = result.get("plans", [])
    #             if plans:
    #                 vpp_plans = plans[-1].get("VPP_Response_Plan", [])
    #                 for vpp_plan in vpp_plans:
    #                     response_info = vpp_plan["response_info"]
    #                     response_profit = response_info["response_profit"]
    #                     total_profit += response_profit
    #             total_profit_list.append([f"第{i + 1}次总收益", str(total_profit)])
    #     print(f"rows_list: {rows_list}")
    #     # 确定最长字典的key顺序（按出现的顺序）
    #     # 找到最长的那个dict
    #     longest_dict = max(rows_list, key=lambda d: len(d))
    #     key_order = list(longest_dict.keys())
    #
    #     # 按这个顺序补全并重排
    #     result_ordered = []
    #     for d in rows_list:
    #         new_d = {}
    #         for k in key_order:
    #             new_d[k] = d.get(k, "0.0")
    #         result_ordered.append(new_d)
    #     rows_list = result_ordered
    #     print(f"rows_list: {rows_list}")
    #     merged_result = {}
    #     for row in rows_list:
    #         for key, value in row.items():
    #             merged_result.setdefault(key, []).append(value)
    #     for key, values in merged_result.items():
    #         rows.append([key] + values)
    #
    #     x_data = list(merged_result.keys())
    #     series_names = []
    #     for idx in range(len(merged_result[x_data[0]])):
    #         series_name = f"plan{idx + 1}"
    #         series_names.append(series_name)
    #     series_list = []
    #     for idx, series_name in enumerate(series_names):
    #         series_data = []
    #         current_data = rows_list[idx]
    #         for x in x_data:
    #             value = float(current_data.get(x, '0.0'))
    #             series_data.append(value)
    #         series_list.append({"name": series_name, "data": series_data})
    #     markdown_bar_reporter = generate_echarts_config("资源分配", chart_type="bar", x_data=x_data, series_list=series_list)
    #     markdown_table_reporter = generate_markdown_table(profit_headers, total_profit_list)
    #     print(markdown_bar_reporter)
    #     print(markdown_table_reporter)
    # if markdown_bar_reporter or markdown_table_reporter:
    #     report_content = report_content + "\n" + markdown_bar_reporter + "\n" + markdown_table_reporter

    headers = ["响应资源", "可响应容量(MW)", "响应量(MW)", "响应成本(万元/MW)", "信用分"]
    rows = []
    rows.append(["name", "capacity", "value", "cost", "score"])
    table = generate_markdown_table(headers, rows)
    print( table)
