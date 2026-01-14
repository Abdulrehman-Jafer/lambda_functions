/**
 * AWS Lambda handler function that returns a Hello World message.
 * 
 * @param {Object} event - The event object that contains the parameters sent when the function is invoked.
 * @param {Object} context - The context in which the function is called.
 * @returns {Object} Response with statusCode and body containing the message.
 */
exports.handler = async (event, context) => {
    return {
        statusCode: 200,
        body: JSON.stringify({
            message: 'Hello World from JavaScript Lambda!'
        })
    };
};
