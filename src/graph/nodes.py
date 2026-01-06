# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage
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
from src.graph_solver.opt_subgraph import subgraph
from src.utils.extra_tools import *
from src.utils.curve import *

logger = logging.getLogger(__name__)


@tool
def handoff_to_planner():
    """Handoff to planner agent to do plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return


@tool
def vpp_trader(
        demand: Annotated[float, "需求响应值，单位MW(兆瓦)，默认为20"],
        hvac_max_temp: Annotated[float, "暖通负荷末端温度上限，默认为30,用户对温度有不明确的需求时需要向用户确认"],
        requirement: Annotated[str, "请从描述中提取用户对于优化任务的优化目标，默认为'收益优先模式'"],
        user_modified_request: Annotated[str, "请从描述中提取用户对于任务的所有要求，例如目标、约束、限制等"]):
    """虚拟电厂交易工具，用于进行需求响应、指令分解等工作，注意单位转换
      你是一个虚拟电厂调度助手，请根据用户自然语言输入，从中提取以下内容：
        1. **demand**：如提到电网下发的响应指令，提取数值（单位：MW）
        2. **hvac_max_temp**：如提到空调/暖通温度限制，提取其最大值，默认为30,用户对温度有不明确的需求时需要向用户确认
        3. **requirement**：如描述优化目标，如"信用优先"、"成本优先"、"考虑信用和成本"、"综合考虑各因素"
        4. **user_modified_request**：请从描述中提取用户对于任务的所有要求，例如目标、约束、限制等
    """
    
    logger.info("虚拟电厂交易工具正在运行...")
    return


@tool
def curve_trader(
        research_topic: Annotated[str, "查看功率温度特性曲线"],
):
    """查看功率曲线工具，用于展示功率温度特性曲线"""
    logger.info("功率曲线工具正在运行...")
    return


def curve_node(state: State, config: RunnableConfig
               ) -> Command[Literal["human_feedback", "reporter", "__end__"]]:
    """Planner node that generate the full plan."""
    logger.info("查看功率温度的特性曲线")
    output = plot_curve()
    response_content = (
        "## 功率温度的特性曲线\n"
        f"{output}\n"
    )

    return Command(
        update={
            "messages": [AIMessage(content=response_content, name="curve",
                                   response_metadata={"finish_reason": "stop"})],
        },
        goto="__end__",
    )


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
) -> Command[Literal["human_feedback", "reporter", "__end__"]]:
    """Planner node that generate the full plan."""
    logger.info("Planner generating full plan: {}".format(state))
    device_health_check = state.get("device_health_check", "")
    if device_health_check:
        query = device_health_check
    else:
        query = state["research_topic"]
    requirement = state.get("requirement", "")
    temperature = state.get("temperature", 30)
    describe = "1. 信用评级优先模式，您获得的考核最低，收益最稳定；\n2. 收益最高优先模式(默认)，风险也更高，您可能会超量响应，超量响应部分的收益会降低，也就是说单位收益会下降，并且可能会存在一定的考核风险"
    full_response = (
        "### 邀约响应\n\n"
        f"- 需求: {query}\n"
        f"- 推荐模式: \n"
        f"{describe}\n"
        f"- 暖通负荷末端温度上限: {temperature}℃\n"
    )
    logger.info(f"Planner response: {full_response}")

    return Command(
        update={
            "messages": [AIMessage(content=full_response, name="planner",
                                   response_metadata={"finish_reason": "stop"})],
            "current_plan": full_response,
            "goto": "vpp",
        },
        goto="human_feedback",
    )


def human_feedback_node(
        state,
) -> Command[Literal["coordinator", "planner", "reporter", "vpp", "__end__"]]:
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
                goto="coordinator",
            )
        elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
            logger.info("Plan is accepted by user.")
        else:
            raise TypeError(f"Interrupt value of {feedback} is not supported.")

    # if the plan is accepted, run the following node
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0

    goto = state["goto"]
    logger.info(f"human_feedback_node: 下一步{goto}")
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
) -> Command[Literal["planner", "__end__"]]:
    """Coordinator node that communicate with customers."""
    logger.info("Coordinator talking.")
    configurable = Configuration.from_runnable_config(config)
    messages = apply_prompt_template("coordinator", state)
    logger.info(f"coordinator_node messages: {messages}")
    response = (
        get_llm_by_type(AGENT_LLM_MAP["coordinator"])
            .bind_tools([vpp_trader, curve_trader], tool_choice="auto")
            .invoke(messages)
    )
    logger.debug(f"Current state messages: {state['messages']}")

    goto = "__end__"
    locale = state.get("locale", "en-US")  # Default locale if not specified
    research_topic = state.get("research_topic", "")
    temp2power = state.get("temp2power", 28)
    power2temp = state.get("power2temp", 100)
    temperature = state.get("temperature", 30)
    demand = state.get("demand", 20)
    requirement = state.get("requirement")
    user_modified_request = ""
    last_demand = state.get("last_demand", 0)
    last_requirement = state.get("last_requirement", "")

    logger.info(f"response.tool_calls: {response.tool_calls}")
    if len(response.tool_calls) > 0:
        try:
            for tool_call in response.tool_calls:
                if tool_call.get("name", "") == "vpp_trader":
                    logger.info(f"Tool call name: {tool_call['name']}")
                    if tool_call.get("args", {}).get("demand"):
                        demand = tool_call.get("args", {}).get("demand", 0)
                        if float(demand) > 0:
                            last_demand = demand
                    if tool_call.get("args", {}).get("hvac_max_temp"):
                        temperature = tool_call.get("args", {}).get("hvac_max_temp")
                    if tool_call.get("args", {}).get("requirement"):
                        requirement = tool_call.get("args", {}).get("requirement")
                        logger.info(f"requirement: {requirement}")
                        if requirement:
                            last_requirement = requirement
                    if tool_call.get("args", {}).get("user_modified_request"):
                        user_modified_request = tool_call.get("args", {}).get("user_modified_request")
                    goto = "planner"
                    logger.info(f"goto: {goto}")
                    break
                elif tool_call.get("name", "") == "curve_trader":
                    logger.info(f"Tool call name: {tool_call['name']}")
                    goto = "curve"
                    logger.info(f"goto: {goto}")
                    break
                elif tool_call.get("name", "") == "temp2power_trader":
                    logger.info(f"Tool call name: {tool_call['name']}")
                    if tool_call.get("args", {}).get("temp_max"):
                        temp2power = tool_call.get("args", {}).get("temp_max")
                    goto = "power"
                    logger.info(f"goto: {goto}")
                elif tool_call.get("name", "") == "power2temp_trader":
                    logger.info(f"Tool call name: {tool_call['name']}")
                    if tool_call.get("args", {}).get("power_adjust"):
                        power2temp = tool_call.get("args", {}).get("power_adjust")
                    goto = "temp"
                    logger.info(f"goto: {goto}")
                else:
                    goto = "__end__"
                    logger.info(f"goto: {goto}")
        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")
    else:
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."
        )
        logger.debug(f"Coordinator response: {response}")
        return Command(
            update={
                "messages": [AIMessage(content=response.content, name="coordinator",
                                       response_metadata={"finish_reason": "stop"}),
                             ],
            },
            goto="__end__",
        )
    if not user_modified_request:
        if requirement:
            last_requirement = requirement
        if not requirement and last_requirement:
            requirement = last_requirement
    if not requirement and not last_requirement:
        requirement = last_requirement = state.get("default_requirement", "综合考虑各因素，最大化电厂收益")
    logger.info(f"demand: {demand}, requirement: {requirement}, last_demand: {last_demand}, last_requirement: {last_requirement}, user_modified_request: {user_modified_request}")
    base_update = {
        "locale": locale,
        "research_topic": research_topic,
        "resources": configurable.resources,
        "temp2power": temp2power,
        "power2temp": power2temp,
        "temperature": temperature,
        "demand": demand,
        "requirement": requirement,
        "device_health_check": user_modified_request,
    }
    if last_demand > 0 or last_requirement:
        if last_demand > 0 and not last_requirement:
            base_update.update({
                "last_demand": last_demand,
            })
            logger.info(f"base_update1: {base_update}")
            return Command(
                update=base_update,
                goto=goto,
            )
        if last_demand < 0.1 and last_requirement:
            base_update.update({
                "last_requirement": last_requirement,
            })
            logger.info(f"base_update2: {base_update}")
            return Command(
                update=base_update,
                goto=goto,
            )
        if last_demand > 0 and last_requirement:
            base_update.update({
                "last_demand": last_demand,
                "last_requirement": last_requirement,
            })
            logger.info(f"base_update3: {base_update}")
            return Command(
                update=base_update,
                goto=goto,
            )
    else:
        logger.info(f"base_update: {base_update}")
        return Command(
            update=base_update,
            goto=goto,
        )


def reporter_node(state: State, config: RunnableConfig):
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")

    response_content = state.get("report_content", "")
    logger.info(f"reporter response: {response_content}")
    return Command(
        update={
            "messages": [AIMessage(content=response_content, name="reporter",
                                   response_metadata={"finish_reason": "stop"}),
                         ],
        },
        goto="__end__",
    )


def research_team_node(state: State):
    """Research team node that collaborates on tasks."""
    logger.info("Research team is collaborating on tasks.")
    pass


async def _execute_agent_step(
        state: State, agent, agent_name: str
) -> Command[Literal["__end__"]]:
    """Helper function to execute a step using the specified agent."""
    current_plan = state.get("current_plan")
    plan_title = current_plan.title
    observations = state.get("observations", [])

    # Find the first unexecuted step
    current_step = None
    completed_steps = []
    for step in current_plan.steps:
        if not step.execution_res:
            current_step = step
            break
        else:
            completed_steps.append(step)

    if not current_step:
        logger.warning("No unexecuted step found")
        return Command(goto="__end__")

    logger.info(f"Executing step: {current_step.title}, agent: {agent_name}")

    # Format completed steps information
    completed_steps_info = ""
    if completed_steps:
        completed_steps_info = "# Completed Research Steps\n\n"
        for i, step in enumerate(completed_steps):
            completed_steps_info += f"## Completed Step {i + 1}: {step.title}\n\n"
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"

    # Prepare the input for the agent with completed steps info
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"# Research Topic\n\n{plan_title}\n\n{completed_steps_info}# Current Step\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}\n\n## Locale\n\n{state.get('locale', 'en-US')}"
            )
        ]
    }

    # Add citation reminder for researcher agent
    if agent_name == "researcher":
        if state.get("resources"):
            resources_info = "**The user mentioned the following resource files:**\n\n"
            for resource in state.get("resources"):
                resources_info += f"- {resource.title} ({resource.description})\n"

            agent_input["messages"].append(
                HumanMessage(
                    content=resources_info
                            + "\n\n"
                            + "You MUST use the **local_search_tool** to retrieve the information from the resource files.",
                )
            )

        agent_input["messages"].append(
            HumanMessage(
                content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
                name="system",
            )
        )

    # Invoke the agent
    default_recursion_limit = 25
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
    result = await agent.ainvoke(
        input=agent_input, config={"recursion_limit": recursion_limit}
    )

    # Process the result
    response_content = result["messages"][-1].content
    logger.debug(f"{agent_name.capitalize()} full response: {response_content}")

    # Update the step with the execution result
    current_step.execution_res = response_content
    logger.info(f"Step '{current_step.title}' execution completed by {agent_name}")

    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=response_content,
                    name=agent_name,
                )
            ],
            "observations": observations + [response_content],
        },
        goto="__end__",
    )


async def _setup_and_execute_agent_step(
        state: State,
        config: RunnableConfig,
        agent_type: str,
        default_tools: list,
) -> Command[Literal["__end__"]]:
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
    configurable = Configuration.from_runnable_config(config)
    mcp_servers = {}
    enabled_tools = {}

    # Extract MCP server configuration for this agent type
    if configurable.mcp_settings:
        for server_name, server_config in configurable.mcp_settings["servers"].items():
            if (
                    server_config["enabled_tools"]
                    and agent_type in server_config["add_to_agents"]
            ):
                mcp_servers[server_name] = {
                    k: v
                    for k, v in server_config.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config["enabled_tools"]:
                    enabled_tools[tool_name] = server_name

    # Create and execute agent with MCP tools if available
    if mcp_servers:
        async with MultiServerMCPClient(mcp_servers) as client:
            loaded_tools = default_tools[:]
            for tool in client.get_tools():
                if tool.name in enabled_tools:
                    tool.description = (
                        f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                    )
                    loaded_tools.append(tool)
            agent = create_agent(agent_type, agent_type, loaded_tools, agent_type)
            return await _execute_agent_step(state, agent, agent_type)
    else:
        # Use default tools if no MCP servers are configured
        agent = create_agent(agent_type, agent_type, default_tools, agent_type)
        return await _execute_agent_step(state, agent, agent_type)


async def researcher_node(
        state: State, config: RunnableConfig
) -> Command[Literal["__end__"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")
    configurable = Configuration.from_runnable_config(config)
    tools = [get_web_search_tool(configurable.max_search_results), crawl_tool]
    retriever_tool = get_retriever_tool(state.get("resources", []))
    if retriever_tool:
        tools.insert(0, retriever_tool)
    logger.info(f"Researcher tools: {tools}")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "researcher",
        tools,
    )


async def coder_node(
        state: State, config: RunnableConfig
) -> Command[Literal["__end__"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")
    return await _setup_and_execute_agent_step(
        state,
        config,
        "coder",
        [python_repl_tool],
    )


async def _ppt_execute_agent_step(
        state: State, agent, agent_name: str
) -> Command[Literal["reporter"]]:
    """Helper function to execute a step using the specified agent."""
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])

    messages = state['messages']
    llm = get_llm_by_type(AGENT_LLM_MAP["planner"])
    response = llm.invoke(messages)
    response_content = response.content
    logger.info(f"{agent_name} full response: {response_content}")

    return Command(
        update={
            "messages": [AIMessage(content=response_content, name=agent_name,
                                   response_metadata={"finish_reason": "stop"})],
        },
        goto="reporter",
    )


async def ppt_node(
        state: State, config: RunnableConfig
) -> Command[Literal["reporter"]]:
    """PPT node that generates presentation content"""
    logger.info("PPT node is generating.")
    return await _ppt_execute_agent_step(
        state,
        "ppt_composer",
        "ppt_composer"
    )


async def _vpp_execute_agent_step(
        state: State, agent, agent_name: str
) -> Command[Literal["reporter"]]:
    """Helper function to execute a step using the specified agent."""
    logger.info("自定义VPP node is generating.")
    research_topic = state.get("research_topic")
    temperature = state.get("temperature", 30)
    demand = state.get("demand", 20)
    requirement = state.get("requirement")
    device_health_check = state.get("device_health_check", "")
    if device_health_check:
        last_demand = state.get("last_demand", 0)
        demand = last_demand if last_demand > 0 else demand
        requirement = ""
    # test_input = {"text": f"虚拟电厂VPP进行{demand}MW的削峰需求响应，该VPP下辖多个用户，每个用户下辖一个设备，分别对应暖通空调HVAC、华贝纳储能ESS_HBN、美力储能ESS_ML、环益储能ESS_HY、光伏站PV、充电桩EV，各设备可响应容量为[6.0, 8.2, 10.0, 7.0, 3.6, 2.2]；用户信用评分[3, 4, 4, 5, 2, 5]，信用评分范围1~5，值越大表示信用越好；用户可直控标识[1, 1, 1, 1, 0, 0]，1表示可直控，0表示不可直控；设备响应成本[0.1, 0.3, 0.04, 0.4, 0.15, 0.5]，单位：万元/MW，值越大表示参与需求响应成本越高。"
    #                       f"{requirement}，分解该VPP总响应量到各个设备参与本次需求响应，输出以上各设备分配方案。",
    #               "temperature": temperature,
    #               "device_health_check": device_health_check}
    text = f"""虚拟电厂VPP进行{demand}MW的削峰需求响应，该VPP下辖多个用户，每个用户下辖一个设备

|    | 设备名称          |   可响应容量(MW) |   用户信用评分(信用评分范围1~5，值越大表示信用越好) |   可直控标识(1表示可直控，0表示不可直控) |   响应成本(万元/MW)(值越大表示参与需求响应成本越高) |
|:---:|:---:|:---:|:---:|:---:|:---:|
|  0 | 暖通空调HVAC      |              6   |                                                   3 |                                        1 |                                                0.1  |
|  1 | 华贝纳储能ESS_HBN |              8.2 |                                                   4 |                                        1 |                                                0.3  |
|  2 | 美力储能ESS_ML    |             10   |                                                   4 |                                        1 |                                                0.04 |
|  3 | 环益储能ESS_HY    |              7   |                                                   5 |                                        1 |                                                0.4  |
|  4 | 光伏站PV          |              3.6 |                                                   2 |                                        0 |                                                0.15 |
|  5 | 充电桩EV          |              2.2 |                                                   5 |                                        0 |                                                0.5  |

{requirement}，分解该VPP总响应量到各个设备参与本次需求响应，输出以上各设备分配方案。
"""

    test_input = {"text": text,
                  "temperature": temperature,
                  "device_health_check": device_health_check}
    logger.info(f"【{agent_name}】test_input: {test_input}")
    result = await subgraph.ainvoke(test_input, config={"recursion_limit": 100})
    logger.info(f"subgraph result = {result}")

    markdown_table, plans_curve, report_content = get_vpp_alloc_plan(result)
    response_content = (
            markdown_table + "\n" + plans_curve
    )

    logger.info(f"【{agent_name}】 full response type: {type(response_content)}: {response_content}")
    return Command(
        update={
            "messages": [AIMessage(content=response_content, name=agent_name,
                                   response_metadata={"finish_reason": "stop"})],
            "report_content": report_content,
        },
        goto="reporter",
    )


async def vpp_node(
        state: State, config: RunnableConfig
) -> Command[Literal["reporter"]]:
    """Researcher node that do research"""
    logger.info("VPP node is generating.")
    return await _vpp_execute_agent_step(
        state,
        "vpp",
        "vpp"
    )
