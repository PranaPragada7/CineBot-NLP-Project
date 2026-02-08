import { Movie } from '../types';
import { getMovieData } from '../integrations/tmdb';
import { calculateSimilarity } from '../utils/similarity';

class ContentBasedRecommender {
    private movieDatabase: Movie[];

    constructor() {
        this.movieDatabase = [];
    }

    public async initialize() {
        this.movieDatabase = await getMovieData();
    }

    public recommendMovies(userPreferences: Movie): Movie[] {
        const recommendations = this.movieDatabase
            .map(movie => ({
                movie,
                similarity: this.calculateMovieSimilarity(userPreferences, movie)
            }))
            .filter(item => item.similarity > 0)
            .sort((a, b) => b.similarity - a.similarity)
            .map(item => item.movie);

        return recommendations.slice(0, 5); // Return top 5 recommendations
    }

    private calculateMovieSimilarity(userPreferences: Movie, movie: Movie): number {
        return calculateSimilarity(userPreferences, movie);
    }
}

export default ContentBasedRecommender;