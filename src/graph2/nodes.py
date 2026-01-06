# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage, AIMessageChunk
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.agents import create_agent
from src.tools.search import LoggedTavilySearch
from src.tools import (
    crawl_tool,
    get_web_search_tool,
    get_retriever_tool,
    python_repl_tool,
)

from src.config.agents import AGENT_LLM_MAP
from src.config.configuration import Configuration
from src.llms.llm import get_llm_by_type
from src.prompts.planner_model import Plan
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output

from .types import State
from ..config import SELECTED_SEARCH_ENGINE, SearchEngine

logger = logging.getLogger(__name__)


@tool
def handoff_to_planner(
    research_topic: Annotated[str, "The topic of the research task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to do plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return


def background_investigation_node(state: State, config: RunnableConfig):
    logger.info("background investigation node is running.")
    configurable = Configuration.from_runnable_config(config)
    query = state.get("research_topic")
    background_investigation_results = None
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        searched_content = LoggedTavilySearch(
            max_results=configurable.max_search_results
        ).invoke(query)
        if isinstance(searched_content, list):
            background_investigation_results = [
                f"## {elem['title']}\n\n{elem['content']}" for elem in searched_content
            ]
            return {
                "background_investigation_results": "\n\n".join(
                    background_investigation_results
                )
            }
        else:
            logger.error(
                f"Tavily search returned malformed response: {searched_content}"
            )
    else:
        background_investigation_results = get_web_search_tool(
            configurable.max_search_results
        ).invoke(query)
    return {
        "background_investigation_results": json.dumps(
            background_investigation_results, ensure_ascii=False
        )
    }


def planner_node(
    state: State, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter"]]:
    """Planner node that generate the full plan."""
    logger.info("Planner generating full plan: {}".format(state))
    configurable = Configuration.from_runnable_config(config)
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    messages = state['messages']

    # llm = get_llm_by_type(AGENT_LLM_MAP["planner"])
    # response = llm.invoke(messages)
    # full_response = response.content

    full_response = (
        "# 静态规划结果\n"
        "这是一个无需LLM的静态markdown内容示例。\n"
        "- 这是一个列表项\n"
        "- 这是另一个列表项\n\n"
        f"- Topic: {state['research_topic']}\n"
        # f"![趋势]({image_path})\n"
        # f"{markdown_table}\n"
    )

    logger.info(f"Current state messages: {state['messages']}")
    logger.info(f"Planner response: {full_response}")

    # try:
    #     curr_plan = json.loads(repair_json_output(full_response))
    # except json.JSONDecodeError:
    #     logger.warning("Planner response is not a valid JSON")
    #     if plan_iterations > 0:
    #         logger.info("Planner: 下一步reporter-1")
    #         return Command(goto="reporter")
    #     else:
    #         logger.info("Planner: 下一步__end__")
    #         return Command(goto="__end__")
    # if curr_plan.get("has_enough_context", False):
    #     logger.info("Planner: 下一步reporter-2")
    #     return Command(
    #         update={
    #             "messages": [AIMessageChunk(content=full_response, name="planner")],
    #             "current_plan": full_response,
    #         },
    #         goto="reporter",
    #     )
    logger.info("Planner: 下一步human_feedback")
    return Command(
        update={
            "messages": [AIMessage(content=full_response, name="planner",
                                        response_metadata={"finish_reason": "stop"})],
            "current_plan": full_response,
        },
        goto="human_feedback",
    )


def human_feedback_node(
    state,
) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
    logger.info("Running human_feedback_node")
    current_plan = state.get("current_plan", "")
    # check if the plan is auto accepted
    auto_accepted_plan = state.get("auto_accepted_plan", False)
    if not auto_accepted_plan:
        feedback = interrupt("Please Review the Plan.")

        # if the feedback is not accepted, return the planner node
        if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
            return Command(
                update={
                    "messages": [
                        HumanMessage(content=feedback, name="feedback"),
                    ],
                    "research_topic": str(feedback).replace("[edit_plan]", "").strip(),
                },
                goto="planner",
            )
        elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
            logger.info("Plan is accepted by user.")
        else:
            raise TypeError(f"Interrupt value of {feedback} is not supported.")

    # if the plan is accepted, run the following node
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    goto = "research_team"
    # try:
    #     current_plan = repair_json_output(current_plan)
    #     # increment the plan iterations
    #     plan_iterations += 1
    #     # parse the plan
    #     new_plan = json.loads(current_plan)
    # except json.JSONDecodeError:
    #     logger.warning("Planner response is not a valid JSON")
    #     if plan_iterations > 1:  # the plan_iterations is increased before this check
    #         return Command(goto="reporter")
    #     else:
    #         return Command(goto="__end__")

    return Command(
        update={
            "current_plan": state["current_plan"],
            "plan_iterations": plan_iterations,
            "locale": "zh-CN",
        },
        goto=goto,
    )


def coordinator_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner", "background_investigator", "__end__"]]:
    """Coordinator node that communicate with customers."""
    logger.info("Coordinator talking.")
    configurable = Configuration.from_runnable_config(config)
    messages = apply_prompt_template("coordinator", state)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["coordinator"])
        .bind_tools([handoff_to_planner])
        .invoke(messages)
    )
    logger.debug(f"Current state messages: {state['messages']}")

    goto = "__end__"
    locale = state.get("locale", "en-US")  # Default locale if not specified
    research_topic = state.get("research_topic", "")

    if len(response.tool_calls) > 0:
        goto = "planner"
        if state.get("enable_background_investigation"):
            # if the search_before_planning is True, add the web search tool to the planner agent
            goto = "background_investigator"
        try:
            for tool_call in response.tool_calls:
                if tool_call.get("name", "") != "handoff_to_planner":
                    continue
                if tool_call.get("args", {}).get("locale") and tool_call.get(
                    "args", {}
                ).get("research_topic"):
                    locale = tool_call.get("args", {}).get("locale")
                    research_topic = tool_call.get("args", {}).get("research_topic")
                    break
        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")
    else:
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."
        )
        logger.debug(f"Coordinator response: {response}")

    return Command(
        update={
            "locale": locale,
            "research_topic": research_topic,
            "resources": configurable.resources,
        },
        goto=goto,
    )


def reporter_node(state: State, config: RunnableConfig):
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")
    configurable = Configuration.from_runnable_config(config)
    current_plan = state.get("current_plan")
    # input_ = {
    #     "messages": [
    #         HumanMessage(
    #             f"# Research Requirements\n\n## Description\n\n{current_plan}"
    #         )
    #     ],
    #     "locale": state.get("locale", "en-US"),
    # }
    # invoke_messages = apply_prompt_template("reporter", input_, configurable)
    # observations = state.get("observations", [])
    # invoke_messages.append(
    #     HumanMessage(
    #         content=observations,
    #         name="observation",
    #     )
    # )
    #
    # logger.debug(f"Current invoke messages: {invoke_messages}")
    # response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(invoke_messages)
    # response_content = response.content

    response_content = (
    "# 上海 趋势报告\n"

    "## 走势图\n"

    "![](/images/image123.png)\n"

    "## 数据表\n"

    "| Date                       |   Price (CNY/㎡) |\n"
    "|:---------------------------|-----------------:|\n"
    "| 2024-08-25 10:43:30.243896 |          69665.4 |\n"
    "| 2024-09-24 10:43:30.243896 |          71327.4 |\n"
    "| 2024-10-24 10:43:30.243896 |          72681.7 |\n")

    logger.info(f"reporter response: {response_content}")

    return Command(
            update={
                "messages": [AIMessage(content=response_content, name="reporter",
                                            response_metadata={"finish_reason": "stop"})],
            },
            goto="__end__",
        )


def research_team_node(state: State):
    """Research team node that collaborates on tasks."""
    logger.info("Research team is collaborating on tasks.")
    pass


async def _execute_agent_step(
    state: State, agent, agent_name: str
) -> Command[Literal["research_team"]]:
    """Helper function to execute a step using the specified agent."""
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])

    # Find the first unexecuted step
    # current_step = None
    # completed_steps = []
    # for step in current_plan.steps:
    #     if not step.execution_res:
    #         current_step = step
    #         break
    #     else:
    #         completed_steps.append(step)
    #
    # if not current_step:
    #     logger.warning("No unexecuted step found")
    #     return Command(goto="research_team")
    #
    # logger.info(f"Executing step: {current_step.title}, agent: {agent_name}")
    #
    # # Format completed steps information
    # completed_steps_info = ""
    # if completed_steps:
    #     completed_steps_info = "# Existing Research Findings\n\n"
    #     for i, step in enumerate(completed_steps):
    #         completed_steps_info += f"## Existing Finding {i + 1}: {step.title}\n\n"
    #         completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"
    #
    # # Prepare the input for the agent with completed steps info
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"Current Task\n\n## Description\n\n{current_plan}\n\n## Locale\n\n{state.get('locale', 'en-US')}"
            )
        ]
    }

    # Add citation reminder for researcher agent
    if agent_name == "researcher":
        agent_input["messages"].append(
            HumanMessage(
                content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
                name="system",
            )
        )

    # Invoke the agent
    default_recursion_limit = 2
    try:
        env_value_str = os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit))
        parsed_limit = int(env_value_str)

        if parsed_limit > 0:
            recursion_limit = parsed_limit
            logger.info(f"Recursion limit set to: {recursion_limit}")
        else:
            logger.warning(
                f"AGENT_RECURSION_LIMIT value '{env_value_str}' (parsed as {parsed_limit}) is not positive. "
                f"Using default value {default_recursion_limit}."
            )
            recursion_limit = default_recursion_limit
    except ValueError:
        raw_env_value = os.getenv("AGENT_RECURSION_LIMIT")
        logger.warning(
            f"Invalid AGENT_RECURSION_LIMIT value: '{raw_env_value}'. "
            f"Using default value {default_recursion_limit}."
        )
        recursion_limit = default_recursion_limit

    logger.info(f"Agent input: {agent_input}")
    logger.info(f"Agent tools: {agent.tools}")
    available_tools = [tool.name for tool in agent.tools]
    result = await agent.ainvoke(
        input=agent_input, config={"recursion_limit": recursion_limit, "early_stopping_method": "generate"}
    )
    # import copy
    # logger.info(f"原始的result: {copy.deepcopy(result)}")
    # # 取 messages 列表
    # messages = result.get("messages", [])
    # # 过滤掉非 available_tools 工具相关的消息
    # filtered_messages = []
    # for message in messages:
    #     if message.type == "tool" and message.name not in available_tools:
    #         continue  # 跳过非 my_custom_tool 的工具调用消息
    #     filtered_messages.append(message)
    #
    # # 更新 state 只保留合法 messages
    # result["messages"] = filtered_messages
    # logger.info(f"过滤后的result: {result}")

    # Process the result
    response_content = result["messages"][-1].content
    logger.info(f"{agent_name.capitalize()} full response: {response_content}")

    # response_content = current_plan
    return Command(
        update={
            "messages": [AIMessage(content=response_content, name=agent_name,
                                            response_metadata={"finish_reason": "stop"})],
        },
        goto="reporter",
    )


async def _setup_and_execute_agent_step(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: list,
) -> Command[Literal["research_team"]]:
    """Helper function to set up an agent with appropriate tools and execute a step.

    This function handles the common logic for both researcher_node and coder_node:
    1. Configures MCP servers and tools based on agent type
    2. Creates an agent with the appropriate tools or uses the default agent
    3. Executes the agent on the current step

    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent ("researcher" or "coder")
        default_tools: The default tools to add to the agent

    Returns:
        Command to update state and go to research_team
    """
    # configurable = Configuration.from_runnable_config(config)
    # mcp_servers = {}
    # enabled_tools = {}
    #
    # # Extract MCP server configuration for this agent type
    # if configurable.mcp_settings:
    #     for server_name, server_config in configurable.mcp_settings["servers"].items():
    #         if (
    #             server_config["enabled_tools"]
    #             and agent_type in server_config["add_to_agents"]
    #         ):
    #             mcp_servers[server_name] = {
    #                 k: v
    #                 for k, v in server_config.items()
    #                 if k in ("transport", "command", "args", "url", "env")
    #             }
    #             for tool_name in server_config["enabled_tools"]:
    #                 enabled_tools[tool_name] = server_name
    #
    # # Create and execute agent with MCP tools if available
    # if mcp_servers:
    #     async with MultiServerMCPClient(mcp_servers) as client:
    #         loaded_tools = default_tools[:]
    #         for tool in client.get_tools():
    #             if tool.name in enabled_tools:
    #                 tool.description = (
    #                     f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
    #                 )
    #                 loaded_tools.append(tool)
    #         agent = create_agent(agent_type, agent_type, loaded_tools, agent_type)
    #         return await _execute_agent_step(state, agent, agent_type)
    # else:
    #     # Use default tools if no MCP servers are configured
    #     agent = create_agent(agent_type, agent_type, default_tools, agent_type)
    #     return await _execute_agent_step(state, agent, agent_type)
    agent = create_agent(agent_type, agent_type, default_tools, agent_type)
    return await _execute_agent_step(state, agent, agent_type)


async def researcher_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")
    # configurable = Configuration.from_runnable_config(config)
    # tools = [get_web_search_tool(configurable.max_search_results), crawl_tool]
    # retriever_tool = get_retriever_tool(state.get("resources", []))
    # if retriever_tool:
    #     tools.insert(0, retriever_tool)
    # logger.info(f"Researcher tools: {tools}")
    # return await _setup_and_execute_agent_step(
    #     state,
    #     config,
    #     "researcher",
    #     tools,
    # )
    from src.tools.mytool import my_custom_tool
    logger.info("PPT node is generating.")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher",
        [my_custom_tool],
    )


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        [python_repl_tool],
    )


async def ppt_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    from src.tools.mytool import my_custom_tool
    logger.info("PPT node is generating.")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "ppt_composer",
        [my_custom_tool],
    )