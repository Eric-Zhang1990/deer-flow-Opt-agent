# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import TypedDict, Optional
from src.config.report_style import ReportStyle
from langgraph.graph import MessagesState
from src.prompts.planner_model import Plan
from src.rag import Resource


class PromptEnhancerState(MessagesState):
    """State for the prompt enhancer workflow."""

    prompt: str = ""
    context: str = ""
    report_style: str = "academic"
    output: str = ""
    auto_accepted_plan: bool = False
