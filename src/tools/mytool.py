#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time     : 2025/7/24 10:59
@Author   : zhangshifeng
@File     : mytool.py
@Description:
"""
# from langchain_core.tools import tool
#
# @tool
# def my_custom_tool():
#     """这是一个搜索工具
#        input_text: 需要检索的关键信息
#     """
#     return "这是自定义工具"



from langchain_core.tools import tool
from typing import Annotated
import logging

logger = logging.getLogger(__name__)

@tool
def my_custom_tool(
    ppt_prompt: Annotated[
        str, "The prompt content from ppt_prompt.md to generate the PPT content."
    ],
) -> str:
    """Use this tool to generate a PPT outline or content based on a given prompt.
    Provide a detailed markdown structure or bullet points suitable for PPT slides."""
    if not isinstance(ppt_prompt, str):
        error_msg = f"Invalid input: ppt_prompt must be a string, got {type(ppt_prompt)}"
        logger.error(error_msg)
        return f"Error processing PPT prompt:\n```\n{ppt_prompt}\n```\nError: {error_msg}"

    logger.info("Processing PPT generation prompt")
    try:
        # Here you would ideally call an LLM or template rendering logic.
        # For demonstration, let's assume we just structure it into slides.

        slides = []
        lines = ppt_prompt.strip().split("\n")
        current_slide = []

        for line in lines:
            if line.strip() == "":
                continue  # skip empty lines
            if line.startswith("#"):
                # Treat markdown headers as slide titles
                if current_slide:
                    slides.append(current_slide)
                current_slide = [line.strip()]
            else:
                current_slide.append(line.strip())
        if current_slide:
            slides.append(current_slide)

        # Format as markdown PPT outline
        ppt_output = "# Generated PPT Outline\n\n"
        for idx, slide in enumerate(slides, 1):
            ppt_output += f"## Slide {idx}: {slide[0].lstrip('#').strip()}\n"
            for bullet in slide[1:]:
                ppt_output += f"- {bullet}\n"
            ppt_output += "\n"

        logger.info("PPT content generated successfully")

    except Exception as e:
        error_msg = repr(e)
        logger.error(error_msg)
        return f"Error generating PPT content:\n```\n{ppt_prompt}\n```\nError: {error_msg}"

    return ppt_output
