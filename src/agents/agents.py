# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP


# Create agents using configured LLM types
# def create_agent(agent_name: str, agent_type: str, tools: list, prompt_template: str):
#     """Factory function to create agents with consistent configuration."""
#     return create_react_agent(
#         name=agent_name,
#         model=get_llm_by_type(AGENT_LLM_MAP[agent_type]),
#         tools=tools,
#         prompt=lambda state: apply_prompt_template(prompt_template, state),
#     )


class AgentWrapper:
    def __init__(self, agent, tools):
        self._agent = agent
        self._tools = tools

    @property
    def tools(self):
        """Return the list of bound tools."""
        return self._tools

    async def ainvoke(self, *args, **kwargs):
        """Proxy async invoke to the wrapped agent."""
        return await self._agent.ainvoke(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        """Proxy sync invoke to the wrapped agent (if needed)."""
        return self._agent.invoke(*args, **kwargs)

    def __getattr__(self, attr):
        """Proxy other attribute access to the wrapped agent."""
        return getattr(self._agent, attr)


def create_agent(agent_name: str, agent_type: str, tools: list, prompt_template: str):
    """Factory to create an agent and wrap it with tools accessor."""
    agent = create_react_agent(
        name=agent_name,
        model=get_llm_by_type(AGENT_LLM_MAP[agent_type]),
        tools=tools,
        prompt=lambda state: apply_prompt_template(prompt_template, state),
    )
    return AgentWrapper(agent, tools)
