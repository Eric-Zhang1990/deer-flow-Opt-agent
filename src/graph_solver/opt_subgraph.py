from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict
from src.graph_solver.opt_nodes import translator_node, formulator_node, coder_node, solver_node, interpreter_node, \
    plan_node, hvac_adjust_node, retry_manager_node, interpretation_validator_node, baseline_node, preprocess_node


class WorkflowState(TypedDict):
    text: str
    device_health_check: str
    translated: str
    formulation: dict
    code_output: dict
    solution: dict
    interpretation: dict
    baselines: list[dict]
    plans: list[dict]  # 历史所有计划列表
    adjusted_translated: str
    hvac_delta: float
    temperature: float
    solver_error_info: str  # 保存 solver 报错信息
    retry: bool
    retry_count: int  # 新增重试计数
    valid: bool
    reason: str


translator_runnable = RunnableLambda(translator_node)
hvac_adjust_runnable = RunnableLambda(hvac_adjust_node)
formulator_runnable = RunnableLambda(formulator_node)
coder_runnable = RunnableLambda(coder_node)
solver_runnable = RunnableLambda(solver_node)
interpreter_runnable = RunnableLambda(interpreter_node)
validator_runnable = RunnableLambda(interpretation_validator_node)
retry_manager_runnable = RunnableLambda(retry_manager_node)
plan_runnable = RunnableLambda(plan_node)
baseline_runnable = RunnableLambda(baseline_node)
preprocess_runnable = RunnableLambda(preprocess_node)


workflow = StateGraph(state_schema=WorkflowState)

# 添加节点
workflow.add_node("preprocess_node", preprocess_runnable)
workflow.add_node("translator_node", translator_runnable)
workflow.add_node("hvac_adjust_node", hvac_adjust_runnable)
workflow.add_node("formulator_node", formulator_runnable)
workflow.add_node("coder_node", coder_runnable)
workflow.add_node("solver_node", solver_runnable)
workflow.add_node("interpreter_node", interpreter_runnable)
workflow.add_node("interpretation_validator_node", RunnableLambda(interpretation_validator_node))
workflow.add_node("retry_manager_node", retry_manager_runnable)
workflow.add_node("plan_node", plan_runnable)
workflow.add_node("baseline_node", baseline_node)

# 定义数据流
workflow.add_edge("preprocess_node", "translator_node")
workflow.add_edge("translator_node", "hvac_adjust_node")
workflow.add_edge("hvac_adjust_node", "formulator_node")
workflow.add_edge("formulator_node", "coder_node")
workflow.add_edge("coder_node", "solver_node")
workflow.add_edge("solver_node", "interpreter_node")
workflow.add_edge("interpreter_node", "interpretation_validator_node")
workflow.add_edge("interpretation_validator_node", "retry_manager_node")


def route_after_retry_manager(state: WorkflowState):
    if state.get("retry"):
        return "reflection"
    return "plan"


workflow.add_conditional_edges(
    "retry_manager_node",
    route_after_retry_manager,
    {
        "reflection": "coder_node",
        "plan": "baseline_node"
    }
)

workflow.add_edge("baseline_node", "plan_node")

workflow.add_edge("plan_node", END)

workflow.set_entry_point("preprocess_node")

subgraph = workflow.compile()

# mermaid_code = subgraph.get_graph().draw_mermaid()
# print(mermaid_code)

# 测试
if __name__ == "__main__":
    import time
    t1 = time.time()
    test_input = {
        'text': '虚拟电厂VPP进行20MW的削峰需求响应，该VPP下辖多个用户，每个用户下辖一个设备，分别对应暖通空调HVAC、华贝纳储能ESS_HBN、美力储能ESS_ML、环益储能ESS_HY、光伏站PV、 充电桩EV，各设备可响应容量为[6.0, 8.2, 10.0, 7.0, 3.6, 2.2]；用户信用评分[3, 4, 4, 5, 2, 5]，信用评分范围1~5，值越大表示信用越好；用户可直控标识[1, 1, 1, 1, 0, 0]，1表示可直控，0表示不可直控；设备响应成本[0.1, 0.3, 0.04, 0.4, 0.15, 0.5]，单位：万元/MW，值越大表示参与需求响应成本越高。信用评级优先，分解该VPP总响应量到各个设备参与本次需求响应，输出以上各设备分配方案。',
        'temperature': 28,
        'device_health_check': '以暖通和华贝纳储能收益最大优先, 美力储能损坏不可用'}
    result = subgraph.invoke(test_input, config={"recursion_limit": 100})
    t2 = time.time()
    print(result)
    print(f'耗时：{round(t2-t1, 2)}')
    # # 保存到本地JSON文件
    # with open("result.json", "w", encoding="utf-8") as f:
    #     # 假设 result 是 dict 或支持转换成 JSON 的结构
    #     json.dump(result, f, ensure_ascii=False, indent=4)
