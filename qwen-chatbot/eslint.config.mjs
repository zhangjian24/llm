import next from 'eslint-config-next';

export default [
  ...next,
  {
    rules: {
      'no-console': 'off',
      'react-hooks/exhaustive-deps': 'warn',
      // React 19 新规则在原代码违反（行为 100% 不变约束下不修复，仅 warn）
      'react-hooks/set-state-in-effect': 'warn',
      'react-hooks/immutability': 'warn',
      'react-hooks/refs': 'warn',
      'import/no-anonymous-default-export': 'warn',
    },
  },
  {
    ignores: [
      'node_modules/**',
      '.next/**',
      'coverage/**',
      'playwright-report/**',
      'test-results/**',
      '**/*.test.ts',
      '**/*.test.tsx',
    ],
  },
];
