#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time     : 2025/7/17 11:16
@Author   : zhangshifeng
@File     : builder.py
@Description:
"""
import pandas as pd
from src.report.graph.state import HousingPriceState
from src.report.graph.report_generator_node import generate_housing_data, generate_markdown_report
from langgraph.graph import END, START, StateGraph
from src.tools.human_assistance import human_assistance, async_human_assistance


def build_housing_price_graph():
    builder = StateGraph(HousingPriceState)

    async def human_feedback_node(state):
        print("当前城市:", state["city"])
        feedback = await async_human_assistance(
            message="是否要修改城市？(Y/N)"
        )
        choice = feedback["feedback"].strip().lower()
        if choice == "y":
            custom_city = input("请输入自定义城市名称: ")
            print("已修改城市为:", state["city"])
            return {"city": custom_city}
        else:
            print("保持当前城市:", state["city"])
            return {"city": state["city"]}

    def generate_data(state):
        print("正在生成数据...", state)
        df = generate_housing_data(state["city"])
        data = df.to_dict(orient="records")
        return {"data": data, "should_regenerate": False }

    def should_regenerate(state):
        return state.get("should_regenerate", False)

    async def confirm_data_node(state):
        feedback = await async_human_assistance(message="数据是否合理？(Y/N)")
        choice = feedback["feedback"].strip().lower()
        if choice == "y":
            print("数据已确认，继续")
            return {"should_regenerate": False}
        else:
            print("数据不合理，重新生成数据")
            return {"should_regenerate": True}

    def generate_report(state):
        print("正在生成报告...", state)
        df = pd.DataFrame(state["data"])
        md_file, image_path = generate_markdown_report(df, state["city"])
        return {"file_path": image_path}

    def llm_generate_report(state):
        import os
        import uuid
        import logging as logger
        from langchain.schema import HumanMessage, SystemMessage
        from src.config.agents import AGENT_LLM_MAP
        from src.llms.llm import get_llm_by_type
        from src.prompts.template import get_prompt_template
        logger.info("调用大模型：Generating ppt content...")
        # model = get_llm_by_type(AGENT_LLM_MAP["ppt_composer"])
        # ppt_content = model.invoke(
        #     [
        #         SystemMessage(content=get_prompt_template("ppt/ppt_composer")),
        #         HumanMessage(content=state["city"]),
        #     ],
        # )
        # logger.info(f"ppt_content: {ppt_content}")

        temp_ppt_file_path = os.path.join(os.getcwd(), f"ppt_content_{uuid.uuid4()}.md")
        # with open(temp_ppt_file_path, "w") as f:
        #     f.write(ppt_content.content)
        return {"ppt_file_path": temp_ppt_file_path}

    builder.add_node("human_feedback", human_feedback_node)
    builder.add_node("generate_data", generate_data)
    builder.add_node("confirm_data", confirm_data_node)
    builder.add_node("generate_report", generate_report)
    builder.add_node("llm_generate_report", llm_generate_report)

    builder.add_conditional_edges(
        "confirm_data",
        should_regenerate,
        {
            True: "generate_data",  # 如果 should_regenerate 为 True，回到 generate_data
            False: "generate_report"  # 否则继续到 generate_report
        }
    )

    builder.add_edge(START, "human_feedback")
    builder.add_edge("human_feedback", "generate_data")
    builder.add_edge("generate_data", "confirm_data")
    # builder.add_edge("confirm_data", "generate_report")   #加了add_conditional_edges，移除直接连接
    builder.add_edge("generate_report", "llm_generate_report")
    builder.add_edge("llm_generate_report", END)

    return builder.compile()
