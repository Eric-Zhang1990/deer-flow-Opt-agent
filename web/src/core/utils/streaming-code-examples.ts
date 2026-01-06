// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { processMessageToMarkdown } from "./markdown-processor";

/**
 * 流式代码片段处理示例
 * 处理被分割成多个片段的代码内容
 */

// 示例1: 你提到的具体场景
export function example1_StreamingCodeFragments() {
  console.log("=== 示例1: 流式代码片段合并 ===");
  
  // 模拟流式接收的代码片段
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

  // 合并代码片段
  const mergedCode = mergeCodeFragments(codeFragments);
  console.log("\n合并后的代码:");
  console.log(mergedCode);

  // 处理为Markdown格式
  const markdownContent = processCodeToMarkdown(mergedCode);
  console.log("\nMarkdown格式:");
  console.log(markdownContent);

  return { fragments: codeFragments, merged: mergedCode, markdown: markdownContent };
}

// 示例2: 包含JSON包装的代码片段
export function example2_JSONWrappedCode() {
  console.log("\n=== 示例2: JSON包装的代码片段 ===");
  
  const jsonFragments = [
    '{"content": "```python\\nimport json\\n\\ndef normalize(data_list, epsilon=0.0"}',
    '{"content": "1):\\n    min_val = min(data_"}',
    '{"content": "list)\\n    max_val = max(data_"}',
    '{"content": "list)\\n    if max_val == min_val:\\n        return [epsilon + (1 - epsilon)"}',
    '{"content": " * (x - min_val) / (max_val - min_val) for x in data_list]\\n    else:\\n        return [epsilon + (1 - epsilon) * (x - min_val) / (max_val - min_val) for x in data_list]\\n\\ndef main():\\n    data = [1, 2, 3, 4, 5]\\n    normalized = normalize(data)\\n    print(normalized)\\n```"}'
  ];

  console.log("JSON包装的代码片段:");
  jsonFragments.forEach((fragment, index) => {
    console.log(`片段 ${index + 1}:`, fragment);
  });

  const mergedCode = mergeJSONCodeFragments(jsonFragments);
  console.log("\n合并后的代码:");
  console.log(mergedCode);

  const markdownContent = processCodeToMarkdown(mergedCode);
  console.log("\nMarkdown格式:");
  console.log(markdownContent);

  return { fragments: jsonFragments, merged: mergedCode, markdown: markdownContent };
}

// 示例3: 混合内容（代码 + 文本）
export function example3_MixedContent() {
  console.log("\n=== 示例3: 混合内容处理 ===");
  
  const mixedFragments = [
    '{"content": "## 数据标准化函数\\n\\n以下是一个Python函数，用于数据标准化：\\n\\n```python\\nimport json\\n\\ndef normalize(data_list, epsilon=0.0"}',
    '{"content": "1):\\n    min_val = min(data_"}',
    '{"content": "list)\\n    max_val = max(data_"}',
    '{"content": "list)\\n    if max_val == min_val:\\n        return [epsilon + (1 - epsilon)"}',
    '{"content": " * (x - min_val) / (max_val - min_val) for x in data_list]\\n    else:\\n        return [epsilon + (1 - epsilon) * (x - min_val) / (max_val - min_val) for x in data_list]\\n```\\n\\n## 使用示例\\n\\n```python\\ndef main():\\n    data = [1, 2, 3, 4, 5]\\n    normalized = normalize(data)\\n    print(normalized)\\n```"}'
  ];

  console.log("混合内容片段:");
  mixedFragments.forEach((fragment, index) => {
    console.log(`片段 ${index + 1}:`, fragment);
  });

  const mergedContent = mergeMixedContent(mixedFragments);
  console.log("\n合并后的内容:");
  console.log(mergedContent);

  const markdownContent = processMessageToMarkdown(mergedContent, {
    removeCodeBlocks: false, // 保留代码块
    syntaxHighlight: true
  });
  console.log("\n处理后的Markdown:");
  console.log(markdownContent);

  return { fragments: mixedFragments, merged: mergedContent, markdown: markdownContent };
}

// 示例4: 流式处理过程
export function example4_StreamingProcess() {
  console.log("\n=== 示例4: 流式处理过程 ===");
  
  const streamingChunks = [
    '{"content": "```python\\nimport json\\n\\ndef normalize(data_list, epsilon=0.0"}',
    '{"content": "1):\\n    min_val = min(data_"}',
    '{"content": "list)\\n    max_val = max(data_"}',
    '{"content": "list)\\n    if max_val == min_val:\\n        return [epsilon + (1 - epsilon)"}',
    '{"content": " * (x - min_val) / (max_val - min_val) for x in data_list]\\n    else:\\n        return [epsilon + (1 - epsilon) * (x - min_val) / (max_val - min_val) for x in data_list]\\n```"}'
  ];

  console.log("流式处理过程:");
  let accumulatedContent = "";
  
  streamingChunks.forEach((chunk, index) => {
    // 解析JSON内容
    let content = "";
    try {
      const parsed = JSON.parse(chunk);
      content = parsed.content || parsed.code || chunk;
    } catch {
      content = chunk;
    }
    
    accumulatedContent += content;
    
    console.log(`\n片段 ${index + 1}:`);
    console.log("原始:", chunk);
    console.log("解析后:", content);
    console.log("累积内容:", accumulatedContent);
    
    // 尝试处理为Markdown
    const processed = processMessageToMarkdown(accumulatedContent, {
      removeCodeBlocks: false,
      syntaxHighlight: true
    });
    console.log("处理后:", processed);
  });

  return accumulatedContent;
}

// 工具函数：合并纯代码片段
function mergeCodeFragments(fragments: string[]): string {
  let mergedCode = "";
  
  fragments.forEach(fragment => {
    try {
      const parsed = JSON.parse(fragment);
      const code = parsed.code || parsed.content || fragment;
      mergedCode += code;
    } catch {
      // 如果不是JSON，直接使用原始内容
      mergedCode += fragment;
    }
  });
  
  return mergedCode;
}

// 工具函数：合并JSON包装的代码片段
function mergeJSONCodeFragments(fragments: string[]): string {
  let mergedContent = "";
  
  fragments.forEach(fragment => {
    try {
      const parsed = JSON.parse(fragment);
      const content = parsed.content || parsed.code || fragment;
      mergedContent += content;
    } catch {
      mergedContent += fragment;
    }
  });
  
  return mergedContent;
}

// 工具函数：合并混合内容
function mergeMixedContent(fragments: string[]): string {
  let mergedContent = "";
  
  fragments.forEach(fragment => {
    try {
      const parsed = JSON.parse(fragment);
      const content = parsed.content || parsed.code || fragment;
      mergedContent += content;
    } catch {
      mergedContent += fragment;
    }
  });
  
  return mergedContent;
}

// 工具函数：处理代码为Markdown格式
function processCodeToMarkdown(code: string): string {
  // 检测代码语言
  const language = detectCodeLanguage(code);
  
  // 转义代码中的特殊字符
  const escapedCode = code
    .replace(/\\n/g, '\n')  // 处理转义的换行符
    .replace(/\\"/g, '"')   // 处理转义的引号
    .replace(/\\\\/g, '\\'); // 处理转义的反斜杠
  
  return `\`\`\`${language}\n${escapedCode}\n\`\`\``;
}

// 工具函数：检测代码语言
function detectCodeLanguage(code: string): string {
  const firstLine = code.trim().split('\n')[0];
  
  if (firstLine.includes('import ') || firstLine.includes('def ') || firstLine.includes('class ')) {
    return 'python';
  }
  if (firstLine.includes('function') || firstLine.includes('const ') || firstLine.includes('let ')) {
    return 'javascript';
  }
  if (firstLine.includes('public class') || firstLine.includes('private ') || firstLine.includes('import ')) {
    return 'java';
  }
  if (firstLine.includes('<?php') || firstLine.includes('function ')) {
    return 'php';
  }
  if (firstLine.includes('package ') || firstLine.includes('import ')) {
    return 'go';
  }
  if (firstLine.includes('fn ') || firstLine.includes('let ') || firstLine.includes('struct ')) {
    return 'rust';
  }
  
  return 'text';
}

// 示例5: 实际应用场景
export function example5_RealWorldScenario() {
  console.log("\n=== 示例5: 实际应用场景 ===");
  
  // 模拟从AI模型接收的流式响应
  const realWorldFragments = [
    '{"content": "根据你的需求，我为你编写了一个数据标准化函数：\\n\\n```python\\nimport json\\n\\ndef normalize(data_list, epsilon=0.0"}',
    '{"content": "1):\\n    min_val = min(data_"}',
    '{"content": "list)\\n    max_val = max(data_"}',
    '{"content": "list)\\n    if max_val == min_val:\\n        return [epsilon + (1 - epsilon)"}',
    '{"content": " * (x - min_val) / (max_val - min_val) for x in data_list]\\n    else:\\n        return [epsilon + (1 - epsilon) * (x - min_val) / (max_val - min_val) for x in data_list]\\n```\\n\\n## 函数说明\\n\\n这个函数实现了Min-Max标准化，将数据缩放到[epsilon, 1]范围内。"}'
  ];

  console.log("实际场景的代码片段:");
  realWorldFragments.forEach((fragment, index) => {
    console.log(`片段 ${index + 1}:`, fragment);
  });

  const mergedContent = mergeMixedContent(realWorldFragments);
  console.log("\n合并后的内容:");
  console.log(mergedContent);

  const markdownContent = processMessageToMarkdown(mergedContent, {
    removeCodeBlocks: false,
    syntaxHighlight: true
  });
  console.log("\n最终Markdown:");
  console.log(markdownContent);

  return { fragments: realWorldFragments, merged: mergedContent, markdown: markdownContent };
}

// 运行所有示例
export function runAllStreamingCodeExamples() {
  console.log("🚀 开始运行流式代码片段处理示例\n");
  
  example1_StreamingCodeFragments();
  example2_JSONWrappedCode();
  example3_MixedContent();
  example4_StreamingProcess();
  example5_RealWorldScenario();
  
  console.log("\n✅ 所有流式代码示例运行完成");
} 