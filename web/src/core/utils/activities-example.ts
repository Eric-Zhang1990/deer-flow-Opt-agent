// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { processActivitiesCode, processActivitiesCodeComplete } from "./activities-code-processor";

/**
 * Activities代码处理示例
 * 展示如何处理Activities中显示的代码格式化问题
 */

export function demonstrateActivitiesCodeProcessing() {
  console.log("=== Activities代码处理示例 ===\n");
  
  // 你提供的原始数据
  const originalData = {
    "code": "data = {\n \"device_names\": [\"HVAC\", \"ESS_HBN\", \"ESS_ML\", \"ESS_HY\", \"PV\", \"]EV\"],\n \"response_cost\": [0.1, 0.3, 0.04,] 0.4, 0.15, 0.5],\n \"capacity\": [0.]4, 0.3, 0.5, 0.2, 0.6, 0.3],\n \"credit\": [80, 95, 92, 88,] 70, 75],\n \"direct_control\": [1, 1, 1,] 1, 0, 1],\n \"TotalDemand\": 1.0,\n \"weights\": {\n \"credit\": 0.2,\n \"direct_control\": 0.3,\n \"cost\": 0.5\n }\n}\n\ndef normalize(values, epsilon=0.01):\n \"\"\"Applies min-max normalization with a small positive offset.\"\"\"\n arr = np.array(values, dtype=float)\n min_val = np.min(arr)\n max_val = np.max(arr)\n if max_val == min_val:\n return np.full_like(arr, epsilon)\n return epsilon + (1 - epsilon) * (arr - min_val) / (max_val - min_val)\n\nnormalized_data = {\n \"credit\": normalize(data[\"credit\"]),\n \"direct_control\": normalize(data[\"direct_control\"]),\n \"cost\": normalize(data[\"response_cost\"])\n}\n\nobjective_coeffs = {}\nfor i in range(len(data[\"device_names\"])):\n objective_coeffs[i] = (\n data[\"weights\"][\"credit\"] * normalized_data[\"credit\"][i] +\n data[\"weights\"][\"direct_control\"] * normalized_data[\"direct_control\"][i] -\n data[\"weights\"][\"cost\"] * normalized_data[\"cost\"][i]\n )\n\nmodel = pyo.ConcreteModel(name=\"DispatchOptimization\")\n\nnum_devices = len(data[\"device_names\"])\nmodel.I = pyo.RangeSet(0, num_devices - 1)\n\nmodel.capacity = pyo.Param(model.I, initialize=lambda model, i: data[\"capacity\"][i])\nmodel.TotalDemand = pyo.Param(initialize=data[\"TotalDemand\"])\n\nmodel.x = pyo.Var(model.I, domain=pyo.NonNegativeReals, doc=\"Dispatched capacity from asset i\")\n\nexpr = sum(objective_coeffs[i] * model.x[i] for i in model.I)\nmodel.objective = pyo.Objective(expr=expr, sense=pyo.maximize)\n\nmodel.demand_constraint = pyo.Constraint(expr=sum(model.x[i] for i in model.I) == model.TotalDemand)\n\nmodel.capacity_constraints = pyo.ConstraintList()\nfor i in model.I:\n model.capacity_constraints.add(model.x[i] <= model.capacity[i])\n\nsolver_path = r\"D:\\project\\github\\enn-deer-flow\\src\\graph_solver\\SCIPOptSuite 9.2.2\\bin\\scip.exe\"\nsolver = pyo.SolverFactory('scip', executable=solver_path)\nresults = solver.solve(model, tee=False)\n\nif results.solver.status == pyo.SolverStatus.ok and results.solver.termination_condition == pyo.TerminationCondition.optimal:\n print(\"Optimal Solution Found:\")\n for i in model.I:\n device_name = data[\"device_names\"][i]\n dispatched_capacity = pyo.value(model.x[i])\n print(f\" - {device_name}: {dispatched_capacity:.4f} MW\")\nelse:\n print(\"Solver did not find an optimal solution.\")\n print(f\"Solver Status: {results.solver.status}\")\n print(f\"Termination Condition: {results.solver.termination_condition}\")",
    "imports": "import pyomo.environ as pyo\nimport numpy as np",
    "prefix": "This script solves a linear programming problem to determine the optimal dispatch of capacity from a set of six devices. Since the input dictionary was missing data for device capacity, credit scores, and direct control flags, placeholder values have been assumed and are defined in the 'data' dictionary. The objective is to maximize a composite benefit score. As required, the factors contributing to this score (credit, direct control, and cost) are first normalized using a min-max scaling method with a small positive offset (epsilon=0.01) to prevent zero values. The model is built using Pyomo, incorporating constraints for total demand and individual device capacity. The SCIP solver is used to find the optimal solution, and the dispatched capacity for each device is printed."
  };

  console.log("原始数据:");
  console.log(JSON.stringify(originalData, null, 2));
  
  console.log("\n=== 处理后的代码 ===");
  
  // 使用完整处理器
  const processedCode = processActivitiesCodeComplete(originalData);
  console.log(processedCode);
  
  return processedCode;
}

export function showCodeComparison() {
  console.log("=== 代码对比示例 ===\n");
  
  // 原始有问题的代码
  const problematicCode = `data = {
 "device_names": ["HVAC", "ESS_HBN", "ESS_ML", "ESS_HY", "PV", "]EV"],
 "response_cost": [0.1, 0.3, 0.04,] 0.4, 0.15, 0.5],
 "capacity": [0.]4, 0.3, 0.5, 0.2, 0.6, 0.3],
 "credit": [80, 95, 92, 88,] 70, 75],
 "direct_control": [1, 1, 1,] 1, 0, 1],
 "TotalDemand": 1.0,
 "weights": {
 "credit": 0.2,
 "direct_control": 0.3,
 "cost": 0.5
 }
}`;

  console.log("原始代码（有问题）:");
  console.log(problematicCode);
  
  console.log("\n修复后的代码:");
  const fixedCode = `data = {
    "device_names": ["HVAC", "ESS_HBN", "ESS_ML", "ESS_HY", "PV", "EV"],
    "response_cost": [0.1, 0.3, 0.04, 0.4, 0.15, 0.5],
    "capacity": [0.4, 0.3, 0.5, 0.2, 0.6, 0.3],
    "credit": [80, 95, 92, 88, 70, 75],
    "direct_control": [1, 1, 1, 1, 0, 1],
    "TotalDemand": 1.0,
    "weights": {
        "credit": 0.2,
        "direct_control": 0.3,
        "cost": 0.5
    }
}`;
  
  console.log(fixedCode);
  
  return { original: problematicCode, fixed: fixedCode };
}

export function demonstrateMarkdownFormatting() {
  console.log("=== Markdown格式化示例 ===\n");
  
  const codeData = {
    code: `def normalize(values, epsilon=0.01):
    """Applies min-max normalization with a small positive offset."""
    arr = np.array(values, dtype=float)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val == min_val:
        return np.full_like(arr, epsilon)
    return epsilon + (1 - epsilon) * (arr - min_val) / (max_val - min_val)`,
    imports: "import numpy as np",
    prefix: "数据标准化函数"
  };
  
  console.log("原始数据:");
  console.log(JSON.stringify(codeData, null, 2));
  
  console.log("\nMarkdown格式化结果:");
  const formatted = processActivitiesCode(codeData);
  console.log(formatted);
  
  return formatted;
}

// 运行所有示例
export function runAllActivitiesExamples() {
  console.log("🚀 开始运行Activities代码处理示例\n");
  
  demonstrateActivitiesCodeProcessing();
  console.log("\n" + "=".repeat(50) + "\n");
  
  showCodeComparison();
  console.log("\n" + "=".repeat(50) + "\n");
  
  demonstrateMarkdownFormatting();
  
  console.log("\n✅ 所有Activities示例运行完成");
} 