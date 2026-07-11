/**
 * Context Manager - Manages code context for AI requests
 * Handles context window optimization and token counting
 */

import type { CodeContext, SymbolInfo } from './types.js';
import { TokenCounter } from './token-counter.js';

interface ContextWindow {
  maxTokens: number;
  usedTokens: number;
  items: ContextItem[];
}

interface ContextItem {
  type: 'code' | 'symbol' | 'file' | 'instruction';
  content: string;
  tokens: number;
  priority: number;
  source?: string;
}

export class ContextManager {
  private tokenCounter: TokenCounter;
  private defaultMaxTokens: number = 4096;

  constructor(maxTokens?: number) {
    this.tokenCounter = new TokenCounter();
    if (maxTokens) {
      this.defaultMaxTokens = maxTokens;
    }
  }

  /**
   * Build optimized context from code context
   */
  async buildContext(codeContext: CodeContext): Promise<string> {
    const window: ContextWindow = {
      maxTokens: this.defaultMaxTokens,
      usedTokens: 0,
      items: [],
    };

    // Add high-priority items first
    if (codeContext.code) {
      this.addItem(window, {
        type: 'code',
        content: codeContext.code,
        priority: 10,
        source: codeContext.filePath,
      });
    }

    // Add symbols
    if (codeContext.symbols) {
      for (const symbol of codeContext.symbols) {
        this.addItem(window, {
          type: 'symbol',
          content: this.formatSymbol(symbol),
          priority: 8,
        });
      }
    }

    // Add recent files
    if (codeContext.recentFiles) {
      for (const file of codeContext.recentFiles.slice(0, 5)) {
        this.addItem(window, {
          type: 'file',
          content: `File: ${file}`,
          priority: 5,
        });
      }
    }

    // Build context string
    return this.buildContextString(window);
  }

  /**
   * Count tokens in a string
   */
  countTokens(text: string): number {
    return this.tokenCounter.count(text);
  }

  /**
   * Check if text fits in remaining context
   */
  fitsInContext(text: string, currentUsed: number): boolean {
    const tokens = this.countTokens(text);
    return currentUsed + tokens <= this.defaultMaxTokens;
  }

  private addItem(window: ContextWindow, item: Omit<ContextItem, 'tokens'>): void {
    const tokens = this.countTokens(item.content);
    
    // Check if we have space
    if (window.usedTokens + tokens > window.maxTokens) {
      // Try to make room by removing low-priority items
      this.makeRoom(window, tokens);
    }

    if (window.usedTokens + tokens <= window.maxTokens) {
      window.items.push({ ...item, tokens });
      window.usedTokens += tokens;
    }
  }

  private makeRoom(window: ContextWindow, neededTokens: number): void {
    // Sort by priority (lowest first)
    window.items.sort((a, b) => a.priority - b.priority);

    // Remove items until we have enough space
    while (
      window.items.length > 0 &&
      window.usedTokens + neededTokens > window.maxTokens
    ) {
      const removed = window.items.shift();
      if (removed) {
        window.usedTokens -= removed.tokens;
      }
    }
  }

  private formatSymbol(symbol: SymbolInfo): string {
    return `${symbol.type} ${symbol.name} [lines ${symbol.range.start}-${symbol.range.end}]`;
  }

  private buildContextString(window: ContextWindow): string {
    const parts: string[] = [];

    for (const item of window.items) {
      switch (item.type) {
        case 'code':
          parts.push(`\n\`\`\`${this.getLanguage(item.source)}\n${item.content}\n\`\`\``);
          break;
        case 'symbol':
          parts.push(`\n${item.content}`);
          break;
        case 'file':
          parts.push(`\n${item.content}`);
          break;
      }
    }

    return parts.join('\n');
  }

  private getLanguage(filePath?: string): string {
    if (!filePath) return '';
    const ext = filePath.split('.').pop()?.toLowerCase();
    const languageMap: Record<string, string> = {
      ts: 'typescript',
      tsx: 'typescript',
      js: 'javascript',
      jsx: 'javascript',
      py: 'python',
      java: 'java',
      cpp: 'cpp',
      c: 'c',
      rs: 'rust',
      go: 'go',
      rb: 'ruby',
      php: 'php',
    };
    return languageMap[ext || ''] || '';
  }
}
