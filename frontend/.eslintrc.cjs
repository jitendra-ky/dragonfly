module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
    // vitest/jest-like globals for test files
    jest: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react-hooks/recommended',
  ],
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  plugins: ['react-hooks'],
  globals: {
    vi: 'readonly',
    describe: 'readonly',
    it: 'readonly',
    expect: 'readonly',
    beforeEach: 'readonly',
    afterEach: 'readonly',
    global: 'readonly',
  },
  overrides: [
    {
      files: ['**/*.test.{js,jsx,ts,tsx}', '**/__tests__/**'],
      env: {
        jest: true,
      },
      globals: {
        vi: 'readonly',
        describe: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        global: 'readonly',
      },
    },
  ],
  rules: {},
};
