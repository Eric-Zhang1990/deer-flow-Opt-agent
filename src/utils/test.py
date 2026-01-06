# import textwrap
# import re
#
# def smart_wrap_code(code: str, width: int = 80, indent: int = 4) -> str:
#     """
#     智能换行代码：超过 width 的行在空格或运算符处换行，不截断变量名
#     """
#     wrapped_lines = []
#     for line in code.splitlines():
#         if len(line) <= width:
#             wrapped_lines.append(line)
#         else:
#             # 优先在空格前换行，同时保持缩进
#             wrapped = textwrap.wrap(
#                 line,
#                 width=width,
#                 break_long_words=False,  # 不从单词中间断开
#                 break_on_hyphens=False,
#                 subsequent_indent=" " * indent
#             )
#             wrapped_lines.extend(wrapped)
#     return "\n".join(wrapped_lines)
#
#
# def code_dict_to_markdown2(code_dict: dict, width: int = 60) -> str:
#     """
#     将代码字典转换成 Markdown 格式，并对长行进行智能换行
#     """
#     imports = smart_wrap_code(code_dict.get("imports", ""), width=width)
#     code = smart_wrap_code(code_dict.get("code", ""), width=width)
#     return f"```python\n{imports}\n\n{code}\n```"
#
#
# def code_dict_to_markdown(code_data, remove_duplicate_imports=True):
#     """
#     将 code_data {'imports': str, 'code': str} 转为 Markdown 代码块字符串。
#     remove_duplicate_imports: 如果 True，会将 code 中开头重复的 import/from 行移除。
#     """
#     imports = code_data.get('imports', '') or ''
#     code = code_data.get('code', '') or ''
#
#     # 去除多余缩进并去首尾空白
#     imports = textwrap.dedent(imports).strip()
#     code = textwrap.dedent(code).rstrip()
#
#     if remove_duplicate_imports and imports:
#         # 将 imports 拆成若干行，方便比对
#         import_lines = [ln.strip() for ln in imports.splitlines() if ln.strip()]
#         code_lines = code.splitlines()
#
#         # 如果 code 开头有与 imports 相同的行，去掉它们（避免重复 import）
#         while code_lines and code_lines[0].strip() in import_lines:
#             code_lines.pop(0)
#         code = "\n".join(code_lines).lstrip()
#
#     # 构造 Markdown 代码块（确保 ```python 在行首，没有前导空格）
#     markdown = "```python\n"
#     if imports:
#         markdown += imports + "\n\n"
#     markdown += code + "\n"
#     markdown += "```"
#
#     return markdown
#
# # 示例调用（基于你提供的 show_code 中的 code_data）
# def show_code():
#     code_data = {
#         'imports': "import pyomo.environ as pyo\nimport numpy as np",
#         'code': 'def solve_demand_response():\n    # 定义设备名称\n    device_names = [\'HVAC\', \'ESS_HBN\', \'ESS_ML\', \'ESS_HY\', \'PV\', \'EV\']\n    # 定义各设备的可响应容量 (MW)\n    capacity = [0.15, 0.41, 0.5, 0.35, 0.18, 0.11]\n    # 定义用户信用评分作为优化的目标因子\n    credit = [3, 4, 4, 5, 2, 5]\n    # 定义总需求响应量 (MW)\n    total_demand = 1.0\n    # 设备数量\n    n = len(device_names)\n\n    # 创建一个具体的Pyomo模 型\n    model = pyo.ConcreteModel(name="DemandResponseAllocation")\n\n    # 定义决策变量x，表示分配给每个设备的响应量\n    # 变量是非负实数\n    model.x = pyo.Var(range(n), domain=pyo.NonNegativeReals)\n\n    # 定义目标函数\n    # 目标是最 大化信用加权的响应量总和\n    model.objective = pyo.Objective(\n        expr=sum(credit[i] * model.x[i] for i in range(n)),\n        sense=pyo.maximize\n    )\n\n    # 定义约束条件\n    # 1. 总量约束：所有设备分配的响应量之和必须等于总需求 响应量\n    model.total_demand_constraint = pyo.Constraint(\n        expr=sum(model.x[i] for i in range(n)) == total_demand\n    )\n\n    # 2. 容量约束：每个设备的分配量不能超过其最大可响应容量\n    # 使用ConstraintList来为每个设备添加一个 约束\n    model.capacity_constraints = pyo.ConstraintList()\n    for i in range(n):\n        model.capacity_constraints.add(model.x[i] <= capacity[i])\n\n    # 定义并配置求解器\n    # 指定SCIP求解器的可执行文件路径，使用r前缀避免转义问题\n    solver_path = r\'D:\\project\\github\\enn-deer-flow\\src\\graph_solver\\SCIPOptSuite 9.2.2\\bin\\scip.exe\'\n    solver = pyo.SolverFactory(\'scip\', executable=solver_path)\n\n    # 调用求解器求解模型\n    results = solver.solve(model, tee=False)\n\n    # 检查求解器状态并处理结果\n    if (results.solver.status == pyo.SolverStatus.ok) and (results.solver.termination_condition == pyo.TerminationCondition.optimal):\n        # 创建一个字典来存储结果\n        allocation_result = {}\n        for i in range(n):\n            # 使用pyo.value()获取变量的值\n            allocated_power = pyo.value(model.x[i])\n            allocation_result[device_names[i]] = round(allocated_power, 4)\n        return allocation_result\n    else:\n        # 如果求解失败，返回错误信息\n        return {\n            "error": "Solver failed",\n            "status": str(results.solver.status),\n            "termination_condition": str(results.solver.termination_condition)\n        }\n\n# 执行求解函数并打印结果\nallocation = solve_demand_response()\nprint(allocation)'
#     }
#
#     md = code_dict_to_markdown(code_data)
#     print(f"截断前： {md}")
#     md = code_dict_to_markdown2(code_data, width=60)
#     print(f"截断后： {md}")
#
# # show_code()
#
#
# import pandas as pd
#
# data = {
#     "设备名称": ["暖通空调HVAC", "华贝纳储能ESS_HBN", "美力储能ESS_ML", "环益储能ESS_HY", "光伏站PV", "充电桩EV"],
#     "可响应容量(MW)": [6.0, 8.2, 10.0, 7.0, 3.6, 2.2],
#     "用户信用评分": [3, 4, 4, 5, 2, 5],
#     "用户可直控标识": [1, 1, 1, 1, 0, 0],
#     "设备响应成本(万元/MW)": [0.1, 0.3, 0.04, 0.4, 0.15, 0.5]
# }
#
# df = pd.DataFrame(data)
#
# # 转成Markdown
# markdown_table = df.to_markdown(index=True)
# print(markdown_table)
#
# import pandas as pd
#
#
# def df_to_markdown_fstring(df, demand, requirement, intro_text=""):
#     # 生成基础 Markdown（含索引）
#     md_raw = df.to_markdown(index=True, tablefmt="github")
#
#     # 按行拆分
#     lines = md_raw.split("\n")
#     if len(lines) > 1:
#         # 表头列数
#         col_count = len(lines[0].split("|")) - 2  # 去掉首尾空白列
#         # 生成全居中的分隔行
#         align_line = "|" + "|".join([":---:" for _ in range(col_count)]) + "|"
#         # 替换第 2 行为居中对齐
#         lines[1] = align_line
#
#     markdown_table = "\n".join(lines)
#
#     # ==== 3. 拼接最终输出 ====
#     markdown_str = f"""虚拟电厂VPP进行demandMW的削峰需求响应，该VPP下辖多个用户，每个用户下辖一个设备
#
# {markdown_table}
#
# requirement，分解该VPP总响应量到各个设备参与本次需求响应，输出以上各设备分配方案。
# """
#     return markdown_str
#
#
# # ===== 测试数据 =====
# data = {
#     "设备名称": ["暖通空调HVAC", "华贝纳储能ESS_HBN", "美力储能ESS_ML", "环益储能ESS_HY", "光伏站PV", "充电桩EV"],
#     "可响应容量(MW)": [6.0, 8.2, 10.0, 7.0, 3.6, 2.2],
#     "用户信用评分(信用评分范围1~5，值越大表示信用越好)": [3, 4, 4, 5, 2, 5],
#     "可直控标识(1表示可直控，0表示不可直控)": [1, 1, 1, 1, 0, 0],
#     "响应成本(万元/MW)(值越大表示参与需求响应成本越高)": [0.1, 0.3, 0.04, 0.4, 0.15, 0.5]
# }
# df = pd.DataFrame(data)
#
# demand = 20
# requirement = "综合考虑各因素"
#
# md_output = df_to_markdown_fstring(df, demand, requirement)
# print(md_output)
#
#
# base_update = {
#         "locale": "locale",
#         "research_topic": "research_topic",
#         "resources": "configurable.resources",
#         "temp2power": "temp2power",
#         "power2temp": "power2temp",
#         "temperature": "temperature",
#         "demand": "demand",
#         "requirement": "requirement",
#         "device_health_check": "user_modified_request",
#     }
# print(base_update)
# base_update.update({
#                     "last_demand": "last_demand",
#                 })
# print(base_update)


import pyomo.environ as pyo

data = {
    "indices": [0, 1, 3, 4, 5],
    "capacity": {0: 6.0, 1: 8.2, 3: 7.0, 4: 3.6, 5: 2.2},
    "cost": {0: 0.10, 1: 0.30, 3: 0.40, 4: 0.15, 5: 0.50},
    "total_demand": 20.0
}

# 对成本数据进行归一化
epsilon = 0.01
cost_values = list(data["cost"].values())
min_cost = min(cost_values)
max_cost = max(cost_values)

normalized_cost = {}
# 检查max_cost和min_cost是否相等以避免除以
# 零
if (max_cost - min_cost) > 1e-9:
    for i in data["indices"]:
        normalized_cost[i] = epsilon + (1 - epsilon) * (data["cost"][i] - min_cost) / (max_cost - min_cost)
else:
    for i in data["indices"]:
        normalized_cost[i] = epsilon

normalized_data = {
    'cost': normalized_cost
}

# 创建一个具体的模型
model = pyo.ConcreteModel(name="DispatchOptimization")

# --- 定义集合 ---
# 定义设备索引集合
model.I = pyo.Set(initialize=data["indices"])

# --- 定义参数 ---
# 定义每个设备的最大容量
model.capacity = pyo.Param(model.I,
    initialize=data["capacity"],  doc="Maximum capacity of each device")
# 定义总需求
model.total_demand = pyo.Param(initialize=data["total_demand"],  doc="Total power demand to be met")
# 定义每个设备的归一化成本
model.norm_cost = pyo.Param(model.I, initialize=normalized_data['cost'],  doc="Normalized cost for each device")

# --- 定义变量 ---
# 定义每个设备的调度功率变量，并设置边界
def x_bounds(model, i):
    return (0, model.capacity[i])
model.x = pyo.Var(model.I,  domain=pyo.NonNegativeReals,
    bounds=x_bounds,  doc="Dispatched power from device i")

# --- 定义目标函数 ---
# 目标是最小化总的归一化调度成本
def objective_rule(model):
    return sum(model.norm_cost[i] * model.x[i] for i in
    model.I)
model.objective = pyo.Objective(rule=objective_rule,
    sense=pyo.minimize)

# --- 定义约束 ---
# 约束1: 所有设备的调度功率之和必须等于总需求
def demand_rule(model):
    return sum(model.x[i] for i in model.I) == model.total_demand
model.demand_constraint = pyo.Constraint(rule=demand_rule)

# 约束2: 设备0必须以其最大容量调度
def hvac_priority_rule(model):
    return model.x[0] == model.capacity[0]
model.hvac_priority_constraint = pyo.Constraint(rule=hvac_priority_rule)

# 约束3: 设备1必须以其最大容量调度
def ess_hbn_priority_rule(model):
    return model.x[1] == model.capacity[1]
model.ess_hbn_priority_constraint = pyo.Constraint(rule=ess_hbn_priority_rule)

# --- 求解模型 ---
# 指定求解器路径并创建求解器实例
solver_path = r"D:\project\github\enn-deer-flow\src\graph_solver\SCIPOptSuite 9.2.2\bin\scip.exe"
solver = pyo.SolverFactory('scip', executable=solver_path)

# 求解模型
results = solver.solve(model, tee=False)

# --- 打印结果 ---
# 检查求解状态并打印变量值
if (results.solver.status == pyo.SolverStatus.ok) and (results.solver.termination_condition == pyo.TerminationCondition.optimal):
    print("Optimal Solution Found:")
    for i in model.I:
        print(f"  Dispatch from device {i} (x_{i}): {pyo.value(model.x[i]): .2f} MW")
    print(f"Total Dispatch Cost (using normalized costs): {pyo.value(model.objective): .4f}")
elif (results.solver.termination_condition ==
    pyo.TerminationCondition.infeasible):
    print("Problem is Infeasible")
else:
    print("Solver Status:", results.solver.status)
    print("Termination Condition: ",
    results.solver.termination_condition)