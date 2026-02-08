import request from 'supertest';
import app from '../src/app'; // Adjust the path as necessary

describe('API Routes', () => {
    describe('POST /api/chat', () => {
        it('should respond with a message from the chatbot', async () => {
            const response = await request(app)
                .post('/api/chat')
                .send({ message: 'Hello, what movies do you recommend?' });
            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('response');
        });
    });

    describe('POST /api/recommend', () => {
        it('should respond with movie recommendations', async () => {
            const response = await request(app)
                .post('/api/recommend')
                .send({ userId: '12345' });
            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('recommendations');
            expect(Array.isArray(response.body.recommendations)).toBe(true);
        });
    });
});