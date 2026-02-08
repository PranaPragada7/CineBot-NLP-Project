import { Movie } from '../../types/index';
import { VectorStore } from 'some-vector-store-library'; // Replace with actual vector store library
import { createEmbedding } from '../../integrations/embeddings';

class MovieIndexer {
    private vectorStore: VectorStore;

    constructor(vectorStore: VectorStore) {
        this.vectorStore = vectorStore;
    }

    public async indexMovies(movies: Movie[]): Promise<void> {
        for (const movie of movies) {
            const embedding = await createEmbedding(movie.description);
            await this.vectorStore.add({
                id: movie.id,
                embedding,
                metadata: {
                    title: movie.title,
                    genre: movie.genre,
                    releaseDate: movie.releaseDate,
                },
            });
        }
    }

    public async search(query: string, topK: number = 5): Promise<Movie[]> {
        const queryEmbedding = await createEmbedding(query);
        const results = await this.vectorStore.query(queryEmbedding, topK);
        return results.map(result => ({
            id: result.id,
            title: result.metadata.title,
            genre: result.metadata.genre,
            releaseDate: result.metadata.releaseDate,
        }));
    }
}

export default MovieIndexer;