import { config } from 'dotenv';

config();

const defaultConfig = {
    server: {
        port: process.env.PORT || 3000,
        host: process.env.HOST || 'localhost',
    },
    api: {
        baseUrl: process.env.API_BASE_URL || '/api',
    },
    database: {
        uri: process.env.DATABASE_URI || 'mongodb://localhost:27017/movie-chatbot',
    },
    recommendations: {
        maxResults: parseInt(process.env.MAX_RESULTS) || 10,
        minRating: parseFloat(process.env.MIN_RATING) || 3.0,
    },
    emotion: {
        detectionThreshold: parseFloat(process.env.EMOTION_DETECTION_THRESHOLD) || 0.5,
    },
    logging: {
        level: process.env.LOG_LEVEL || 'info',
    },
};

export default defaultConfig;