import { ContentBasedRecommender } from './contentBased';
import { CollaborativeRecommender } from './collaborative';
import { Movie } from '../types/index';

export class HybridRecommender {
    private contentBasedRecommender: ContentBasedRecommender;
    private collaborativeRecommender: CollaborativeRecommender;

    constructor() {
        this.contentBasedRecommender = new ContentBasedRecommender();
        this.collaborativeRecommender = new CollaborativeRecommender();
    }

    public async recommendMovies(userId: string, userPreferences: any): Promise<Movie[]> {
        const contentBasedRecommendations = await this.contentBasedRecommender.recommend(userPreferences);
        const collaborativeRecommendations = await this.collaborativeRecommender.recommend(userId);

        const combinedRecommendations = this.combineRecommendations(contentBasedRecommendations, collaborativeRecommendations);
        return this.filterUniqueMovies(combinedRecommendations);
    }

    private combineRecommendations(contentBased: Movie[], collaborative: Movie[]): Movie[] {
        const recommendationMap = new Map<string, Movie>();

        contentBased.forEach(movie => recommendationMap.set(movie.id, movie));
        collaborative.forEach(movie => recommendationMap.set(movie.id, movie));

        return Array.from(recommendationMap.values());
    }

    private filterUniqueMovies(recommendations: Movie[]): Movie[] {
        const uniqueMovies = new Set<string>();
        return recommendations.filter(movie => {
            if (!uniqueMovies.has(movie.id)) {
                uniqueMovies.add(movie.id);
                return true;
            }
            return false;
        });
    }
}