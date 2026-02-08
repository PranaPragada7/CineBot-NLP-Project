import { KnowledgeBase } from './knowledgeBase';
import { Movie } from '../types/index';

export class Retriever {
    private knowledgeBase: KnowledgeBase;

    constructor(knowledgeBase: KnowledgeBase) {
        this.knowledgeBase = knowledgeBase;
    }

    public async retrieveRelevantMovies(query: string): Promise<Movie[]> {
        const results = await this.knowledgeBase.search(query);
        return this.filterMovies(results);
    }

    private filterMovies(results: any[]): Movie[] {
        return results.map(result => ({
            id: result.id,
            title: result.title,
            genre: result.genre,
            releaseDate: result.release_date,
            overview: result.overview,
        }));
    }
}