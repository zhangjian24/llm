import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
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
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
});
