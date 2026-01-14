import json


def lambda_handler(event, context):
    """
    AWS Lambda handler function that returns a Hello World message.

    Args:
        event: The event dict that contains the parameters sent when the function is invoked.
        context: The context in which the function is called.

    Returns:
        dict: Response with statusCode and body containing the message.
    """
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello World from Python Lambda!'
        })
    }
