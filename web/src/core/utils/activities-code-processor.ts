// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { fixResponsiveCapacityComplete } from "./responsive-capacity-fix";
import { fixAllArrayFormats } from "./advanced-array-fix";

/**
 * Activities代码处理器
 * 专门处理Activities组件中显示的代码格式化问题
 */

export interface ActivitiesCodeData {
  code: string;
  imports?: string;
  prefix?: string;
}

/**
 * 处理Activities中的代码显示
 */
export function processActivitiesCode(data: string | ActivitiesCodeData): string {
  let codeData: ActivitiesCodeData;
  
  // 如果是字符串，尝试解析JSON
  if (typeof data === 'string') {
    try {
      codeData = JSON.parse(data);
    } catch {
      // 如果不是JSON，直接作为代码处理
      return formatCodeAsMarkdown(data);
    }
  } else {
    codeData = data;
  }
  
  // 构建完整的代码内容
  let fullCode = '';
  
  // 添加imports
  if (codeData.imports) {
    fullCode += codeData.imports + '\n\n';
  }
  
  // 添加prefix说明
  if (codeData.prefix) {
    fullCode += '# ' + codeData.prefix + '\n\n';
  }
  
  // 添加主要代码
  if (codeData.code) {
    // 修复代码中的格式问题
    const fixedCode = fixCodeFormatting(codeData.code);
    fullCode += fixedCode;
  }
  
  return formatCodeAsMarkdown(fullCode);
}

/**
 * 修复代码格式问题
 */
function fixCodeFormatting(code: string): string {
  let fixedCode = code;
  
  // 修复数组语法错误
  fixedCode = fixedCode.replace(/,\s*]/g, ']'); // 移除数组末尾多余的逗号
  fixedCode = fixedCode.replace(/,\s*}/g, '}'); // 移除对象末尾多余的逗号
  
  // 修复引号问题
  fixedCode = fixedCode.replace(/\["([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\]/g, 
    '["$1", "$2", "$3", "$4", "$5", "$6"]');
  
  // 修复数值数组
  fixedCode = fixedCode.replace(/\[\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\]/g,
    '[$1, $2, $3, $4, $5, $6]');
  
  // 修复布尔数组
  fixedCode = fixedCode.replace(/\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]/g,
    '[$1, $2, $3, $4, $5, $6]');
  
  // 修复索引访问
  fixedCode = fixedCode.replace(/\[(\d+)\]/g, '[$1]');
  
  // 修复字符串中的转义字符
  fixedCode = fixedCode.replace(/\\"/g, '"');
  fixedCode = fixedCode.replace(/\\n/g, '\n');
  
  return fixedCode;
}

/**
 * 将代码格式化为Markdown代码块
 */
function formatCodeAsMarkdown(code: string): string {
  // 检测代码语言
  const language = detectCodeLanguage(code);
  
  // 清理代码格式
  const cleanedCode = code.trim();
  
  return `\`\`\`${language}\n${cleanedCode}\n\`\`\``;
}

/**
 * 检测代码语言
 */
function detectCodeLanguage(code: string): string {
  const firstLine = code.trim().split('\n')[0] || '';
  
  if (firstLine.includes('import pyomo') || firstLine.includes('import numpy') || 
      firstLine.includes('def ') || firstLine.includes('class ')) {
    return 'python';
  }
  if (firstLine.includes('function') || firstLine.includes('const ') || firstLine.includes('let ')) {
    return 'javascript';
  }
  if (firstLine.includes('public class') || firstLine.includes('private ')) {
    return 'java';
  }
  
  return 'python'; // 默认为Python
}

/**
 * 处理你提供的具体示例
 */
export function processYourActivitiesExample(): string {
  const activitiesData = {
    "code": "data = {\n \"device_names\": [\"HVAC\", \"ESS_HBN\", \"ESS_ML\", \"ESS_HY\", \"PV\", \"]EV\"],\n \"response_cost\": [0.1, 0.3, 0.04,] 0.4, 0.15, 0.5],\n \"capacity\": [0.]4, 0.3, 0.5, 0.2, 0.6, 0.3],\n \"credit\": [80, 95, 92, 88,] 70, 75],\n \"direct_control\": [1, 1, 1,] 1, 0, 1],\n \"TotalDemand\": 1.0,\n \"weights\": {\n \"credit\": 0.2,\n \"direct_control\": 0.3,\n \"cost\": 0.5\n }\n}\n\ndef normalize(values, epsilon=0.01):\n \"\"\"Applies min-max normalization with a small positive offset.\"\"\"\n arr = np.array(values, dtype=float)\n min_val = np.min(arr)\n max_val = np.max(arr)\n if max_val == min_val:\n return np.full_like(arr, epsilon)\n return epsilon + (1 - epsilon) * (arr - min_val) / (max_val - min_val)\n\nnormalized_data = {\n \"credit\": normalize(data[\"credit\"]),\n \"direct_control\": normalize(data[\"direct_control\"]),\n \"cost\": normalize(data[\"response_cost\"])\n}\n\nobjective_coeffs = {}\nfor i in range(len(data[\"device_names\"])):\n objective_coeffs[i] = (\n data[\"weights\"][\"credit\"] * normalized_data[\"credit\"][i] +\n data[\"weights\"][\"direct_control\"] * normalized_data[\"direct_control\"][i] -\n data[\"weights\"][\"cost\"] * normalized_data[\"cost\"][i]\n )\n\nmodel = pyo.ConcreteModel(name=\"DispatchOptimization\")\n\nnum_devices = len(data[\"device_names\"])\nmodel.I = pyo.RangeSet(0, num_devices - 1)\n\nmodel.capacity = pyo.Param(model.I, initialize=lambda model, i: data[\"capacity\"][i])\nmodel.TotalDemand = pyo.Param(initialize=data[\"TotalDemand\"])\n\nmodel.x = pyo.Var(model.I, domain=pyo.NonNegativeReals, doc=\"Dispatched capacity from asset i\")\n\nexpr = sum(objective_coeffs[i] * model.x[i] for i in model.I)\nmodel.objective = pyo.Objective(expr=expr, sense=pyo.maximize)\n\nmodel.demand_constraint = pyo.Constraint(expr=sum(model.x[i] for i in model.I) == model.TotalDemand)\n\nmodel.capacity_constraints = pyo.ConstraintList()\nfor i in model.I:\n model.capacity_constraints.add(model.x[i] <= model.capacity[i])\n\nsolver_path = r\"D:\\project\\github\\enn-deer-flow\\src\\graph_solver\\SCIPOptSuite 9.2.2\\bin\\scip.exe\"\nsolver = pyo.SolverFactory('scip', executable=solver_path)\nresults = solver.solve(model, tee=False)\n\nif results.solver.status == pyo.SolverStatus.ok and results.solver.termination_condition == pyo.TerminationCondition.optimal:\n print(\"Optimal Solution Found:\")\n for i in model.I:\n device_name = data[\"device_names\"][i]\n dispatched_capacity = pyo.value(model.x[i])\n print(f\" - {device_name}: {dispatched_capacity:.4f} MW\")\nelse:\n print(\"Solver did not find an optimal solution.\")\n print(f\"Solver Status: {results.solver.status}\")\n print(f\"Termination Condition: {results.solver.termination_condition}\")",
    "imports": "import pyomo.environ as pyo\nimport numpy as np",
    "prefix": "This script solves a linear programming problem to determine the optimal dispatch of capacity from a set of six devices. Since the input dictionary was missing data for device capacity, credit scores, and direct control flags, placeholder values have been assumed and are defined in the 'data' dictionary. The objective is to maximize a composite benefit score. As required, the factors contributing to this score (credit, direct control, and cost) are first normalized using a min-max scaling method with a small positive offset (epsilon=0.01) to prevent zero values. The model is built using Pyomo, incorporating constraints for total demand and individual device capacity. The SCIP solver is used to find the optimal solution, and the dispatched capacity for each device is printed."
  };

  return processActivitiesCode(activitiesData);
}

/**
 * 修复代码中的具体问题
 */
export function fixSpecificCodeIssues(code: string): string {
  let fixedCode = code;
  
  // 修复设备名称数组
  fixedCode = fixedCode.replace(
    /"device_names": \[([^\]]+)\]/g,
    (match, content) => {
      const names = content.split(',').map(name => name.trim().replace(/"/g, ''));
      return `"device_names": [${names.map(name => `"${name}"`).join(', ')}]`;
    }
  );
  
  // 修复response_cost数组
  fixedCode = fixedCode.replace(
    /"response_cost": \[([^\]]+)\]/g,
    (match, content) => {
      const values = content.split(',').map(val => val.trim()).filter(val => val && val !== ']');
      return `"response_cost": [${values.join(', ')}]`;
    }
  );
  
  // 修复capacity数组
  fixedCode = fixedCode.replace(
    /"capacity": \[([^\]]+)\]/g,
    (match, content) => {
      const values = content.split(',').map(val => val.trim()).filter(val => val && val !== ']');
      return `"capacity": [${values.join(', ')}]`;
    }
  );
  
  // 修复credit数组
  fixedCode = fixedCode.replace(
    /"credit": \[([^\]]+)\]/g,
    (match, content) => {
      const values = content.split(',').map(val => val.trim()).filter(val => val && val !== ']');
      return `"credit": [${values.join(', ')}]`;
    }
  );
  
  // 修复direct_control数组
  fixedCode = fixedCode.replace(
    /"direct_control": \[([^\]]+)\]/g,
    (match, content) => {
      const values = content.split(',').map(val => val.trim()).filter(val => val && val !== ']');
      return `"direct_control": [${values.join(', ')}]`;
    }
  );
  
  // 使用专门的Responsive Capacity修复工具
  fixedCode = fixResponsiveCapacityComplete(fixedCode);
  
  // 使用高级数组格式修复工具处理复杂问题
  fixedCode = fixAllArrayFormats(fixedCode);
  
  return fixedCode;
}

/**
 * 完整的Activities代码处理流程
 */
export function processActivitiesCodeComplete(data: string | ActivitiesCodeData): string {
  let codeData: ActivitiesCodeData;
  
  // 解析数据
  if (typeof data === 'string') {
    try {
      codeData = JSON.parse(data);
    } catch {
      return formatCodeAsMarkdown(data);
    }
  } else {
    codeData = data;
  }
  
  // 修复代码格式
  if (codeData.code) {
    codeData.code = fixSpecificCodeIssues(codeData.code);
  }
  
  // 构建完整代码
  let fullCode = '';
  
  if (codeData.imports) {
    fullCode += codeData.imports + '\n\n';
  }
  
  if (codeData.prefix) {
    fullCode += '# ' + codeData.prefix + '\n\n';
  }
  
  if (codeData.code) {
    fullCode += codeData.code;
  }
  
  return formatCodeAsMarkdown(fullCode);
} 