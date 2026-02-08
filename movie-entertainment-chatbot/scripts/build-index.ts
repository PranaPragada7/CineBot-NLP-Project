import { createIndex } from '../src/knowledge/vectorstore/indexer';
import { loadMovieData } from '../src/data/schemas/movie';
import { logger } from '../src/utils/logger';

async function buildIndex() {
    try {
        logger.info('Loading movie data...');
        const movieData = await loadMovieData();
        
        logger.info('Building index...');
        await createIndex(movieData);
        
        logger.info('Index built successfully!');
    } catch (error) {
        logger.error('Error building index:', error);
    }
}

buildIndex();