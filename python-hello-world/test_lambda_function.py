import unittest
import json
from lambda_function import lambda_handler


class TestLambdaHandler(unittest.TestCase):
    def test_lambda_handler_returns_200(self):
        """Test that the lambda handler returns a 200 status code"""
        event = {}
        context = {}
        
        response = lambda_handler(event, context)
        
        self.assertEqual(response['statusCode'], 200)
    
    def test_lambda_handler_returns_message(self):
        """Test that the lambda handler returns the expected message"""
        event = {}
        context = {}
        
        response = lambda_handler(event, context)
        body = json.loads(response['body'])
        
        self.assertIn('message', body)
        self.assertEqual(body['message'], 'Hello World from Python Lambda!')


if __name__ == '__main__':
    unittest.main()
