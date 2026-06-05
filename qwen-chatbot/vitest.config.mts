import { defineConfig } from 'vitest/config';
import path from 'node:path';

export default defineConfig({
  test: {
    include: [
      'lib/**/*.test.{ts,tsx}',
      'components/**/*.test.{ts,tsx}',
      'pages/**/*.test.{ts,tsx}',
      'contexts/**/*.test.{ts,tsx}',
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
      include: ['lib/**', 'components/**', 'contexts/**', 'pages/**'],
      exclude: ['**/*.test.*', '**/*.spec.*', '**/node_modules/**', '**/.next/**'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '~': path.resolve(__dirname, '.'),
    },
  },
});
