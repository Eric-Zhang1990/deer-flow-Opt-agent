#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time     : 2025/7/28 15:54
@Author   : zhangshifeng
@File     : curve.py
@Description:
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from src.utils.extra_tools import generate_echarts_config
import matplotlib
matplotlib.use("Agg")


def get_p_temperature_curve(ratedPower, x, t0=20, t1=32):
    """
    计算HVAC系统功率-末端稳态温度特性曲线
    Args:
        ratedPower: 额定功率
        x: 功率
        t0: 最低温度，默认20
        t1: 室外温度，默认32
    Returns:
        指定功率下，末端稳态温度
    """

    T = t0 + (t1 - t0) * (1 + np.tanh(-(x - ratedPower / 2) / ratedPower * 4)) / 2
    return T


def get_p_by_temperature(T_max, ratedPower, t0=20, t1=32):
    """
    计算HVAC系统功率-末端稳态温度特性曲线的反函数
    Args:
        T_max: 末端稳态温度限制
        ratedPower: 额定功率
        t0: 最低温度，默认20
        t1: 室外温度，默认32
    Returns:
        指定温度下，功率
    """
    for x in range(0, ratedPower, 100):
        if get_p_temperature_curve(ratedPower, x, t0, t1) <= T_max:
            return x
    return 0


def plot_curve():
    ratedPower = 5000

    xs = []
    ys = []
    for xi in range(0, ratedPower, 50):
        xs.append(xi)
        y = get_p_temperature_curve(ratedPower, xi)
        ys.append(y)

    # 绘制曲线
    series_list = [
        {"name": "HVAC Power vs. Temperature Curve", "data": ys}
    ]
    output = generate_echarts_config("", chart_type="line", x_data=xs, series_list=series_list)

    return output
