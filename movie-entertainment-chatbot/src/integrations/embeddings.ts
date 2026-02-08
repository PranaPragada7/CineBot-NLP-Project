import { createHash } from 'crypto';
import { EmbeddingModel } from 'some-embedding-library'; // Replace with actual embedding library

class EmbeddingService {
    private model: EmbeddingModel;

    constructor() {
        this.model = new EmbeddingModel(); // Initialize the embedding model
    }

    public async generateEmbedding(text: string): Promise<number[]> {
        const embedding = await this.model.embed(text);
        return embedding;
    }

    public hashText(text: string): string {
        return createHash('sha256').update(text).digest('hex');
    }

    public async getEmbeddingsForTexts(texts: string[]): Promise<{ text: string; embedding: number[]; hash: string }[]> {
        const embeddings = await Promise.all(texts.map(async (text) => {
            const embedding = await this.generateEmbedding(text);
            const hash = this.hashText(text);
            return { text, embedding, hash };
        }));
        return embeddings;
    }
}

export default new EmbeddingService();