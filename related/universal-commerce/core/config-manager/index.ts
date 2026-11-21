import * as fs from 'fs';
import * as path from 'path';

export interface ConfigLoader {
  load(filePath: string): Promise<Record<string, unknown>>;
  watch(path: string, callback: () => void): () => void;
}

export class FileSystemConfigLoader implements ConfigLoader {
  private watchers: Map<string, () => void> = new Map();
  private cache: Map<string, Record<string, unknown>> = new Map();

  async load(filePath: string): Promise<Record<string, unknown>> {
    if (this.cache.has(filePath)) {
      return this.cache.get(filePath)!;
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const config = this.parse(content, filePath);
    this.cache.set(filePath, config);
    return config;
  }

  watch(filePath: string, callback: () => void): () => void {
    this.watchers.set(filePath, callback);
    
    // Simple polling-based watch (production would use fs.watch)
    const interval = setInterval(() => {
      try {
        const mtime = fs.statSync(filePath).mtimeMs;
        const cached = this.cache.get(filePath);
        if (cached && mtime > cached.__mtime) {
          this.cache.delete(filePath);
          callback();
        }
      } catch {
        // File may have been deleted
      }
    }, 1000);

    return () => {
      this.watchers.delete(filePath);
      clearInterval(interval);
    };
  }

  private parse(content: string, ext: string): Record<string, unknown> {
    if (ext.endsWith('.yaml') || ext.endsWith('.yml')) {
      // Simple YAML parser (production: use yaml npm package)
      return this.parseYaml(content);
    }
    if (ext.endsWith('.json')) {
      return JSON.parse(content);
    }
    return {};
  }

  private parseYaml(content: string): Record<string, unknown> {
    const result: Record<string, unknown> = {};
    const lines = content.split('\n');
    let currentKey: string | null = null;

    for (const line of lines) {
      if (line.trim().startsWith('#') || !line.trim()) continue;
      
      const match = line.match(/^(\w+):\s*(.+)?/);
      if (match) {
        const [, key, value] = match;
        if (value !== undefined && value.trim()) {
          result[key] = value.trim().replace(/"/g, '');
          currentKey = null;
        } else {
          currentKey = key;
          result[key] = {};
        }
      } else if (currentKey && line.trim().startsWith('-')) {
        const items = (result[currentKey] as unknown[]) || [];
        items.push(line.trim().slice(1).trim().replace(/"/g, ''));
        result[currentKey] = items;
      }
    }

    return result;
  }
}

export const configLoader = new FileSystemConfigLoader();
