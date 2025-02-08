# Linting and Formatting Tools Quick Reference

This project uses several tools for linting and formatting. Below is a list of commands and their purposes.

## 1. Black (Code Formatter)
Formats Python code to follow the [PEP 8](https://peps.python.org/pep-0008/) style guide.

**Run Black:**
```bash
black . --config ./tools/pyproject.toml
```

## 2. isort (Import Sorting)
Sorts and organizes Python imports.

**Run isort:**
```bash
isort . --settings-path ./tools/pyproject.toml
```

## 3. flake8 (Code Linter)
Checks for style issues, code quality, and potential bugs.

**Run flake8:**
```bash
flake8 . --config ./tools/.flake8
```
