// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { 
  processMessageToMarkdown, 
  validateMarkdown, 
  formatMarkdown 
} from "./markdown-processor";

/**
 * Markdown处理使用示例
 */

// 示例1: 基础Markdown处理
export function basicMarkdownExample() {
  const rawContent = `
# 这是一个标题

这是一段普通文本，包含**粗体**和*斜体*。

## 代码示例
\`\`\`
function hello() {
  console.log("Hello World!");
}
\`\`\`

## 数学公式
这是一个数学公式: $E = mc^2$

## 链接和图片
这是一个[链接](https://example.com)
![图片](https://example.com/image.jpg)
  `;

  const processedContent = processMessageToMarkdown(rawContent);
  console.log("处理后的Markdown:", processedContent);
  
  return processedContent;
}

// 示例2: 修复不完整的Markdown
export function fixIncompleteMarkdownExample() {
  const incompleteContent = `
# 不完整的Markdown

这是一个不完整的[链接
这是一个不完整的![图片

\`\`\`markdown
# 被错误包装的内容
\`\`\`
  `;

  const processedContent = processMessageToMarkdown(incompleteContent);
  console.log("修复后的内容:", processedContent);
  
  return processedContent;
}

// 示例3: 数学公式处理
export function mathFormulaExample() {
  const mathContent = `
# 数学公式示例

行内公式: \\(x^2 + y^2 = z^2\\)

块级公式:
\\[
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
\\]

使用LaTeX语法:
$\\frac{a}{b} = \\frac{c}{d}$
  `;

  const processedContent = processMessageToMarkdown(mathContent);
  console.log("数学公式处理结果:", processedContent);
  
  return processedContent;
}

// 示例4: 代码语言检测
export function codeLanguageDetectionExample() {
  const codeContent = `
# 代码示例

JavaScript代码:
\`\`\`
function add(a, b) {
  return a + b;
}
\`\`\`

Python代码:
\`\`\`
def add(a, b):
    return a + b
\`\`\`

Java代码:
\`\`\`
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
\`\`\`
  `;

  const processedContent = processMessageToMarkdown(codeContent);
  console.log("代码语言检测结果:", processedContent);
  
  return processedContent;
}

// 示例5: Markdown验证
export function markdownValidationExample() {
  const invalidContent = `
# 无效的Markdown

这是一个不匹配的[链接
这是一个不匹配的(括号

\`\`\`markdown
# 不完整的代码块
  `;

  const validation = validateMarkdown(invalidContent);
  console.log("验证结果:", validation);
  
  if (!validation.isValid) {
    console.log("发现以下错误:");
    validation.errors.forEach(error => console.log(`- ${error}`));
  }
  
  return validation;
}

// 示例6: Markdown格式化
export function markdownFormattingExample() {
  const unformattedContent = `
# 标题1
这是一些文本
## 标题2
更多文本
- 列表项1
- 列表项2
\`\`\`
代码块
\`\`\`
  `;

  const formattedContent = formatMarkdown(unformattedContent);
  console.log("格式化后的内容:", formattedContent);
  
  return formattedContent;
}

// 示例7: 在消息处理中使用
export function messageProcessingExample() {
  // 模拟从AI模型接收的原始内容
  const aiResponse = `
根据你的问题，我建议以下解决方案：

## 1. 问题分析
首先需要分析问题的根本原因。

## 2. 解决方案
\`\`\`javascript
// 示例代码
const solution = {
  step1: "分析问题",
  step2: "制定方案",
  step3: "实施解决"
};
\`\`\`

## 3. 数学计算
使用公式: $\\sum_{i=1}^{n} x_i = \\frac{n(n+1)}{2}$

## 4. 参考资料
更多信息请参考[官方文档](https://docs.example.com
  `;

  // 处理消息内容
  const processedMessage = processMessageToMarkdown(aiResponse, {
    autoFix: true,
    processMath: true,
    removeCodeBlocks: false, // 保留代码块
    syntaxHighlight: true,
  });

  console.log("处理后的消息:", processedMessage);
  
  // 验证Markdown语法
  const validation = validateMarkdown(processedMessage);
  console.log("语法验证:", validation);
  
  return {
    original: aiResponse,
    processed: processedMessage,
    validation,
  };
}

// 示例8: 流式消息处理
export function streamingMessageExample() {
  // 模拟流式接收的消息片段
  const messageChunks = [
    "# 这是一个",
    "# 这是一个标题\n\n",
    "# 这是一个标题\n\n这是第一段",
    "# 这是一个标题\n\n这是第一段内容。\n\n",
    "# 这是一个标题\n\n这是第一段内容。\n\n## 子标题\n\n",
    "# 这是一个标题\n\n这是第一段内容。\n\n## 子标题\n\n这是第二段内容。",
  ];

  let accumulatedContent = "";
  
  messageChunks.forEach((chunk, index) => {
    accumulatedContent += chunk;
    
    // 对累积的内容进行Markdown处理
    const processedContent = processMessageToMarkdown(accumulatedContent, {
      autoFix: true,
      processMath: true,
      removeCodeBlocks: true,
      syntaxHighlight: true,
    });
    
    console.log(`片段 ${index + 1}:`, processedContent);
  });
  
  return accumulatedContent;
} 