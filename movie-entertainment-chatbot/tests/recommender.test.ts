import { recommendMovies } from '../src/recommender/engine';
import { UserProfile } from '../src/types/index';

describe('Recommender System', () => {
    const mockUserProfile: UserProfile = {
        id: 'user123',
        likedGenres: ['Action', 'Comedy'],
        dislikedGenres: ['Horror'],
        watchHistory: ['Movie A', 'Movie B'],
    };

    it('should recommend movies based on user profile', () => {
        const recommendations = recommendMovies(mockUserProfile);
        expect(recommendations).toBeDefined();
        expect(recommendations.length).toBeGreaterThan(0);
        recommendations.forEach(movie => {
            expect(movie.genres).toEqual(expect.arrayContaining(mockUserProfile.likedGenres));
            expect(movie.genres).not.toEqual(expect.arrayContaining(mockUserProfile.dislikedGenres));
        });
    });

    it('should return an empty array if no suitable recommendations are found', () => {
        const emptyProfile: UserProfile = {
            id: 'user456',
            likedGenres: [],
            dislikedGenres: ['Drama'],
            watchHistory: [],
        };
        const recommendations = recommendMovies(emptyProfile);
        expect(recommendations).toEqual([]);
    });
});