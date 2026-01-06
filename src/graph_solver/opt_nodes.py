from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import io
import pandas as pd
import numpy as np
import copy
from contextlib import redirect_stdout
import os
from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP
from langgraph.config import get_stream_writer
import textwrap
from uuid import uuid4
import re

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
csv_path = os.path.join(script_dir, 'combined_15min_data.csv')

llm = get_llm_by_type(AGENT_LLM_MAP["planner"])

local_solver_path = os.getenv("local_solver_path")
csv_path = os.path.join(script_dir, 'combined_15min_data.csv')
MaxRetryCount = 2
device_name_map = {'HVAC': '暖通', 'ESS_HBN': '华贝纳储能', 'ESS_ML': '美力储能', 'ESS_HY': '环益储能', 'EV': '充电桩', 'PV': '光伏'}


# preprocess_prompt = ChatPromptTemplate.from_messages([
#     ("system", """
# 你是一个电力需求响应调度优化的文本预处理专家。你的任务是根据给定的“特殊说明”（extra_instructions），对输入的中文调度描述文本进行信息删除、修改或优先化处理，使其满足后续调度/建模计算要求。
#
# 处理规则（严格执行）：
# 1. 如果特殊说明中指出某设备或用户“故障”“不参与”“剔除”等，则从文本中删除对应设备/用户的所有描述（包括容量、信用评分、可直控标识、响应成本等信息），删除后不得在文本中留下任何该设备的数值或断章片段。
# 2. 如果特殊说明中要求“优先/优先考虑/合约即将到期/重要接待”等，则对该设备/用户：
#    - 信用评分设为 5（范围 1~5，取最大值）。
#    - 可直控标识设为 1。
#    - 设备响应成本设为 0（万元/MW）。
#    - 保留其原有容量信息。
# 3. 不涉及的内容保持原样，不要随意增删其他设备或数值。
# 4. 如果提示信息不涉及到文本中的任何设备或用户，则保持原有描述不变。
# 5. 输出要求：**仅返回修改后的完整中文描述文本**，不得输出任何变更原因、诊断信息或额外注释。
#
# 输入格式：
# 原始文本：{text}
# 特殊说明：{extra_instructions}
# """),
#     ("human", "原始文本：{text}\n\n特殊说明：{extra_instructions}")
# ])


# preprocess_prompt = ChatPromptTemplate.from_messages([
#     ("system", """
# 你是一个电力需求响应调度优化的文本预处理专家。你的任务是根据给定的“特殊说明”（extra_instructions），对输入的中文调度描述文本进行信息删除、修改或优先化处理，使其满足后续调度/建模计算要求。
#
# 处理规则（严格执行）：
# 1. 如果特殊说明中指出某设备或用户“故障”“不参与”“剔除”等，则从文本中删除对应设备/用户的所有描述（包括容量、信用评分、可直控标识、响应成本等信息），删除后不得在文本中留下任何该设备的数值或断章片段。
# 2. 不涉及的内容保持原样，不要随意增删其他设备或数值。
# 3. 如果提示信息不涉及到文本中的任何设备或用户，则保持原有描述不变。
# 4. 输出要求：**仅返回修改后的完整中文描述文本**，不得输出任何变更原因、诊断信息或额外注释。
#
# 输入格式：
# 原始文本：{text}
# 特殊说明：{extra_instructions}
# """),
#     ("human", "原始文本：{text}\n\n特殊说明：{extra_instructions}")
# ])

preprocess_prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是一个电力需求响应调度优化的文本预处理专家。你的任务是根据给定的“特殊说明”（extra_instructions），对输入的中文调度描述文本进行信息删除、修改或优先化处理，使其满足后续调度/建模计算要求。

处理规则（严格执行）：
1. 只有当特殊说明中**明确**出现以下类型的删除性指令时，才删除对应设备/用户的全部描述：
   - 包含关键词：删除、移除、剔除、踢掉、不参与需求响应、不参与响应、不参与调度、设备损坏、设备故障、设备不可用、停止使用
   - 或等价表述，且明确指向某设备或用户
   在删除时，需要移除该设备/用户的所有描述（包括容量、信用评分、可直控标识、响应成本等），删除后不得在文本中留下该设备的数值或残留片段。
2. 如果仅涉及运行状态调整（如末端温度设定、响应值调整、功率限制、优先级变化等），不应视为删除性指令，应保留该设备/用户的信息。
3. 不涉及的内容保持原样，不要随意增删其他设备或数值。
4. 如果提示信息不涉及到文本中的任何设备或用户，则保持原有描述不变。
5. 输出要求：**仅返回修改后的完整中文描述文本**，不得输出任何变更原因、诊断信息或额外注释。

输入格式：
原始文本：{text}
特殊说明：{extra_instructions}
"""),
    ("human", "原始文本：{text}\n\n特殊说明：{extra_instructions}")
])


translator_prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是一名运筹优化技术问题的写作优化助手。你的任务是：
- 如果输入是中文，输出保持中文，必要时优化语句，使其更清晰、更专业，但不能改变含义。
- 不进行跨语言翻译。
- 技术术语保持准确（如HVAC、ESS、Pyomo等不能翻译）。
- 不添加任何额外解释，只输出优化后的文本。
- 注意，暖通温度相关的因素已经在前置环节进行过处理，这里必须要忽略！
"""),
    ("human", "问题描述：{problem_description} 要求：{requirement}")
])

adjust_capacity_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an assistant that edits numerical lists based on instructions.
The input text describes devices and their capacities. The devices are listed in a fixed order in the text.
Your task:
- Identify the device 'HVAC' in the description.
- Find the position of HVAC in the capacity list.
- Subtract the given delta from its capacity value.
- Keep the text exactly the same, except update that single number.
- Do not change any other numbers or text.

Return only the modified text.
"""),
    ("human", """
Original text:
{translated_text}

Delta (MW): {delta}
""")
])

formulator_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an operations research expert. Your task is to translate the given natural language description into a formal optimization formulation.

Follow these instructions carefully:
1. Identify all decision variables and assign clear names and descriptions.
2. Determine the objective function (maximize or minimize) and write it using standard mathematical notation.
   - If the natural language description does not clearly specify an optimization goal (such as "cost priority", "credit priority", or "consider all factors"), assume the default objective is "maximize benefit" (收益最优).
3. List all constraints explicitly, including bounds on variables.
4. Extract all numeric data from the description and organize them into a structured JSON inside "notes".
   - Include arrays for parameters like capacity, credit, direct control, cost, or any other constants mentioned.
   - Do NOT output code in "notes".
5. Add a new field called "device_names" containing an ordered list of the actual device names mentioned in the description.
   - Device names MUST come only from this fixed set: ["HVAC", "ESS_HBN", "ESS_ML", "ESS_HY", "PV", "EV"].
   - Do NOT create new names.
   - Maintain the order in which these names appear in the description.
6. Add a new field called "response_cost" containing an ordered list of the response cost values for each device, maintaining the same order as device_names.
7. Add a new field called "credit_scores" containing an ordered list of the credit values for each device, maintaining the same order as device_names.
8. Add a new field called "response_capacity" containing an ordered list of the response capacity values for each device, maintaining the same order as device_names.  
   - Response capacity refers to the maximum controllable or dispatchable capacity of each device.  
   - Ensure the values correspond exactly in order to device_names.
9. If weights are not provided, default all weights to 1.0 and mention this assumption in notes.
10. If any information is missing, make reasonable assumptions and document them in "notes".
   - If the optimization goal was not provided in the description, note in "assumptions" that the default objective "maximize benefit" (收益最优) was applied.
11. Output MUST follow this JSON structure:

{{
  "variables": [
    {{"name": "x_i", "description": "Amount of resource allocated to user i", "domain": "x_i >= 0"}}
  ],
  "objective": {{
    "type": "maximize",
    "expression": "sum_{{i}} (w1*credit_i + w2*direct_i - w3*cost_i) * x_i"
  }},
  "constraints": [
    "sum_{{i}} x_i = TotalDemand",
    "0 <= x_i <= capacity_i"
  ],
  "notes": {{
    "response_capacity": [100, 200, 300],
    "credit": [0.9, 0.8, 0.95],
    "direct_control": [1, 0, 1],
    "cost": [10, 20, 15],
    "weights": [1.0, 1.0, 1.0],
    "TotalDemand": 600,
    "assumptions": "Weights defaulted to 1.0 since not explicitly provided."
  }},
  "device_names": ["HVAC", "ESS_HBN", "ESS_ML", "ESS_HY", "PV", "EV"],
  "credit_scores": [0.9, 0.8, 0.95],
  "response_cost": [10, 20, 15],
  "response_capacity": [120, 180, 250]
}}

# Natural language description:
{problem_description}

"""),
    ("human", "{problem_description}")
])

coder_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert in mathematical programming and Python coding. You will receive an optimization formulation as a structured Python dict. Generate executable Python code using Pyomo following these rules:

Follow these rules:
1. **Import rules**
   - All import statements MUST appear ONLY in the "imports" field.
   - The "code" field MUST NOT contain any import statements.
   - Import only the packages that are strictly required by the code.
2. Create a Pyomo ConcreteModel.
3. Define sets, parameters, and decision variables based on "variables" in Dict
   - Use 0-based indices for Pyomo sets so they align with Python lists.
4. When using indices in Pyomo sets, always use the loop variable (i), not a string key.
5. Define the objective function as per "objective", but apply the following preprocessing:
    - Apply min-max normalization for each factor across all devices.
    - To avoid zero weights, add a small positive offset ε = 0.01:
      normalized_value = ε + (1 - ε) * (value - min(values)) / (max(values) - min(values))
   - Store normalized arrays in a dict named `normalized_data` for clarity.
   - The objective must use normalized factors and their weights.
6. Add all constraints listed in "constraints".
7. Include solver selection and execution using the solver path provided: {solver_path} (use SCIP solver).
8. Print the solution values of all decision variables.
9. The "notes" field is descriptive. 
   - You may EXTRACT numeric values or clearly defined constants from notes to initialize parameters.
   - DO NOT use `notes` as a variable in code.
   - DO NOT use `eval(notes)` or similar dynamic parsing.
   - Instead, create explicit Python structures (e.g., lists or dicts) with extracted numeric values.
10. If you create a data dictionary (e.g., from notes), 
    it must be defined BEFORE it is referenced in parameter initialization.
    - Always define any required data structures at the top of the code BEFORE using them.
    - Always define `data` BEFORE creating Pyomo Params.
    - Ensure that the order of code prevents NameError.
    - Extract numeric arrays from the "notes" field and define them as a Python dict named `data` at the top of the code.
       Example:
       data = {{
           "capacity": [...],
           "credit": [...],
           "direct_control": [...],
           "cost": [...],
           "TotalDemand": ...
       }}
11. If no explicit values are provided, default all weights to 1.0
12. Always define the solver path using a raw string literal with prefix r to avoid backslash escaping issues, e.g., solver_path = r"D:\path\to\solver.exe"
13. Output the code in JSON format with keys: "prefix" (explanation), "imports" (import statements), "code" (Python code excluding imports).
14. Always retrieve variable values using `pyo.value(model.x[i])` or `model.x[i]()` WITHOUT `.value` to avoid AttributeError.
15. **Avoid Pyomo warnings about replacing components**:
   - Use unique names for constraints and avoid reassigning the same name for different components.
   - Use `ConstraintList()` for multiple constraints and name it `capacity_constraints`.

If there was a previous solver error, here is the error message:
{solver_error_info}

→ If solver_error_info is not empty, adjust the code to fix likely causes (e.g., missing data, misaligned dimensions, infeasible constraints, wrong variable domain, etc.).

Input Dict:
{formulation_dict}

Output format:
{{
  "prefix": "使用中文详细解释代码逻辑，描述每一步代码的作用，不翻译代码。",
  "imports": "import pyomo.environ as pyo\n...",
  "code": "model = pyo.ConcreteModel()\n..."
}}
严格要求：
1. "prefix" 字段必须使用中文详细解释代码逻辑，描述主要步骤及作用。
2. "imports" 和 "code" 字段中的 **代码保持英文**，但**代码注释必须是中文**。
3. 输出 JSON 格式必须严格符合示例结构，字段名保持英文。
"""),
    ("human", "Here is the formulation Dict:\n{formulation_dict}")
])

interpreter_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that converts raw optimization solver output into structured JSON.

The raw text contains:
- Solver logs (including solver status, termination condition, and messages)
- Variable results in the format: x[i] = value

Your task:
1. Determine solver status and map it to one of:
   - "optimal" (if solver reports optimal solution found)
   - "feasible" (if solver found a feasible but not optimal solution)
   - "infeasible" (if solver reports infeasible)
   - "error" (if execution or solver crash)
   - "warning" (if solver warns but provides partial solution)
   - "unknown" (if cannot infer)
2. Extract all decision variables and replace x[i] with the corresponding {device_names} (order matters).
   - **Always match decision variables from the solver output to devices in {device_names} using their index information, and ensure the mapping is correct.**
   - **If a device is missing in the solver output, still include it with value 0.0.**
3. If solver indicates infeasible, error, or no solution, still return a valid JSON structure but set:
   - "status": "infeasible" or "error"
   - "variables": [] (empty list)
4. Return JSON:
{{
  "status": "...",
  "variables": [{{"name": "<device_name>", "value": <float>}}, ...],
  "interpretation": "中文简洁描述下分配情况，例如：已生成需求响应分配方案，分配如下：HVAC **兆瓦，ESS_HBN **兆瓦，ESS_ML **兆瓦，ESS_HY **兆瓦，PV **兆瓦，EV **兆瓦。"
}}
"""),
    ("human", "device_names: {device_names}\n\nText:\n{solution}")
])


interpretation_validator_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a validation agent that checks whether an optimization result is valid.

Inputs:
- solver_error_info: May contain error message from code execution or solver.
- interpretation: A JSON with fields: status, objective_value, variables.

Validation logic:
1. If solver_error_info contains syntax errors, name errors, or execution errors → invalid.
2. If interpretation.status is not "optimal" or "feasible" → invalid.
3. If objective_value is missing or 0 AND variables are empty or all zero → invalid.
Otherwise, valid=True.

Return JSON:
{{
  "valid": true or false,
  "reason": "用中文简要说明原因"
}}
"""),
    ("human", "solver_error_info: {solver_error_info}\n\ninterpretation: {interpretation}")
])


class Variable(BaseModel):
    name: str
    domain: str
    description: str


class Objective(BaseModel):
    type: str  # "maximize" or "minimize"
    expression: str
    description: str


class Formulation(BaseModel):
    variables: list[Variable]
    objective: Objective
    constraints: list[str]
    notes: str
    device_names: list[str]
    response_cost: list[float]
    credit_scores: list[float]
    response_capacity: list[float]


class CodeOutput(BaseModel):
    prefix: str = Field(description="Description of the code logic")
    imports: str = Field(description="Import statements for the code")
    code: str = Field(description="Python code excluding imports")


class SolverOutput(BaseModel):
    raw_output: str = Field(description="Raw console output from executing the optimization code")


class VariableItem(BaseModel):
    name: str
    value: float


class OptimizationResult(BaseModel):
    status: str = Field(..., description="Solver status, e.g., 'optimal', 'infeasible', 'error'")
    variables: list[VariableItem] = Field(default_factory=list, description="List of variables and their values")
    interpretation: str = Field(..., description="Short explanation for non-technical person in Chinese")


class InterpretationValidationResult(BaseModel):
    valid: bool = Field(..., description="True if result is valid and no retry needed")
    reason: str = Field(..., description="Explanation why valid or invalid")


preprocess_chain = preprocess_prompt | llm
translator_chain = translator_prompt | llm
formulator_chain = formulator_prompt | llm.with_structured_output(Formulation)
coder_chain = coder_prompt | llm.with_structured_output(CodeOutput)
interpreter_chain = interpreter_prompt | llm.with_structured_output(OptimizationResult)
interpretation_validator_chain = interpretation_validator_prompt | llm.with_structured_output(InterpretationValidationResult)


def preprocess_node(inputs: dict) -> dict:
    """
    输入: {"text": "...", "extra_instructions": "..."}
    输出: {"text": "<修改后文本>"} (覆盖原 text)
    """
    text = inputs.get("text", "")
    extra = inputs.get("device_health_check", "")
    try:
        result = preprocess_chain.invoke({"text": text, "extra_instructions": extra})
        modified_text = result.content.strip() if hasattr(result, "content") else str(result).strip()
        print(f"经预处理后，输入模型文本：\n{modified_text}\n")
        return {"text": modified_text}
    except Exception as e:
        print(f'preprocess_error is {str(e)}')
        return {"text": text}


def translator_node(inputs: dict) -> dict:
    """
    LangGraph 节点，输入 {text: "..."}，输出 {"translated": "..."}
    """
    problem_description = inputs.get("text", "")
    requirement = inputs.get("device_health_check", "")
    writer = get_stream_writer()
    markdown_text = (
        "#### 新奥泛能网虚拟电厂需求侧响应分配与调度计划生成\n"
        "- [🟡] 需求转译 — 将用户需求转译成运筹优化可理解的描述方式\n"
        "- [ ] 结构化处理 — 将需求转化为结构化数据\n"
        "- [ ] 代码生成 — 根据转译后的需求生成优化模型能力代码\n"
        "- [ ] 任务求解 — 执行优化求解代码，得到调度与分配结果\n"
        "- [ ] 结果解释 — 将求解结果转化为结构化的中文解释与可读输出\n"
        "- [ ] Reflection 自我修正 — 根据执行结果对模型生成的代码进行自动修正\n"
        "- [ ] 调度计划生成 — 基于求解结果和基线数据，生成最终的调度与分配计划\n"
    )
    writer({f"custom_text{str(uuid4())}": markdown_text})
    result = translator_chain.invoke({"problem_description": problem_description, "requirement": requirement})
    markdown_text = (
        "#### 新奥泛能网虚拟电厂需求侧响应分配与调度计划生成\n"
        "- [✔] 需求转译 — 将用户需求转译成运筹优化可理解的描述方式\n"
        "- [🟡] 结构化处理 — 将需求转化为结构化数据\n"
        "- [ ] 代码生成 — 根据转译后的需求生成优化模型能力代码\n"
        "- [ ] 任务求解 — 执行优化求解代码，得到调度与分配结果\n"
        "- [ ] 结果解释 — 将求解结果转化为结构化的中文解释与可读输出\n"
        "- [ ] Reflection 自我修正 — 根据执行结果对模型生成的代码进行自动修正\n"
        "- [ ] 调度计划生成 — 基于求解结果和基线数据，生成最终的调度与分配计划\n"
    )
    writer({f"custom_text{str(uuid4())}": markdown_text})
    return {"translated": result.content}


def hvac_adjust_node(state: dict) -> dict:
    temperature = state.get("temperature", 30)
    translated_text = state.get("translated", "")

    # 计算 delta
    delta = compute_delta(temperature=temperature)

    if delta == 0:
        adjusted_text = translated_text
    else:
        messages = adjust_capacity_prompt.format_messages(
            translated_text=translated_text,
            delta=delta
        )
        response = llm.invoke(messages)
        adjusted_text = response.content

    return {
        **state,
        "temperature": temperature,
        "adjusted_translated": adjusted_text,
        "hvac_delta": delta
    }


def formulator_node(inputs: dict) -> dict:
    translated_text = inputs.get("adjusted_translated", "")
    requirement = inputs.get("device_health_check", "")
    writer = get_stream_writer()
    result = formulator_chain.invoke({"problem_description": translated_text})
    result = result.dict()
    device_names_en = result.get('device_names', [])
    result['device_names_cn'] = device_names_en
    if device_names_en:
        result['device_names_cn'] = [device_name_map[name] for name in device_names_en]
    markdown_text = (
        "#### 新奥泛能网虚拟电厂需求侧响应分配与调度计划生成\n"
        "- [✔] 需求转译 — 将用户需求转译成运筹优化可理解的描述方式\n"
        "- [✔] 结构化处理 — 将需求转化为结构化数据\n"
        "- [🟡] 代码生成 — 根据转译后的需求生成优化模型能力代码\n"
        "- [ ] 任务求解 — 执行优化求解代码，得到调度与分配结果\n"
        "- [ ] Reflection 自我修正 — 根据执行结果对模型生成的代码进行自动修正\n"
        "- [ ] 结果解释 — 将求解结果转化为结构化的中文解释与可读输出\n"
        "- [ ] 调度计划生成 — 基于求解结果和基线数据，生成最终的调度与分配计划\n"
    )
    writer({f"custom_text{str(uuid4())}": markdown_text})
    return {"formulation": result}


def smart_wrap_code(code: str, width: int = 60, indent: int = 4) -> str:
    """
    智能换行代码：
    - 英文变量名不截断
    - 中文注释整句换行（不拆成单字）
    - 长字符串在逗号、冒号等符号后优先换行
    """
    wrapped_lines = []
    for line in code.splitlines():
        # 中文注释处理
        if line.strip().startswith("#"):
            if len(line) <= width // 2:
                wrapped_lines.append(line)
                continue
            prefix = re.match(r"(\s*#\s*)", line).group(1)
            text = line[len(prefix):]
            wrapped = textwrap.wrap(
                text,
                width=width // 2 - len(prefix),
                break_long_words=True,   # 允许截断长连续文本（中文）
                break_on_hyphens=False
            )
            wrapped_lines.extend([prefix + w for w in wrapped])
        else:
            if len(line) <= width:
                wrapped_lines.append(line)
                continue
            # 普通代码：避免变量被截断
            line_mod = re.sub(r'([,:])', r'\1 ', line)
            wrapped = textwrap.wrap(
                line_mod,
                width=width,
                break_long_words=False,
                break_on_hyphens=False,
                subsequent_indent=" " * indent
            )
            wrapped_lines.extend(wrapped)

    return "\n".join(wrapped_lines)


def show_code(code_dict: dict, width: int = 60) -> str:
    """
    将代码字典转换成 Markdown 格式，并对长行进行智能换行
    """
    imports = smart_wrap_code(code_dict.get("imports", ""), width=width)
    code = smart_wrap_code(code_dict.get("code", ""), width=width)
    return f"```python\n{imports}\n\n{code}\n```"


def coder_node(inputs: dict) -> dict:
    formulation = inputs.get("formulation", {})
    solver_error_info = inputs.get("solver_error_info", "")
    writer = get_stream_writer()
    result = coder_chain.invoke({
        "formulation_dict": formulation,
        "solver_path": local_solver_path,
        "solver_error_info": solver_error_info})
    markdown_text = (
        "#### 新奥泛能网虚拟电厂需求侧响应分配与调度计划生成\n"
        "- [✔] 需求转译 — 将用户需求转译成运筹优化可理解的描述方式\n"
        "- [✔] 结构化处理 — 将需求转化为结构化数据\n"
        "- [✔] 代码生成 — 根据转译后的需求生成优化模型能力代码\n"
        "- [🟡] 任务求解 — 执行优化求解代码，得到调度与分配结果\n"
        "- [ ] 结果解释 — 将求解结果转化为结构化的中文解释与可读输出\n"
        "- [ ] Reflection 自我修正 — 根据执行结果对模型生成的代码进行自动修正\n"
        "- [ ] 调度计划生成 — 基于求解结果和基线数据，生成最终的调度与分配计划\n"
    )
    writer({f"custom_text{str(uuid4())}": markdown_text})
    markdown_code = show_code(result.dict())
    writer({f"custom_text{str(uuid4())}": markdown_code})
    return {"code_output": result.dict()}


def solver_node(inputs: dict) -> dict:
    code_output = inputs.get("code_output", {})
    imports = code_output.get("imports", "")
    code = code_output.get("code", "")

    writer = get_stream_writer()

    # print(imports + "\n" + code)

    f = io.StringIO()
    context = {"__builtins__": __builtins__}  # 确保 Python 内置可用
    try:
        with redirect_stdout(f):
            exec(imports + "\n" + code, context, context)
        raw_out = f.getvalue()
        result = SolverOutput(raw_output=raw_out)
        markdown_text = (
            "#### 新奥泛能网虚拟电厂需求侧响应分配与调度计划生成\n"
            "- [✔] 需求转译 — 将用户需求转译成运筹优化可理解的描述方式\n"
            "- [✔] 结构化处理 — 将需求转化为结构化数据\n"
            "- [✔] 代码生成 — 根据转译后的需求生成优化模型能力代码\n"
            "- [✔] 任务求解 — 执行优化求解代码，得到调度与分配结果\n"
            "- [🟡] 结果解释 — 将求解结果转化为结构化的中文解释与可读输出\n"
            "- [ ] Reflection 自我修正 — 根据执行结果对模型生成的代码进行自动修正\n"
            "- [ ] 调度计划生成 — 基于求解结果和基线数据，生成最终的调度与分配计划\n"
        )
        writer({f"custom_text{str(uuid4())}": markdown_text})
        return {"solution": result.dict(), "solver_error_info": ""}
    except Exception as e:
        error_message = str(e)
        raw_out = f.getvalue()
        return {
            "solution": {"raw_output": f"Execution error: {error_message}\n{raw_out}"},
            "solver_error_info": error_message
        }


def interpreter_node(inputs: dict) -> dict:
    solution_text = inputs.get("solution", {}).get("raw_output", "")
    device_names = inputs.get("formulation", {}).get("device_names", [])

    try:
        result = interpreter_chain.invoke({
            "solution": solution_text,
            "device_names": device_names
        })
        parsed = result.dict()
        response_allocation = []
        variables = parsed.get("variables", [])
        if variables:
            response_allocation = [{"name": device_name_map[ele["name"]], "value": ele["value"]} for ele in variables]
        return {
            "interpretation": {
                "status": parsed.get("status", "unknown"),
                "variables": variables,
                "response_allocation": response_allocation,
                "interpretation": parsed.get("interpretation", "No interpretation provided")
            }
        }
    except Exception as e:
        return {
            "interpretation": {
                "status": "error",
                "variables": [],
                "response_allocation": [],
                "interpretation": f"Error during interpretation: {e}"
            }
        }


def generate_dr_plan(
        response_alloc: dict,
        response_cost: dict,
        start_time: str = "16:00:00",
        end_time: str = "17:00:00",
        sampling_frequency: float = 0.25,
        response_price: float = 3.0
):
    if not response_cost: response_cost = {k: 0 for k, v in response_alloc.items()}
    # （此处略，使用你之前的完整generate_dr_plan函数实现）
    rated_power = {'ESS_HBN': 1200, 'ESS_HY': 1500, 'ESS_ML': 1300}
    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'])
    full_data = df.copy()
    mask = (df['time'].dt.strftime("%H:%M:%S") >= start_time) & (df['time'].dt.strftime("%H:%M:%S") < end_time)
    response_window = df.loc[mask].copy()
    intervals = len(response_window)

    ori_response_alloc = copy.deepcopy(response_alloc)
    # 单位MW --> KW
    response_alloc = {k: v * 1000 * intervals for k, v in response_alloc.items()}

    json_plan = {"VPP_Response_Plan": []}

    for device, alloc in response_alloc.items():
        baseline_dict = {
            "time": [t.strftime("%H:%M:%S") for t in df['time']],
            "value": [float(round(v, 2)) for v in df[device].tolist()]  # ✅ 转为 float
        }
        new_values_full = df[device].tolist()
        if device == "PV":
            pass
        elif device == "EV":
            if alloc > 0:
                for i in response_window.index:
                    new_values_full[i] = 0.0
        elif device == "HVAC":
            reduce_each = alloc / intervals
            for i in response_window.index:
                new_values_full[i] = max(0, df.loc[i, device] - reduce_each)
        elif device in ["ESS_HBN", "ESS_HY", "ESS_ML"]:
            max_power = rated_power[device]
            baseline_power = df.loc[response_window.index, device].tolist()
            available = []
            for v in baseline_power:
                if v < 0:
                    available.append(abs(v))
                else:
                    available.append(max_power - v if v < max_power else 0)
            if sum(available) == 0:
                increments = [0.0] * intervals
            else:
                increments = [(a / sum(available)) * alloc for a in available]
            for idx, (i, inc) in enumerate(zip(response_window.index, increments)):
                v = df.loc[i, device]
                if v < 0:
                    adjust = min(abs(v), inc)
                    new_values_full[i] = v + adjust
                    leftover = inc - adjust
                    if leftover > 0:
                        new_values_full[i] = min(max_power, new_values_full[i] + leftover)
                else:
                    new_values_full[i] = min(max_power, v + inc)
                new_values_full[i] = round(new_values_full[i], 2)
        full_data[device] = new_values_full
        response_dict = {
            "time": [t.strftime("%H:%M:%S") for t in df['time']],
            "value": [float(round(v, 2)) for v in new_values_full]  # ✅ 转为 float
        }
        json_plan["VPP_Response_Plan"].append({
            "device_id": device,
            "device_name": device_name_map[device],
            "response_info": {
                "allocated_amount": ori_response_alloc[device],
                "baseline": baseline_dict,
                "response_plan": response_dict,
                "response_price": response_price,
                "response_profit": round((response_price - response_cost[device]) * ori_response_alloc[device] * 1000, 2)
            }
        })
    return json_plan


def plan_node(state: dict) -> dict:
    interpretation = state.get("interpretation", {})
    variables = interpretation.get("variables", [])
    response_cost = state.get("formulation", {}).get("response_cost", [])
    device_names = state.get("formulation", {}).get("device_names", [])

    writer = get_stream_writer()

    if len(response_cost) == len(device_names):
        response_cost_dict = dict(zip(device_names, response_cost))
    else:
        response_cost_dict = {}
    if not variables:
        plan = {"error": "No variables found in interpretation"}
    else:
        response_alloc = {item["name"]: float(item["value"]) for item in variables}
        plan = generate_dr_plan(response_alloc=response_alloc, response_cost=response_cost_dict)

    # 更新状态中的历史计划列表
    plans = state.get("plans", [])
    plans.append(plan)

    markdown_text = (
        "#### 新奥泛能网虚拟电厂需求侧响应分配与调度计划生成\n"
        "- [✔] 需求转译 — 将用户需求转译成运筹优化可理解的描述方式\n"
        "- [✔] 结构化处理 — 将需求转化为结构化数据\n"
        "- [✔] 代码生成 — 根据转译后的需求生成优化模型能力代码\n"
        "- [✔] 任务求解 — 执行优化求解代码，得到调度与分配结果\n"
        "- [✔] 结果解释 — 将求解结果转化为结构化的中文解释与可读输出\n"
        "- [✔] Reflection 自我修正 — 根据执行结果对模型生成的代码进行自动修正\n"
        "- [✔] 调度计划生成 — 基于求解结果和基线数据，生成最终的调度与分配计划\n"
    )
    writer({f"custom_text{str(uuid4())}": markdown_text})

    # 返回更新的 plan 和 plans
    return {"plans": plans}


def get_p_temperature_curve(ratedPower, x, t0=20, t1=32):
    """
    功率与温度的关系曲线
    """
    T = t0 + (t1 - t0) * (1 + np.tanh(-(x - ratedPower / 2) / ratedPower * 4)) / 2
    return T


# def get_p_by_temperature(T_max, ratedPower=800, t0=25, t1=35):
#     """
#     根据末端稳态温度返回对应功率
#     """
#     for x in range(0, ratedPower + 1, 100):
#         if get_p_temperature_curve(ratedPower, x, t0, t1) <= T_max:
#             return x
#     return ratedPower

def get_p_by_temperature(T_max, ratedPower=20000, t0=20, t1=32):
    """
    根据末端稳态温度返回对应功率
    """
    for x in range(0, ratedPower + 1, 100):
        if get_p_temperature_curve(ratedPower, x, t0, t1) <= T_max:
            return x
    return ratedPower


def compute_delta(temperature, baseline_temp=30, ratedPower=20000):
    P0 = get_p_by_temperature(baseline_temp, ratedPower)
    P1 = get_p_by_temperature(temperature, ratedPower)
    return (P1 - P0) / 1000  # 转MW


def retry_manager_node(inputs: dict) -> dict:
    valid = inputs.get("valid", True)
    reason = inputs.get("reason", "")
    retry_count = inputs.get("retry_count", 0)

    writer = get_stream_writer()

    if not valid:
        retry_count += 1
        if retry_count <= MaxRetryCount:
            return {"retry": True, "retry_count": retry_count, "solver_error_info": reason}
        else:
            return {"retry": False, "retry_count": retry_count, "solver_error_info": reason}
    markdown_text = (
        "#### 新奥泛能网虚拟电厂需求侧响应分配与调度计划生成\n"
        "- [✔] 需求转译 — 将用户需求转译成运筹优化可理解的描述方式\n"
        "- [✔] 结构化处理 — 将需求转化为结构化数据\n"
        "- [✔] 代码生成 — 根据转译后的需求生成优化模型能力代码\n"
        "- [✔] 任务求解 — 执行优化求解代码，得到调度与分配结果\n"
        "- [✔] 结果解释 — 将求解结果转化为结构化的中文解释与可读输出\n"
        "- [✔] Reflection 自我修正 — 根据自检结果对模型生成的代码进行自动修正\n"
        "- [🟡] 调度计划生成 — 基于求解结果和基线数据，生成最终的调度与分配计划\n"
    )
    writer({f"custom_text{str(uuid4())}": markdown_text})
    return {"retry": False, "retry_count": retry_count}


def interpretation_validator_node(inputs: dict) -> dict:
    interpretation = inputs.get("interpretation", {})
    solver_error_info = inputs.get("solver_error_info", "")

    writer = get_stream_writer()

    result = interpretation_validator_chain.invoke({
        "solver_error_info": solver_error_info,
        "interpretation": interpretation
    })

    markdown_text = (
        "#### 新奥泛能网虚拟电厂需求侧响应分配与调度计划生成\n"
        "- [✔] 需求转译 — 将用户需求转译成运筹优化可理解的描述方式\n"
        "- [✔] 结构化处理 — 将需求转化为结构化数据\n"
        "- [✔] 代码生成 — 根据转译后的需求生成优化模型能力代码\n"
        "- [✔] 任务求解 — 执行优化求解代码，得到调度与分配结果\n"
        "- [✔] 结果解释 — 将求解结果转化为结构化的中文解释与可读输出\n"
        "- [🟡] Reflection 自我修正 — 根据执行结果对模型生成的代码进行自动修正\n"
        "- [ ] 调度计划生成 — 基于求解结果和基线数据，生成最终的调度与分配计划\n"
    )
    writer({f"custom_text{str(uuid4())}": markdown_text})

    return result.dict()  # {"valid": bool, "reason": str}


def get_baselines():
    """
    基线预测节点：从本地CSV读取数据，返回指定结构。

    CSV字段示例：
    time    HVAC    ESS_HBN ESS_ML  ESS_HY  PV  EV
    2025-08-04 00:00:00    10    5   2   3   100  20
    """
    # 读取CSV
    df = pd.read_csv(csv_path)

    # 确认包含 time 字段
    if 'time' not in df.columns:
        raise ValueError("CSV文件缺少 time 字段")

    # 设备字段（排除 time）
    device_columns = [col for col in df.columns if col != 'time']

    baselines = []

    # 遍历每个设备
    for device in device_columns:
        device_data = {
            "device_name": device_name_map[device],
            "baseline": {
                "times": df['time'].tolist(),
                "value": df[device].tolist()
            }
        }
        baselines.append(device_data)

    return baselines


def baseline_node(state: dict) -> dict:
    state["baselines"] = get_baselines()
    from src.utils.extra_tools import generate_echarts_config
    baselines = get_baselines()
    x_data = []
    baseline_list = []
    for baseline in baselines:
        name = baseline["device_name"]
        x_data = baseline["baseline"]["times"]
        baseline_values = baseline["baseline"]["value"]
        each = {"name": name + "_baseline", "data": baseline_values}
        baseline_list.append(each)
    baseline_curve = generate_echarts_config("基线曲线", chart_type="line", x_data=x_data, series_list=baseline_list)
    writer = get_stream_writer()
    writer({f"custom_text{str(uuid4())}": f"""{baseline_curve}"""})
    return state


