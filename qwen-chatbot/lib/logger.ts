/**
 * 统一日志工具
 * - debug / info：仅开发环境输出（process.env.NODE_ENV !== 'production'）
 * - warn / error：始终输出（生产中保留关键错误）
 *
 * 使用方式：import { log } from '../lib/logger';
 */

const isDev = process.env.NODE_ENV !== 'production';

export const log = {
  debug: (...args: unknown[]) => {
    if (isDev) console.log('[DEBUG]', ...args);
  },
  info: (...args: unknown[]) => {
    if (isDev) console.info('[INFO]', ...args);
  },
  warn: (...args: unknown[]) => {
    console.warn('[WARN]', ...args);
  },
  error: (...args: unknown[]) => {
    console.error('[ERROR]', ...args);
  },
};
