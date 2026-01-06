// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 流式代码处理器
 * 专门处理被分割成多个片段的代码内容
 */

export interface StreamingCodeOptions {
  /** 是否自动检测代码语言 */
  autoDetectLanguage?: boolean;
  /** 是否处理转义字符 */
  unescapeCharacters?: boolean;
  /** 是否包装为Markdown代码块 */
  wrapAsCodeBlock?: boolean;
  /** 默认代码语言 */
  defaultLanguage?: string;
}

/**
 * 处理流式代码片段
 */
export function processStreamingCode(
  content: string,
  options: StreamingCodeOptions = {}
): string {
  const {
    autoDetectLanguage = true,
    unescapeCharacters = true,
    wrapAsCodeBlock = true,
    defaultLanguage = 'text'
  } = options;

  if (!content) return content;

  try {
    // 尝试解析JSON格式的内容
    const parsed = JSON.parse(content);
    const codeContent = parsed.code || parsed.content || content;
    
    let processedCode = codeContent;

    // 处理转义字符
    if (unescapeCharacters) {
      processedCode = unescapeCodeContent(processedCode);
    }

    // 如果是代码片段且需要包装为代码块
    if (parsed.code && wrapAsCodeBlock) {
      const language = autoDetectLanguage 
        ? detectCodeLanguage(processedCode) 
        : defaultLanguage;
      
      return `\`\`\`${language}\n${processedCode}\n\`\`\``;
    }
    
    return processedCode;
  } catch {
    // 如果不是JSON格式，直接返回原内容
    return content;
  }
}

/**
 * 合并多个流式代码片段
 */
export function mergeStreamingCodeFragments(
  fragments: string[],
  options: StreamingCodeOptions = {}
): string {
  let mergedCode = "";
  
  fragments.forEach(fragment => {
    const processedFragment = processStreamingCode(fragment, {
      ...options,
      wrapAsCodeBlock: false // 在合并时不包装，最后统一包装
    });
    mergedCode += processedFragment;
  });

  // 最终处理
  if (options.wrapAsCodeBlock !== false) {
    const language = options.autoDetectLanguage !== false 
      ? detectCodeLanguage(mergedCode) 
      : (options.defaultLanguage || 'text');
    
    return `\`\`\`${language}\n${mergedCode}\n\`\`\``;
  }
  
  return mergedCode;
}

/**
 * 处理混合内容（代码 + 文本）
 */
export function processMixedContent(
  content: string,
  options: StreamingCodeOptions = {}
): string {
  if (!content) return content;

  try {
    const parsed = JSON.parse(content);
    const mixedContent = parsed.content || parsed.code || content;
    
    let processedContent = mixedContent;

    // 处理转义字符
    if (options.unescapeCharacters !== false) {
      processedContent = unescapeCodeContent(processedContent);
    }

    return processedContent;
  } catch {
    return content;
  }
}

/**
 * 转义代码内容中的特殊字符
 */
function unescapeCodeContent(code: string): string {
  return code
    .replace(/\\n/g, '\n')  // 处理转义的换行符
    .replace(/\\"/g, '"')   // 处理转义的引号
    .replace(/\\\\/g, '\\') // 处理转义的反斜杠
    .replace(/\\t/g, '\t')  // 处理转义的制表符
    .replace(/\\r/g, '\r'); // 处理转义的回车符
}

/**
 * 检测代码语言
 */
function detectCodeLanguage(code: string): string {
  const lines = code.trim().split('\n');
  const firstLine = lines[0] || '';
  
  // Python
  if (firstLine.includes('import ') || firstLine.includes('def ') || firstLine.includes('class ') || 
      firstLine.includes('from ') || firstLine.includes('if __name__')) {
    return 'python';
  }
  
  // JavaScript/TypeScript
  if (firstLine.includes('function') || firstLine.includes('const ') || firstLine.includes('let ') ||
      firstLine.includes('var ') || firstLine.includes('export ') || firstLine.includes('import ')) {
    return 'javascript';
  }
  
  // Java
  if (firstLine.includes('public class') || firstLine.includes('private ') || firstLine.includes('import ') ||
      firstLine.includes('package ') || firstLine.includes('public static')) {
    return 'java';
  }
  
  // PHP
  if (firstLine.includes('<?php') || firstLine.includes('function ') || firstLine.includes('class ')) {
    return 'php';
  }
  
  // Go
  if (firstLine.includes('package ') || firstLine.includes('import ') || firstLine.includes('func ')) {
    return 'go';
  }
  
  // Rust
  if (firstLine.includes('fn ') || firstLine.includes('let ') || firstLine.includes('struct ') ||
      firstLine.includes('impl ') || firstLine.includes('use ')) {
    return 'rust';
  }
  
  // C/C++
  if (firstLine.includes('#include') || firstLine.includes('int main') || firstLine.includes('class ') ||
      firstLine.includes('namespace ') || firstLine.includes('using namespace')) {
    return 'cpp';
  }
  
  // C#
  if (firstLine.includes('using ') || firstLine.includes('namespace ') || firstLine.includes('public class') ||
      firstLine.includes('private ') || firstLine.includes('static void')) {
    return 'csharp';
  }
  
  // Ruby
  if (firstLine.includes('require ') || firstLine.includes('def ') || firstLine.includes('class ') ||
      firstLine.includes('module ')) {
    return 'ruby';
  }
  
  // Shell/Bash
  if (firstLine.includes('#!/') || firstLine.includes('echo ') || firstLine.includes('if [') ||
      firstLine.includes('for ') || firstLine.includes('while ')) {
    return 'bash';
  }
  
  // SQL
  if (firstLine.includes('SELECT ') || firstLine.includes('INSERT ') || firstLine.includes('UPDATE ') ||
      firstLine.includes('CREATE ') || firstLine.includes('DROP ')) {
    return 'sql';
  }
  
  // HTML
  if (firstLine.includes('<!DOCTYPE') || firstLine.includes('<html') || firstLine.includes('<div') ||
      firstLine.includes('<p>') || firstLine.includes('<span')) {
    return 'html';
  }
  
  // CSS
  if (firstLine.includes('{') && (firstLine.includes(':') || firstLine.includes('color') || firstLine.includes('font'))) {
    return 'css';
  }
  
  // JSON
  if (firstLine.includes('{') || firstLine.includes('[')) {
    try {
      JSON.parse(code);
      return 'json';
    } catch {
      // 不是有效的JSON
    }
  }
  
  return 'text';
}

/**
 * 验证代码片段的完整性
 */
export function validateCodeFragment(fragment: string): {
  isValid: boolean;
  isComplete: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  let isComplete = true;

  try {
    const parsed = JSON.parse(fragment);
    const codeContent = parsed.code || parsed.content || fragment;
    
    // 检查是否有未闭合的括号
    const openBrackets = (codeContent.match(/\(/g) || []).length;
    const closeBrackets = (codeContent.match(/\)/g) || []).length;
    if (openBrackets !== closeBrackets) {
      errors.push(`不匹配的括号: 开始${openBrackets}个，结束${closeBrackets}个`);
      isComplete = false;
    }

    // 检查是否有未闭合的引号
    const singleQuotes = (codeContent.match(/'/g) || []).length;
    const doubleQuotes = (codeContent.match(/"/g) || []).length;
    if (singleQuotes % 2 !== 0) {
      errors.push('未闭合的单引号');
      isComplete = false;
    }
    if (doubleQuotes % 2 !== 0) {
      errors.push('未闭合的双引号');
      isComplete = false;
    }

    // 检查是否有未闭合的代码块
    const codeBlockStarts = (codeContent.match(/```/g) || []).length;
    if (codeBlockStarts % 2 !== 0) {
      errors.push('未闭合的代码块');
      isComplete = false;
    }

  } catch (error) {
    errors.push('无效的JSON格式');
    isComplete = false;
  }

  return {
    isValid: errors.length === 0,
    isComplete,
    errors
  };
}

/**
 * 格式化代码内容
 */
export function formatCodeContent(code: string, language?: string): string {
  let formattedCode = code.trim();
  
  // 根据语言进行特定格式化
  switch (language) {
    case 'python':
      // Python特定的格式化
      formattedCode = formattedCode.replace(/\n{3,}/g, '\n\n'); // 移除多余的空行
      break;
    case 'javascript':
    case 'typescript':
      // JavaScript/TypeScript特定的格式化
      formattedCode = formattedCode.replace(/;\s*\n/g, ';\n'); // 规范化分号
      break;
    case 'json':
      try {
        // 格式化JSON
        const parsed = JSON.parse(formattedCode);
        formattedCode = JSON.stringify(parsed, null, 2);
      } catch {
        // 如果解析失败，保持原样
      }
      break;
    default:
      // 通用格式化
      formattedCode = formattedCode.replace(/\n{3,}/g, '\n\n'); // 移除多余的空行
  }
  
  return formattedCode;
}

/**
 * 示例：处理你提到的具体场景
 */
export function processYourExample(): void {
  console.log("=== 处理你提到的流式代码片段示例 ===");
  
  const codeFragments = [
    '{"code": "import json\\n\\ndef normalize(data_list, epsilon=0.0"}',
    '{"code": "1):\\n    min_val = min(data_"}',
    '{"code": "list)\\n    max_val = max(data_"}',
    '{"code": "list)\\n    if max_val == min_val:\\n        return [epsilon + (1 - epsilon)"}',
    '{"code": " * (x - min_val) / (max_val - min_val) for x in data_list]\\n    else:\\n        return [epsilon + (1 - epsilon) * (x - min_val) / (max_val - min_val) for x in data_list]\\n\\ndef main():\\n    data = [1, 2, 3, 4, 5]\\n    normalized = normalize(data)\\n    print(normalized)"}'
  ];

  console.log("原始代码片段:");
  codeFragments.forEach((fragment, index) => {
    console.log(`片段 ${index + 1}:`, fragment);
  });

  // 合并并处理代码片段
  const mergedCode = mergeStreamingCodeFragments(codeFragments, {
    autoDetectLanguage: true,
    unescapeCharacters: true,
    wrapAsCodeBlock: true
  });

  console.log("\n处理后的完整代码:");
  console.log(mergedCode);

  // 验证代码完整性
  const validation = validateCodeFragment(codeFragments[codeFragments.length - 1]);
  console.log("\n代码验证结果:", validation);
} 