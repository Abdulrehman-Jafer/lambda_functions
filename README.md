# Lambda Functions

This repository contains AWS Lambda functions with CI/CD using GitHub Actions.

## Functions

### Python Hello-World
- **Location**: `python-hello-world/`
- **Handler**: `lambda_function.lambda_handler`
- **Runtime**: Python 3.9
- **Description**: A simple Hello World Lambda function in Python

### JavaScript Hello-World
- **Location**: `javascript-hello-world/`
- **Handler**: `index.handler`
- **Runtime**: Node.js 18
- **Description**: A simple Hello World Lambda function in JavaScript

## Testing

### Python Lambda
```bash
cd python-hello-world
python -m unittest test_lambda_function.py
```

### JavaScript Lambda
```bash
cd javascript-hello-world
npm install
npm test
```

## Linting

### Python
```bash
cd python-hello-world
pip install flake8
flake8 lambda_function.py --max-line-length=100
```

### JavaScript
```bash
cd javascript-hello-world
npm install
npm run lint
```

## CI/CD

The repository uses GitHub Actions for continuous integration and deployment. The workflow automatically:
- Tests both Python and JavaScript Lambda functions
- Lints the code for quality assurance
- Runs on every push to main branch and pull requests

## Project Structure

```
lambda_functions/
├── python-hello-world/
│   ├── lambda_function.py
│   └── test_lambda_function.py
├── javascript-hello-world/
│   ├── index.js
│   ├── index.test.js
│   └── package.json
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── README.md
```