import axios from 'axios';

const RECOMMENDER_API_URL = process.env.RECOMMENDER_API_URL || 'https://api.example.com/recommendations';

export interface RecommendationRequest {
    userId: string;
    genre?: string;
    mood?: string;
}

export interface RecommendationResponse {
    recommendations: Array<{
        title: string;
        description: string;
        releaseDate: string;
        rating: number;
    }>;
}

export const getRecommendations = async (request: RecommendationRequest): Promise<RecommendationResponse> => {
    try {
        const response = await axios.post<RecommendationResponse>(RECOMMENDER_API_URL, request);
        return response.data;
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        throw new Error('Could not fetch recommendations');
    }
};