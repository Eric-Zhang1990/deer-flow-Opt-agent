#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time     : 2025/7/18 9:57
@Author   : zhangshifeng
@File     : human_assistance.py
@Description:
"""
from typing import Dict, Any


def human_assistance(
    message: str,
    options: Dict[str, Any] = None,
    default: Any = None
) -> Dict[str, Any]:
    """
    模拟与用户的交互，返回用户选择的值。
    """
    print(message)
    if options:
        for key, value in options.items():
            print(f"{key}: {value}")
        choice = input("请选择一个选项: ")
        return {"feedback": choice, "selected_option": options.get(choice, default)}
    else:
        user_input = input("请输入选项 (Y/N): ").strip().lower()
        while user_input not in ["y", "n"]:
            print("输入无效，请输入 Y 或 N。")
            user_input = input("请输入选项 (Y/N): ").strip().lower()
        return {"feedback": user_input}


async def async_human_assistance(
    message: str,
    options: Dict[str, Any] = None,
    default: Any = None
) -> Dict[str, Any]:
    print(message)
    if options:
        for key, value in options.items():
            print(f"{key}: {value}")
        choice = input("请选择一个选项: ")
        return {"feedback": choice, "selected_option": options.get(choice, default)}
    else:
        user_input = input("请输入选项 (Y/N): ").strip().lower()
        while user_input not in ["y", "n"]:
            print("输入无效，请输入 Y 或 N。")
            user_input = input("请输入选项 (Y/N): ").strip().lower()
        return {"feedback": user_input}

