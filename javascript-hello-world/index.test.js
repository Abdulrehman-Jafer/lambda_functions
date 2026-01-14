const { handler } = require('./index');

describe('Lambda Handler', () => {
    test('returns 200 status code', async () => {
        const event = {};
        const context = {};
        
        const response = await handler(event, context);
        
        expect(response.statusCode).toBe(200);
    });
    
    test('returns expected message', async () => {
        const event = {};
        const context = {};
        
        const response = await handler(event, context);
        const body = JSON.parse(response.body);
        
        expect(body).toHaveProperty('message');
        expect(body.message).toBe('Hello World from JavaScript Lambda!');
    });
});
