#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time     : 2025/7/17 10:58
@Author   : zhangshifeng
@File     : state.py
@Description:
"""
from langgraph.graph import MessagesState
from typing import Dict, Any, List


class HousingPriceState(MessagesState):
    city: str = ""
    data: List[Dict[str, Any]] = []
    file_path: str = ""
    should_regenerate: bool = False
    ppt_file_path: str = ""
