import { UserProfile, Movie } from '../types';
import { getUserSimilarities, getMovieRatings } from './dataService';

export class CollaborativeRecommender {
    private userProfiles: UserProfile[];

    constructor(userProfiles: UserProfile[]) {
        this.userProfiles = userProfiles;
    }

    public recommendMovies(userId: string, topN: number = 5): Movie[] {
        const userSimilarities = this.calculateSimilarities(userId);
        const recommendedMovies = this.aggregateRecommendations(userSimilarities, topN);
        return recommendedMovies;
    }

    private calculateSimilarities(userId: string): Map<string, number> {
        const similarities = new Map<string, number>();
        const targetUserProfile = this.userProfiles.find(profile => profile.userId === userId);

        if (!targetUserProfile) {
            return similarities;
        }

        this.userProfiles.forEach(profile => {
            if (profile.userId !== userId) {
                const similarity = this.computeSimilarity(targetUserProfile, profile);
                similarities.set(profile.userId, similarity);
            }
        });

        return similarities;
    }

    private computeSimilarity(profileA: UserProfile, profileB: UserProfile): number {
        const commonMovies = profileA.ratings.filter(movie => profileB.ratings.includes(movie));
        const similarityScore = commonMovies.length / Math.sqrt(profileA.ratings.length * profileB.ratings.length);
        return similarityScore;
    }

    private aggregateRecommendations(similarities: Map<string, number>, topN: number): Movie[] {
        const movieScores: Map<string, number> = new Map();

        similarities.forEach((similarity, userId) => {
            const userRatings = getMovieRatings(userId);
            userRatings.forEach(movie => {
                const currentScore = movieScores.get(movie.id) || 0;
                movieScores.set(movie.id, currentScore + similarity * movie.rating);
            });
        });

        const sortedMovies = Array.from(movieScores.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, topN)
            .map(entry => ({ id: entry[0], score: entry[1] }));

        return sortedMovies;
    }
}