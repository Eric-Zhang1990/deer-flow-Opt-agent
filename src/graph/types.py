# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT


from langgraph.graph import MessagesState

from src.prompts.planner_model import Plan
from src.rag import Resource


class State(MessagesState):
    """State for the agent system, extends MessagesState with next field."""

    # Runtime Variables
    locale: str = "en-US"
    research_topic: str = ""
    observations: list[str] = []
    resources: list[Resource] = []
    plan_iterations: int = 0
    current_plan: Plan | str = None
    final_report: str = ""
    auto_accepted_plan: bool = False
    report_content: str = ""
    goto: str = "__end__"
    temp2power: float = 28
    power2temp: float = 100
    temperature: float = 30
    demand: float = 20
    default_requirement: str = "综合考虑各因素，最大化电厂收益"
    requirement: str = ""
    device_health_check: str = ""
    last_demand: float = 0
    last_requirement: str = ""

