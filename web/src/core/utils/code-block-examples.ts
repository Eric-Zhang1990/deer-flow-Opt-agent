// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { processMessageToMarkdown } from "./markdown-processor";

/**
 * 代码块包装处理示例
 * 展示"移除多余的代码块包装"功能处理的具体内容
 */

// 示例1: AI模型错误地将普通文本包装在代码块中
export function example1_AIWrappedContent() {
  console.log("=== 示例1: AI模型错误包装普通文本 ===");
  
  const aiResponse = `\`\`\`markdown
# 这是一个标题

这是一段普通的文本内容，包含**粗体**和*斜体*。

## 子标题
- 列表项1
- 列表项2

这是一个[链接](https://example.com)
\`\`\``;

  console.log("原始内容:");
  console.log(aiResponse);
  console.log("\n处理后:");
  
  const processed = processMessageToMarkdown(aiResponse, {
    removeCodeBlocks: true
  });
  console.log(processed);
  
  return processed;
}

// 示例2: 不完整的代码块包装
export function example2_IncompleteCodeBlock() {
  console.log("\n=== 示例2: 不完整的代码块包装 ===");
  
  const incompleteContent = `\`\`\`text
这是一些文本内容
但是代码块没有正确关闭
`;

  console.log("原始内容:");
  console.log(incompleteContent);
  console.log("\n处理后:");
  
  const processed = processMessageToMarkdown(incompleteContent, {
    removeCodeBlocks: true
  });
  console.log(processed);
  
  return processed;
}

// 示例3: 多层嵌套的代码块包装
export function example3_NestedCodeBlocks() {
  console.log("\n=== 示例3: 多层嵌套的代码块包装 ===");
  
  const nestedContent = `\`\`\`markdown
# 外层包装

\`\`\`javascript
function example() {
  console.log("内层代码");
}
\`\`\`

## 更多内容
\`\`\``;

  console.log("原始内容:");
  console.log(nestedContent);
  console.log("\n处理后:");
  
  const processed = processMessageToMarkdown(nestedContent, {
    removeCodeBlocks: true
  });
  console.log(processed);
  
  return processed;
}

// 示例4: 混合内容（需要保留的代码块 vs 需要移除的包装）
export function example4_MixedContent() {
  console.log("\n=== 示例4: 混合内容处理 ===");
  
  const mixedContent = `\`\`\`markdown
# 这是被错误包装的Markdown内容

下面是一个真正的代码示例：

\`\`\`javascript
function calculateSum(a, b) {
  return a + b;
}
\`\`\`

## 更多文本内容
- 列表项1
- 列表项2

\`\`\`python
# 另一个真正的代码块
def multiply(x, y):
    return x * y
\`\`\`

结束文本。
\`\`\``;

  console.log("原始内容:");
  console.log(mixedContent);
  console.log("\n处理后:");
  
  const processed = processMessageToMarkdown(mixedContent, {
    removeCodeBlocks: true
  });
  console.log(processed);
  
  return processed;
}

// 示例5: 流式消息中的代码块包装问题
export function example5_StreamingIssues() {
  console.log("\n=== 示例5: 流式消息中的代码块包装问题 ===");
  
  // 模拟流式接收的消息片段
  const streamingChunks = [
    "```markdown\n",
    "```markdown\n# 标题",
    "```markdown\n# 标题\n\n内容",
    "```markdown\n# 标题\n\n内容\n\n## 子标题",
    "```markdown\n# 标题\n\n内容\n\n## 子标题\n\n更多内容",
    "```markdown\n# 标题\n\n内容\n\n## 子标题\n\n更多内容\n```"
  ];

  console.log("流式接收的片段:");
  streamingChunks.forEach((chunk, index) => {
    console.log(`片段 ${index + 1}:`, JSON.stringify(chunk));
  });

  console.log("\n累积处理过程:");
  let accumulated = "";
  streamingChunks.forEach((chunk, index) => {
    accumulated += chunk;
    const processed = processMessageToMarkdown(accumulated, {
      removeCodeBlocks: true
    });
    console.log(`\n片段 ${index + 1} 处理后:`);
    console.log(processed);
  });
  
  return accumulated;
}

// 示例6: 不同语言的代码块包装
export function example6_DifferentLanguages() {
  console.log("\n=== 示例6: 不同语言的代码块包装 ===");
  
  const examples = [
    {
      name: "markdown包装",
      content: "```markdown\n# 标题\n内容\n```"
    },
    {
      name: "text包装", 
      content: "```text\n普通文本内容\n```"
    },
    {
      name: "无语言标识包装",
      content: "```\n内容\n```"
    }
  ];

  examples.forEach(example => {
    console.log(`\n${example.name}:`);
    console.log("原始:", example.content);
    
    const processed = processMessageToMarkdown(example.content, {
      removeCodeBlocks: true
    });
    console.log("处理后:", processed);
  });
  
  return examples;
}

// 示例7: 实际AI响应中的问题
export function example7_RealAIResponse() {
  console.log("\n=== 示例7: 实际AI响应中的问题 ===");
  
  const realAIResponse = `根据你的问题，我提供以下解决方案：

\`\`\`markdown
## 解决方案步骤

1. **分析问题**
   - 检查错误日志
   - 确认问题范围

2. **制定计划**
   - 确定修复策略
   - 准备测试方案

3. **实施修复**
   - 修改代码
   - 运行测试

## 代码示例

\`\`\`javascript
function fixIssue() {
  console.log("修复问题");
  return "success";
}
\`\`\`

## 注意事项
- 备份重要数据
- 在测试环境验证
\`\`\`

希望这个解决方案对你有帮助！`;

  console.log("原始AI响应:");
  console.log(realAIResponse);
  console.log("\n处理后:");
  
  const processed = processMessageToMarkdown(realAIResponse, {
    removeCodeBlocks: true
  });
  console.log(processed);
  
  return processed;
}

// 示例8: 对比处理前后的效果
export function example8_Comparison() {
  console.log("\n=== 示例8: 处理前后对比 ===");
  
  const testCases = [
    {
      name: "简单包装",
      before: "```markdown\n# 标题\n内容\n```",
      expected: "# 标题\n内容"
    },
    {
      name: "不完整包装",
      before: "```text\n内容\n",
      expected: "内容\n"
    },
    {
      name: "保留真实代码块",
      before: "```markdown\n文本\n\n```javascript\ncode\n```\n```",
      expected: "文本\n\n```javascript\ncode\n```"
    }
  ];

  testCases.forEach(testCase => {
    console.log(`\n${testCase.name}:`);
    console.log("处理前:", JSON.stringify(testCase.before));
    
    const processed = processMessageToMarkdown(testCase.before, {
      removeCodeBlocks: true
    });
    console.log("处理后:", JSON.stringify(processed));
    console.log("期望结果:", JSON.stringify(testCase.expected));
    console.log("匹配:", processed === testCase.expected ? "✅" : "❌");
  });
  
  return testCases;
}

// 运行所有示例
export function runAllCodeBlockExamples() {
  console.log("🚀 开始运行代码块包装处理示例\n");
  
  example1_AIWrappedContent();
  example2_IncompleteCodeBlock();
  example3_NestedCodeBlocks();
  example4_MixedContent();
  example5_StreamingIssues();
  example6_DifferentLanguages();
  example7_RealAIResponse();
  example8_Comparison();
  
  console.log("\n✅ 所有示例运行完成");
} 