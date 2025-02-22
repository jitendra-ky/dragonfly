const { configs } = require('eslint-plugin-prettier')

module.exports = [
  {
    ignores: ['.venv/**'], // Ignore the virtual environment directory
    files: ['static/js/**/*.js'], // Adjust this path for your project
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    plugins: {
      prettier: require('eslint-plugin-prettier'),
    },
    rules: {
      ...configs.recommended.rules,
      'prettier/prettier': 'error',
    },
  },
]
