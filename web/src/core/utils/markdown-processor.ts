// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * Markdown内容处理器
 * 用于处理和格式化消息内容为Markdown格式
 */

export interface MarkdownProcessingOptions {
  /** 是否启用自动修复 */
  autoFix?: boolean;
  /** 是否处理数学公式 */
  processMath?: boolean;
  /** 是否移除多余的代码块标记 */
  removeCodeBlocks?: boolean;
  /** 是否启用语法高亮 */
  syntaxHighlight?: boolean;
}

/**
 * 处理消息内容为Markdown格式
 */
export function processMessageToMarkdown(
  content: string,
  options: MarkdownProcessingOptions = {}
): string {
  const {
    autoFix = true,
    processMath = true,
    removeCodeBlocks = true,
    syntaxHighlight = true,
  } = options;

  if (!content) return content;

  let processedContent = content;

  // 1. 自动修复不完整的Markdown语法
  if (autoFix) {
    processedContent = autoFixMarkdown(processedContent);
  }

  // 2. 处理数学公式语法
  if (processMath) {
    processedContent = processKatexInMarkdown(processedContent) || processedContent;
  }

  // 3. 移除多余的代码块标记
  if (removeCodeBlocks) {
    const cleanedContent = dropMarkdownQuote(processedContent);
    processedContent = cleanedContent || processedContent;
  }

  // 4. 添加语法高亮支持
  if (syntaxHighlight) {
    processedContent = addSyntaxHighlighting(processedContent);
  }

  return processedContent;
}

/**
 * 自动修复不完整的Markdown语法
 */
function autoFixMarkdown(markdown: string): string {
  let fixedMarkdown = markdown;

  // 修复不完整的图片语法
  fixedMarkdown = fixedMarkdown.replace(
    /!\[([^\]]*)\]\(([^)]*)$/g,
    (match: string, altText: string, url: string): string => {
      return `![${altText}](${url})`;
    }
  );

  // 修复不完整的链接语法
  fixedMarkdown = fixedMarkdown.replace(
    /\[([^\]]*)\]\(([^)]*)$/g,
    (match: string, linkText: string, url: string): string => {
      return `[${linkText}](${url})`;
    }
  );

  // 修复不完整的图片语法（只有开始标记）
  fixedMarkdown = fixedMarkdown.replace(
    /!\[([^\]]*)$/g,
    (match: string, altText: string): string => {
      return `![${altText}]`;
    }
  );

  // 修复不完整的链接语法（只有开始标记）
  fixedMarkdown = fixedMarkdown.replace(
    /\[([^\]]*)$/g,
    (match: string, linkText: string): string => {
      return `[${linkText}]`;
    }
  );

  // 修复缺少右括号的图片和链接
  fixedMarkdown = fixedMarkdown.replace(
    /!\[([^\]]*)\]\(([^)]*)$/g,
    (match: string, altText: string, url: string): string => {
      return `![${altText}](${url})`;
    }
  );

  fixedMarkdown = fixedMarkdown.replace(
    /\[([^\]]*)\]\(([^)]*)$/g,
    (match: string, linkText: string, url: string): string => {
      return `[${linkText}](${url})`;
    }
  );

  return fixedMarkdown;
}

/**
 * 处理数学公式语法
 */
function processKatexInMarkdown(markdown?: string | null): string | null {
  if (!markdown) return markdown;

  return markdown
    .replace(/\\\\\[/g, "$$") // Replace '\\[' with '$$'
    .replace(/\\\\\]/g, "$$") // Replace '\\]' with '$$'
    .replace(/\\\\\(/g, "$") // Replace '\\(' with '$'
    .replace(/\\\\\)/g, "$") // Replace '\\)' with '$'
    .replace(/\\\[/g, "$$") // Replace '\[' with '$$'
    .replace(/\\\]/g, "$$") // Replace '\]' with '$$'
    .replace(/\\\(/g, "$") // Replace '\(' with '$'
    .replace(/\\\)/g, "$"); // Replace '\)' with '$'
}

/**
 * 移除多余的代码块标记
 */
function dropMarkdownQuote(markdown?: string | null): string | null {
  if (!markdown) return null;

  const patternsToRemove = [
    { prefix: "```markdown\n", suffix: "\n```", prefixLen: 12 },
    { prefix: "```text\n", suffix: "\n```", prefixLen: 8 },
    { prefix: "```\n", suffix: "\n```", prefixLen: 4 },
  ];

  let result = markdown;

  // 处理开头的不完整代码块
  for (const { prefix, suffix, prefixLen } of patternsToRemove) {
    if (result.startsWith(prefix) && !result.endsWith(suffix)) {
      result = result.slice(prefixLen);
      break;
    }
  }

  // 处理完整的代码块
  let changed = true;
  while (changed) {
    changed = false;

    for (const { prefix, suffix, prefixLen } of patternsToRemove) {
      let startIndex = 0;
      while ((startIndex = result.indexOf(prefix, startIndex)) !== -1) {
        const endIndex = result.indexOf(suffix, startIndex + prefixLen);
        if (endIndex !== -1) {
          // 只移除完全匹配的代码块
          const before = result.slice(0, startIndex);
          const content = result.slice(startIndex + prefixLen, endIndex);
          const after = result.slice(endIndex + suffix.length);
          result = before + content + after;
          changed = true;
          startIndex = before.length + content.length;
        } else {
          startIndex += prefixLen;
        }
      }
    }
  }

  return result;
}

/**
 * 添加语法高亮支持
 */
function addSyntaxHighlighting(markdown: string): string {
  // 为代码块添加语言标识符（如果没有的话）
  return markdown.replace(
    /```\n([\s\S]*?)```/g,
    (match: string, code: string) => {
      // 尝试检测代码语言
      const language = detectCodeLanguage(code);
      return `\`\`\`${language}\n${code}\n\`\`\``;
    }
  );
}

/**
 * 检测代码语言
 */
function detectCodeLanguage(code: string): string {
  // 简单的语言检测逻辑
  const firstLine = code.trim().split('\n')[0];
  
  if (firstLine.includes('function') || firstLine.includes('const') || firstLine.includes('let')) {
    return 'javascript';
  }
  if (firstLine.includes('def ') || firstLine.includes('import ') || firstLine.includes('class ')) {
    return 'python';
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

/**
 * 验证Markdown语法
 */
export function validateMarkdown(markdown: string): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  // 检查不匹配的括号
  const openBrackets = (markdown.match(/\[/g) || []).length;
  const closeBrackets = (markdown.match(/\]/g) || []).length;
  if (openBrackets !== closeBrackets) {
    errors.push(`不匹配的方括号: 开始${openBrackets}个，结束${closeBrackets}个`);
  }

  // 检查不匹配的圆括号
  const openParens = (markdown.match(/\(/g) || []).length;
  const closeParens = (markdown.match(/\)/g) || []).length;
  if (openParens !== closeParens) {
    errors.push(`不匹配的圆括号: 开始${openParens}个，结束${closeParens}个`);
  }

  // 检查不匹配的代码块
  const codeBlockStarts = (markdown.match(/```/g) || []).length;
  if (codeBlockStarts % 2 !== 0) {
    errors.push('不匹配的代码块标记');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * 格式化Markdown内容
 */
export function formatMarkdown(markdown: string): string {
  let formatted = markdown;

  // 确保标题前后有空行
  formatted = formatted.replace(/([^\n])\n(#+ )/g, '$1\n\n$2');
  formatted = formatted.replace(/(#+ .*)\n([^\n])/g, '$1\n\n$2');

  // 确保列表项前后有空行
  formatted = formatted.replace(/([^\n])\n([*+-] )/g, '$1\n\n$2');
  formatted = formatted.replace(/([^\n])\n(\d+\. )/g, '$1\n\n$2');

  // 确保代码块前后有空行
  formatted = formatted.replace(/([^\n])\n```/g, '$1\n\n```');
  formatted = formatted.replace(/```\n([^\n])/g, '```\n\n$1');

  return formatted;
} 