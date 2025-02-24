# Testing Documentation

This codebase is setup with a **high standard testing**.
Which automate the testing of almost complte codebase.

Here we explain how we put different testing in our codebase.

Wishing you Happy Reading :) from @jitendra-ky

## Django API Endpoint Tests

### Overview

Django API endpoint tests are used to test individual API endpoints of the application to ensure they work as expected.

### Running Django API Endpoint Tests

To run the Django API endpoint tests, use the following command:

```bash
python manage.py test
```

### Test Framework

We use Django's built-in test framework for testing API endpoints.

## UI Tests

### Overview

UI tests are used to test the user interface of the application using Selenium.

> With `selenium` i automate almost complete UI (User Interface).
> So no more headache or visiting every page and checking, if it is woring corrently or not after making every small change.

### Running UI Tests

To run the UI tests:

> make sure django server is running on localhost:8000.
> you can run the server with `python manag.epy runserver`

```bash
./tools/uitest
```

### Test Framework

We use Selenium for UI testing.

Selenium is a powerful tool for **controlling a web browser through the program**. It is functional for all browsers, works on all major OS, and its scripts can be written in various programming languages such as **Python**, Java, C#, etc. Selenium is primarily used for **automating web applications for testing purposes** but is certainly not limited to just that. Boring web-based administration tasks can also be automated as well.

## Linting

### Overview

Linting is used to ensure code quality and adherence to coding standards.

### Running Linting

To run the linting checks for python code, use the following command:

```bash
ruff check --force-exclude $(git ls-files '*.py')
```

To run ESLint and Prettier check.

```bash
npm run test
```

### Tools

- Ruff for linting Python code.
- ESLint for linting JavaScript code.
- Prettier for code formattng.

## CI/CD Pipeline

### Overview

With Github Actions We automation to run all the tests on every pull request.

### Pipeline Configuration

The pipeline is configured using GitHub Actions. The configuration file is located at `.github/workflows/tests_ci.yml`.
