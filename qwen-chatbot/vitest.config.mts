import { defineConfig } from 'vitest/config';
import path from 'node:path';

export default defineConfig({
  test: {
    include: [
      'lib/**/*.test.{ts,tsx}',
      'components/**/*.test.{ts,tsx}',
      'pages/**/*.test.{ts,tsx}',
      'contexts/**/*.test.{ts,tsx}',
      '__tests__/**/*.test.{ts,tsx}',
    ],
    environment: 'happy-dom',
    setupFiles: ['./vitest.setup.ts'],
    globals: true,
    esbuild: {
      jsx: 'automatic',
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary', 'html'],
      reportOnFailure: true,
      all: true,
      include: [
        'lib/role-reducer.ts',
        'lib/logger.ts',
        'lib/model-options.ts',
        'lib/langchain/index.ts',
        'lib/langchain/tools.ts',
        'components/useRoleStorage.ts',
        'components/TypeWriterEffect.tsx',
        'components/MarkdownRenderer.tsx',
        'components/HistoryTable.tsx',
        'components/LoadingState.tsx',
      ],
      exclude: ['**/*.test.*', '**/*.spec.*', '**/node_modules/**', '**/.next/**', 'pages/**', 'contexts/**'],
      thresholds: {
        lines: 30,
        functions: 40,
        branches: 60,
        statements: 30,
      },
    },
  },
  resolve: {
    alias: {
      '~': path.resolve(__dirname, '.'),
    },
  },
});
