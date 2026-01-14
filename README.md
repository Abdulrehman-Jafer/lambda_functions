# Lambda Functions

This repository contains AWS Lambda functions.

## Functions

### Python Hello-World
- **Location**: `python-hello-world/`
- **Handler**: `lambda_function.lambda_handler`
- **Runtime**: Python 3.9
- **Description**: A simple Hello World Lambda function that returns a JSON response with "Hello from Lambda!" message

## Function Details

### lambda_function.py
The main Lambda function that:
- Accepts an event and context parameter
- Returns a JSON response with status code 200
- Includes a simple "Hello from Lambda!" message in the response body

## Local Development

### Testing the Python Lambda
To test the function locally, you can run:
```python
from python-hello-world.lambda_function import lambda_handler

event = {}
context = {}
response = lambda_handler(event, context)
print(response)
```

## CI/CD

The repository uses GitHub Actions for continuous integration and deployment. The workflow automatically:
- Runs on every push to main branch and pull requests

## Project Structure

```
lambda_functions/
├── python-hello-world/
│   ├── lambda_function.py
│   └── test_lambda_function.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── README.md
```