// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 高级数组格式修复工具
 * 处理复杂的数组格式问题
 */

/**
 * 修复复杂的数组格式问题
 */
export function fixAdvancedArrayFormat(text: string): string {
  let fixedText = text;
  
  console.log("=== 开始高级数组格式修复 ===");
  console.log("原始文本:", fixedText);
  
  // 修复1: [0.15, 0.41, 0.5, 0.3]5, 0.18, 0.11] -> [0.15, 0.41, 0.5, 0.35, 0.18, 0.11]
  fixedText = fixedText.replace(/\[([\d.,\s]+)\]([\d.]+)/g, (match, arrayContent, extraNumber) => {
    console.log(`修复1: 找到 ${match} -> 将 ${extraNumber} 合并到数组中`);
    const values = arrayContent.split(',').map(v => v.trim()).filter(v => v);
    values.push(extraNumber);
    return `[${values.join(', ')}]`;
  });
  
  // 修复2: [3, 4], 4, 5, 2, 5] -> [3, 4, 4, 5, 2, 5]
  fixedText = fixedText.replace(/\[([\d.,\s]+)\],\s*([\d.,\s]+)\]/g, (match, firstPart, secondPart) => {
    console.log(`修复2: 找到 ${match} -> 合并两个部分`);
    const firstValues = firstPart.split(',').map(v => v.trim()).filter(v => v);
    const secondValues = secondPart.split(',').map(v => v.trim()).filter(v => v);
    const allValues = [...firstValues, ...secondValues];
    return `[${allValues.join(', ')}]`;
  });
  
  // 修复3: [1, 1, 1, 1,] 0, 0] -> [1, 1, 1, 1, 0, 0]
  fixedText = fixedText.replace(/\[([\d.,\s]+),\s*\]\s*([\d.,\s]+)\]/g, (match, firstPart, secondPart) => {
    console.log(`修复3: 找到 ${match} -> 合并并移除多余逗号`);
    const firstValues = firstPart.split(',').map(v => v.trim()).filter(v => v);
    const secondValues = secondPart.split(',').map(v => v.trim()).filter(v => v);
    const allValues = [...firstValues, ...secondValues];
    return `[${allValues.join(', ')}]`;
  });
  
  // 修复4: []0.1, 0.3, 0.04, 0.4, 0.15, 0.5] -> [0.1, 0.3, 0.04, 0.4, 0.15, 0.5]
  fixedText = fixedText.replace(/\[\]([\d.,\s]+)\]/g, (match, content) => {
    console.log(`修复4: 找到 ${match} -> 移除开头的[]`);
    const values = content.split(',').map(v => v.trim()).filter(v => v);
    return `[${values.join(', ')}]`;
  });
  
  // 修复5: 通用的数组中间]问题
  fixedText = fixedText.replace(/\]\s*([\d.]+)/g, ', $1');
  
  // 修复6: 移除数组末尾多余的逗号
  fixedText = fixedText.replace(/,\s*\]/g, ']');
  
  // 修复7: 移除数组开头的多余逗号
  fixedText = fixedText.replace(/\[\s*,/g, '[');
  
  // 修复8: 处理连续的逗号
  fixedText = fixedText.replace(/,\s*,/g, ',');
  
  console.log("修复后文本:", fixedText);
  
  return fixedText;
}

/**
 * 专门修复Responsive Capacity格式
 */
export function fixResponsiveCapacityAdvanced(text: string): string {
  let fixedText = text;
  
  // 查找并修复Responsive Capacity行
  const responsiveCapacityRegex = /Responsive Capacity \(MW\):\s*\[([^\]]*)\]/g;
  
  fixedText = fixedText.replace(responsiveCapacityRegex, (match, content) => {
    console.log("找到Responsive Capacity内容:", content);
    
    // 应用高级数组修复
    const fixedContent = fixAdvancedArrayFormat(`[${content}]`);
    
    // 移除外层的[]
    const cleanContent = fixedContent.replace(/^\[|\]$/g, '');
    
    return `Responsive Capacity (MW): [${cleanContent}]`;
  });
  
  return fixedText;
}

/**
 * 专门修复User Credit Score格式
 */
export function fixUserCreditScore(text: string): string {
  let fixedText = text;
  
  const creditScoreRegex = /User Credit Score:\s*\[([^\]]*)\]/g;
  
  fixedText = fixedText.replace(creditScoreRegex, (match, content) => {
    console.log("找到User Credit Score内容:", content);
    
    const fixedContent = fixAdvancedArrayFormat(`[${content}]`);
    const cleanContent = fixedContent.replace(/^\[|\]$/g, '');
    
    return `User Credit Score: [${cleanContent}]`;
  });
  
  return fixedText;
}

/**
 * 专门修复Direct Control Flag格式
 */
export function fixDirectControlFlag(text: string): string {
  let fixedText = text;
  
  const directControlRegex = /Direct Control Flag:\s*\[([^\]]*)\]/g;
  
  fixedText = fixedText.replace(directControlRegex, (match, content) => {
    console.log("找到Direct Control Flag内容:", content);
    
    const fixedContent = fixAdvancedArrayFormat(`[${content}]`);
    const cleanContent = fixedContent.replace(/^\[|\]$/g, '');
    
    return `Direct Control Flag: [${cleanContent}]`;
  });
  
  return fixedText;
}

/**
 * 专门修复Response Cost格式
 */
export function fixResponseCost(text: string): string {
  let fixedText = text;
  
  const responseCostRegex = /Response Cost \(in 10,000 CNY\/MW\):\s*\[([^\]]*)\]/g;
  
  fixedText = fixedText.replace(responseCostRegex, (match, content) => {
    console.log("找到Response Cost内容:", content);
    
    const fixedContent = fixAdvancedArrayFormat(`[${content}]`);
    const cleanContent = fixedContent.replace(/^\[|\]$/g, '');
    
    return `Response Cost (in 10,000 CNY/MW): [${cleanContent}]`;
  });
  
  return fixedText;
}

/**
 * 完整的数组格式修复
 */
export function fixAllArrayFormats(text: string): string {
  console.log("=== 开始完整数组格式修复 ===");
  console.log("原始文本:", text);
  
  let fixedText = text;
  
  // 按顺序应用各种修复
  fixedText = fixResponsiveCapacityAdvanced(fixedText);
  fixedText = fixUserCreditScore(fixedText);
  fixedText = fixDirectControlFlag(fixedText);
  fixedText = fixResponseCost(fixedText);
  
  // 最后应用通用修复
  fixedText = fixAdvancedArrayFormat(fixedText);
  
  console.log("最终修复结果:", fixedText);
  
  return fixedText;
}

/**
 * 测试你的具体问题
 */
export function testYourSpecificProblem() {
  console.log("=== 测试你的具体问题 ===\n");
  
  const problematicText = `Responsive Capacity (MW): [0.15, 0.41, 0.5, 0.3]5, 0.18, 0.11]
User Credit Score: [3, 4], 4, 5, 2, 5] (on a scale of 1-5, where a higher value indicates better credit)
Direct Control Flag: [1, 1, 1, 1,] 0, 0] (where 1 indicates the device is directly controllable by the VPP, and 0 indicates it is not)
Response Cost (in 10,000 CNY/MW): []0.1, 0.3, 0.04, 0.4, 0.15, 0.5] (a higher value indicates a higher cost to participate in the demand response)`;
  
  console.log("原始文本:");
  console.log(problematicText);
  console.log();
  
  const fixedText = fixAllArrayFormats(problematicText);
  
  console.log("修复后文本:");
  console.log(fixedText);
  
  return { original: problematicText, fixed: fixedText };
}

/**
 * 验证修复结果
 */
export function validateArrayFix(original: string, fixed: string): boolean {
  // 检查是否还有错误的格式
  const errorPatterns = [
    /\]\s*[\d.]+/,  // ] 数字
    /\[\s*\]/,      // []
    /,\s*\]\s*[\d.]+/, // ,] 数字
    /\[\s*[\d.]+,\s*\]/ // [数字,]
  ];
  
  for (const pattern of errorPatterns) {
    if (pattern.test(fixed)) {
      console.log(`❌ 仍有错误格式: ${pattern}`);
      return false;
    }
  }
  
  // 检查是否是正确的数组格式
  const arrayPattern = /\[[\d.,\s]+\]/g;
  const arrays = fixed.match(arrayPattern);
  
  if (arrays) {
    console.log("✅ 数组格式正确");
    arrays.forEach((array, index) => {
      console.log(`  数组 ${index + 1}: ${array}`);
    });
    return true;
  } else {
    console.log("❌ 没有找到正确的数组格式");
    return false;
  }
} 