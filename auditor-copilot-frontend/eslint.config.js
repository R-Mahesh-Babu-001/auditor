import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

/**
 * ESLint Configuration
 *
 * This file configures ESLint for linting JavaScript and React code.
 * It uses the flat config format (ESLint v9+).
 */
export default [
  // Ignore build artifacts
  { ignores: ['dist'] },
  {
    // Apply these rules to all JS and JSX files
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      // Recommended ESLint rules
      ...js.configs.recommended.rules,
      // Recommended React Hooks rules
      ...reactHooks.configs.recommended.rules,
      // Warn about unused variables, ignoring those starting with capital letters or underscores
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
      // Warning for Fast Refresh: Only export components from files
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
]
