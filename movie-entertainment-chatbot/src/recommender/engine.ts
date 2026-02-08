import { ContentBasedRecommender } from './contentBased';
import { CollaborativeRecommender } from './collaborative';
import { HybridRecommender } from './hybrid';
import { UserProfile } from '../types/index';

class RecommenderEngine {
    private contentBasedRecommender: ContentBasedRecommender;
    private collaborativeRecommender: CollaborativeRecommender;
    private hybridRecommender: HybridRecommender;

    constructor() {
        this.contentBasedRecommender = new ContentBasedRecommender();
        this.collaborativeRecommender = new CollaborativeRecommender();
        this.hybridRecommender = new HybridRecommender();
    }

    public recommendMovies(userProfile: UserProfile, method: 'content' | 'collaborative' | 'hybrid'): Promise<any[]> {
        switch (method) {
            case 'content':
                return this.contentBasedRecommender.recommend(userProfile);
            case 'collaborative':
                return this.collaborativeRecommender.recommend(userProfile);
            case 'hybrid':
                return this.hybridRecommender.recommend(userProfile);
            default:
                throw new Error('Invalid recommendation method');
        }
    }
}

export default RecommenderEngine;