import { config } from 'dotenv';

config();

export const ENV = {
    PORT: process.env.PORT || 3000,
    DB_URI: process.env.DB_URI || 'mongodb://localhost:27017/movie-chatbot',
    TMDB_API_KEY: process.env.TMDB_API_KEY || '',
    RECOMMENDER_API_URL: process.env.RECOMMENDER_API_URL || '',
    EMBEDDINGS_MODEL: process.env.EMBEDDINGS_MODEL || 'default-model',
    LLM_API_URL: process.env.LLM_API_URL || '',
    CACHE_EXPIRY: process.env.CACHE_EXPIRY ? parseInt(process.env.CACHE_EXPIRY) : 3600,
    LOG_LEVEL: process.env.LOG_LEVEL || 'info',
};