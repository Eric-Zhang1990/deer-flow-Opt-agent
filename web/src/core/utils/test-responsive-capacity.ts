// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { fixSpecificCodeIssues } from "./activities-code-processor";

/**
 * 测试Responsive Capacity数组修复
 */

export function testResponsiveCapacityFix() {
  console.log("=== 测试Responsive Capacity数组修复 ===\n");
  
  // 测试用例1：你提到的具体问题
  const testCase1 = `Responsive Capacity (MW): [0.15,] 0.41, 0.5, 0.35, 0.18, 0.11]`;
  console.log("测试用例1 - 原始文本:");
  console.log(testCase1);
  
  const result1 = fixSpecificCodeIssues(testCase1);
  console.log("修复后:");
  console.log(result1);
  console.log();
  
  // 测试用例2：模拟原始格式
  const testCase2 = `Responsive Capacity (MW): [0.15,`;
  console.log("测试用例2 - 原始格式:");
  console.log(testCase2);
  
  const result2 = fixSpecificCodeIssues(testCase2);
  console.log("修复后:");
  console.log(result2);
  console.log();
  
  // 测试用例3：完整的数组
  const testCase3 = `Responsive Capacity (MW): [0.15, 0.41, 0.5, 0.35, 0.18, 0.11]`;
  console.log("测试用例3 - 完整数组:");
  console.log(testCase3);
  
  const result3 = fixSpecificCodeIssues(testCase3);
  console.log("修复后:");
  console.log(result3);
  console.log();
  
  // 测试用例4：包含在代码块中的情况
  const testCase4 = `data = {
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
}

print("Responsive Capacity (MW): [0.15,] 0.41, 0.5, 0.35, 0.18, 0.11]")`;
  
  console.log("测试用例4 - 代码块中的情况:");
  console.log(testCase4);
  
  const result4 = fixSpecificCodeIssues(testCase4);
  console.log("修复后:");
  console.log(result4);
  console.log();
  
  return {
    testCase1: { original: testCase1, fixed: result1 },
    testCase2: { original: testCase2, fixed: result2 },
    testCase3: { original: testCase3, fixed: result3 },
    testCase4: { original: testCase4, fixed: result4 }
  };
}

export function testArrayFormattingIssues() {
  console.log("=== 测试数组格式化问题 ===\n");
  
  const testCases = [
    // 问题1：数组中间有多余的]
    `[0.15,] 0.41, 0.5, 0.35, 0.18, 0.11]`,
    
    // 问题2：数组末尾有多余的逗号
    `[0.15, 0.41, 0.5, 0.35, 0.18, 0.11,]`,
    
    // 问题3：数组开头有多余的逗号
    `[, 0.15, 0.41, 0.5, 0.35, 0.18, 0.11]`,
    
    // 问题4：多个连续的逗号
    `[0.15,, 0.41, 0.5, 0.35, 0.18, 0.11]`,
    
    // 问题5：混合问题
    `[0.15,] 0.41, 0.5, 0.35, 0.18, 0.11,]`
  ];
  
  testCases.forEach((testCase, index) => {
    console.log(`测试用例 ${index + 1}:`);
    console.log("原始:", testCase);
    
    const fixed = fixSpecificCodeIssues(testCase);
    console.log("修复后:", fixed);
    console.log();
  });
  
  return testCases.map(testCase => ({
    original: testCase,
    fixed: fixSpecificCodeIssues(testCase)
  }));
}

export function testResponsiveCapacityInContext() {
  console.log("=== 测试Responsive Capacity在上下文中的修复 ===\n");
  
  const contextCode = `# 设备容量分析

## 设备信息
- HVAC: 0.15 MW
- ESS_HBN: 0.41 MW  
- ESS_ML: 0.5 MW
- ESS_HY: 0.35 MW
- PV: 0.18 MW
- EV: 0.11 MW

## 容量汇总
Responsive Capacity (MW): [0.15,] 0.41, 0.5, 0.35, 0.18, 0.11]

## 分析结果
总容量: 1.7 MW
平均容量: 0.283 MW`;

  console.log("原始代码:");
  console.log(contextCode);
  console.log();
  
  const fixedCode = fixSpecificCodeIssues(contextCode);
  console.log("修复后:");
  console.log(fixedCode);
  
  return { original: contextCode, fixed: fixedCode };
}

// 运行所有测试
export function runAllResponsiveCapacityTests() {
  console.log("🚀 开始运行Responsive Capacity修复测试\n");
  
  testResponsiveCapacityFix();
  console.log("=".repeat(50) + "\n");
  
  testArrayFormattingIssues();
  console.log("=".repeat(50) + "\n");
  
  testResponsiveCapacityInContext();
  
  console.log("\n✅ 所有Responsive Capacity测试完成");
} 