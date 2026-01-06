// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { fixAllArrayFormats, validateArrayFix } from "./advanced-array-fix";

/**
 * 测试高级数组格式修复工具
 */

export function testAdvancedArrayFix() {
  console.log("=== 测试高级数组格式修复 ===\n");
  
  // 你提供的具体问题
  const testCase1 = `Responsive Capacity (MW): [0.15, 0.41, 0.5, 0.3]5, 0.18, 0.11]
User Credit Score: [3, 4], 4, 5, 2, 5] (on a scale of 1-5, where a higher value indicates better credit)
Direct Control Flag: [1, 1, 1, 1,] 0, 0] (where 1 indicates the device is directly controllable by the VPP, and 0 indicates it is not)
Response Cost (in 10,000 CNY/MW): []0.1, 0.3, 0.04, 0.4, 0.15, 0.5] (a higher value indicates a higher cost to participate in the demand response)`;

  console.log("测试用例1 - 你的具体问题:");
  console.log("原始文本:");
  console.log(testCase1);
  console.log();
  
  const result1 = fixAllArrayFormats(testCase1);
  console.log("修复后:");
  console.log(result1);
  console.log();
  
  // 验证修复结果
  const isValid1 = validateArrayFix(testCase1, result1);
  console.log(`验证结果: ${isValid1 ? '✅ 成功' : '❌ 失败'}`);
  console.log();
  
  // 更多测试用例
  const testCases = [
    {
      name: "问题1: ]5格式",
      original: "[0.15, 0.41, 0.5, 0.3]5, 0.18, 0.11]",
      expected: "[0.15, 0.41, 0.5, 0.35, 0.18, 0.11]"
    },
    {
      name: "问题2: ],格式",
      original: "[3, 4], 4, 5, 2, 5]",
      expected: "[3, 4, 4, 5, 2, 5]"
    },
    {
      name: "问题3: ,]格式",
      original: "[1, 1, 1, 1,] 0, 0]",
      expected: "[1, 1, 1, 1, 0, 0]"
    },
    {
      name: "问题4: []格式",
      original: "[]0.1, 0.3, 0.04, 0.4, 0.15, 0.5]",
      expected: "[0.1, 0.3, 0.04, 0.4, 0.15, 0.5]"
    }
  ];
  
  testCases.forEach((testCase, index) => {
    console.log(`测试用例 ${index + 2} - ${testCase.name}:`);
    console.log("原始:", testCase.original);
    
    const fixed = fixAllArrayFormats(testCase.original);
    console.log("修复后:", fixed);
    console.log("期望:", testCase.expected);
    console.log("匹配:", fixed === testCase.expected ? "✅" : "❌");
    console.log();
  });
  
  return {
    testCase1: { original: testCase1, fixed: result1, valid: isValid1 },
    testCases: testCases.map(tc => ({
      ...tc,
      fixed: fixAllArrayFormats(tc.original),
      valid: validateArrayFix(tc.original, fixAllArrayFormats(tc.original))
    }))
  };
}

export function testIndividualFixes() {
  console.log("=== 测试单独修复功能 ===\n");
  
  // 测试Responsive Capacity修复
  const responsiveCapacityTest = "Responsive Capacity (MW): [0.15, 0.41, 0.5, 0.3]5, 0.18, 0.11]";
  console.log("Responsive Capacity测试:");
  console.log("原始:", responsiveCapacityTest);
  
  const { fixResponsiveCapacityAdvanced } = require("./advanced-array-fix");
  const fixedRC = fixResponsiveCapacityAdvanced(responsiveCapacityTest);
  console.log("修复后:", fixedRC);
  console.log();
  
  // 测试User Credit Score修复
  const creditScoreTest = "User Credit Score: [3, 4], 4, 5, 2, 5]";
  console.log("User Credit Score测试:");
  console.log("原始:", creditScoreTest);
  
  const { fixUserCreditScore } = require("./advanced-array-fix");
  const fixedCS = fixUserCreditScore(creditScoreTest);
  console.log("修复后:", fixedCS);
  console.log();
  
  // 测试Direct Control Flag修复
  const directControlTest = "Direct Control Flag: [1, 1, 1, 1,] 0, 0]";
  console.log("Direct Control Flag测试:");
  console.log("原始:", directControlTest);
  
  const { fixDirectControlFlag } = require("./advanced-array-fix");
  const fixedDC = fixDirectControlFlag(directControlTest);
  console.log("修复后:", fixedDC);
  console.log();
  
  // 测试Response Cost修复
  const responseCostTest = "Response Cost (in 10,000 CNY/MW): []0.1, 0.3, 0.04, 0.4, 0.15, 0.5]";
  console.log("Response Cost测试:");
  console.log("原始:", responseCostTest);
  
  const { fixResponseCost } = require("./advanced-array-fix");
  const fixedRCost = fixResponseCost(responseCostTest);
  console.log("修复后:", fixedRCost);
  console.log();
  
  return {
    responsiveCapacity: { original: responsiveCapacityTest, fixed: fixedRC },
    creditScore: { original: creditScoreTest, fixed: fixedCS },
    directControl: { original: directControlTest, fixed: fixedDC },
    responseCost: { original: responseCostTest, fixed: fixedRCost }
  };
}

export function testComplexScenarios() {
  console.log("=== 测试复杂场景 ===\n");
  
  const complexScenarios = [
    {
      name: "混合问题1",
      text: `# 设备分析报告

## 容量信息
Responsive Capacity (MW): [0.15, 0.41, 0.5, 0.3]5, 0.18, 0.11]

## 信用评分
User Credit Score: [3, 4], 4, 5, 2, 5]

## 控制标志
Direct Control Flag: [1, 1, 1, 1,] 0, 0]

## 响应成本
Response Cost (in 10,000 CNY/MW): []0.1, 0.3, 0.04, 0.4, 0.15, 0.5]`
    },
    {
      name: "混合问题2",
      text: `data = {
  "capacity": [0.15, 0.41, 0.5, 0.3]5, 0.18, 0.11],
  "credit": [3, 4], 4, 5, 2, 5],
  "control": [1, 1, 1, 1,] 0, 0],
  "cost": []0.1, 0.3, 0.04, 0.4, 0.15, 0.5]
}`
    }
  ];
  
  complexScenarios.forEach((scenario, index) => {
    console.log(`复杂场景 ${index + 1} - ${scenario.name}:`);
    console.log("原始文本:");
    console.log(scenario.text);
    console.log();
    
    const fixed = fixAllArrayFormats(scenario.text);
    console.log("修复后:");
    console.log(fixed);
    console.log();
    
    const isValid = validateArrayFix(scenario.text, fixed);
    console.log(`验证结果: ${isValid ? '✅ 成功' : '❌ 失败'}`);
    console.log("=".repeat(50));
    console.log();
  });
  
  return complexScenarios.map(scenario => ({
    ...scenario,
    fixed: fixAllArrayFormats(scenario.text),
    valid: validateArrayFix(scenario.text, fixAllArrayFormats(scenario.text))
  }));
}

// 运行所有测试
export function runAllAdvancedArrayTests() {
  console.log("🚀 开始运行高级数组格式修复测试\n");
  
  testAdvancedArrayFix();
  console.log("=".repeat(50) + "\n");
  
  testIndividualFixes();
  console.log("=".repeat(50) + "\n");
  
  testComplexScenarios();
  
  console.log("\n✅ 所有高级数组格式修复测试完成");
} 