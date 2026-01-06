// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Responsive Capacity数组格式修复工具
 * 专门处理你提到的数组格式问题
 */

/**
 * 修复Responsive Capacity数组格式问题
 */
export function fixResponsiveCapacityFormat(text: string): string {
  let fixedText = text;
  
  // 修复你提到的具体问题：[0.15,] 0.41, 0.5, 0.35, 0.18, 0.11]
  // 应该修复为：[0.15, 0.41, 0.5, 0.35, 0.18, 0.11]
  
  // 步骤1：找到Responsive Capacity行
  const responsiveCapacityRegex = /Responsive Capacity \(MW\):\s*\[([^\]]*)\]/g;
  
  fixedText = fixedText.replace(responsiveCapacityRegex, (match, content) => {
    console.log("找到Responsive Capacity内容:", content);
    
    // 步骤2：清理内容
    let cleanedContent = content;
    
    // 移除多余的]符号
    cleanedContent = cleanedContent.replace(/\]\s*/g, ', ');
    
    // 移除多余的逗号
    cleanedContent = cleanedContent.replace(/,\s*,/g, ',');
    cleanedContent = cleanedContent.replace(/,\s*$/g, ''); // 移除末尾逗号
    
    // 清理空白字符
    cleanedContent = cleanedContent.replace(/\s+/g, ' ').trim();
    
    console.log("清理后的内容:", cleanedContent);
    
    return `Responsive Capacity (MW): [${cleanedContent}]`;
  });
  
  return fixedText;
}

/**
 * 更通用的数组格式修复
 */
export function fixArrayFormat(text: string): string {
  let fixedText = text;
  
  // 修复数组中间的错误格式：[数字,] 数字
  fixedText = fixedText.replace(/\[([\d.]+),\s*\]\s*([\d.]+)/g, '[$1, $2');
  
  // 修复数组末尾多余的逗号
  fixedText = fixedText.replace(/,\s*\]/g, ']');
  
  // 修复数组开头的多余逗号
  fixedText = fixedText.replace(/\[\s*,/g, '[');
  
  // 修复连续的逗号
  fixedText = fixedText.replace(/,\s*,/g, ',');
  
  // 修复数组中间的错误格式：] 数字
  fixedText = fixedText.replace(/\]\s*([\d.]+)/g, ', $1');
  
  return fixedText;
}

/**
 * 完整的Responsive Capacity修复流程
 */
export function fixResponsiveCapacityComplete(text: string): string {
  console.log("=== 开始修复Responsive Capacity格式 ===");
  console.log("原始文本:", text);
  
  // 首先应用通用数组修复
  let fixedText = fixArrayFormat(text);
  console.log("通用数组修复后:", fixedText);
  
  // 然后应用专门的Responsive Capacity修复
  fixedText = fixResponsiveCapacityFormat(fixedText);
  console.log("Responsive Capacity修复后:", fixedText);
  
  return fixedText;
}

/**
 * 测试修复效果
 */
export function testResponsiveCapacityFix() {
  console.log("=== 测试Responsive Capacity修复 ===\n");
  
  const testCases = [
    // 你提到的具体问题
    "Responsive Capacity (MW): [0.15,] 0.41, 0.5, 0.35, 0.18, 0.11]",
    
    // 类似的问题
    "Responsive Capacity (MW): [0.15, 0.41,] 0.5, 0.35, 0.18, 0.11]",
    
    // 多个问题
    "Responsive Capacity (MW): [0.15,] 0.41,] 0.5, 0.35, 0.18, 0.11]",
    
    // 正常格式（不应该被修改）
    "Responsive Capacity (MW): [0.15, 0.41, 0.5, 0.35, 0.18, 0.11]",
    
    // 在代码块中的情况
    `print("Responsive Capacity (MW): [0.15,] 0.41, 0.5, 0.35, 0.18, 0.11]")`
  ];
  
  testCases.forEach((testCase, index) => {
    console.log(`测试用例 ${index + 1}:`);
    console.log("原始:", testCase);
    
    const fixed = fixResponsiveCapacityComplete(testCase);
    console.log("修复后:", fixed);
    console.log();
  });
  
  return testCases.map(testCase => ({
    original: testCase,
    fixed: fixResponsiveCapacityComplete(testCase)
  }));
}

/**
 * 验证修复结果
 */
export function validateResponsiveCapacityFix(original: string, fixed: string): boolean {
  // 检查是否还有错误的格式
  const hasErrorFormat = /\[[\d.]+,]\s*[\d.]+/.test(fixed);
  const hasExtraBracket = /\]\s*[\d.]+/.test(fixed);
  
  if (hasErrorFormat || hasExtraBracket) {
    console.log("❌ 修复失败，仍有格式错误");
    return false;
  }
  
  // 检查是否是正确的数组格式
  const isValidArray = /\[[\d.,\s]+\]/.test(fixed);
  
  if (isValidArray) {
    console.log("✅ 修复成功，格式正确");
    return true;
  } else {
    console.log("❌ 修复失败，格式不正确");
    return false;
  }
} 