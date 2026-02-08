import { classifyIntent } from '../src/nlp/intents/classifier';
import { extractEntities } from '../src/nlp/entities/extractors';
import { preprocessText } from '../src/nlp/preprocessing/text';

describe('NLP Module Tests', () => {
    describe('Intent Classification', () => {
        it('should classify intent correctly for a greeting', () => {
            const input = 'Hello, how are you?';
            const expectedIntent = 'greeting';
            const result = classifyIntent(preprocessText(input));
            expect(result).toEqual(expectedIntent);
        });

        it('should classify intent correctly for a movie recommendation request', () => {
            const input = 'Can you recommend a good action movie?';
            const expectedIntent = 'recommend_movie';
            const result = classifyIntent(preprocessText(input));
            expect(result).toEqual(expectedIntent);
        });
    });

    describe('Entity Extraction', () => {
        it('should extract movie title from user input', () => {
            const input = 'I want to watch Inception.';
            const expectedEntities = { movieTitle: 'Inception' };
            const result = extractEntities(preprocessText(input));
            expect(result).toEqual(expectedEntities);
        });

        it('should extract genre from user input', () => {
            const input = 'I love romantic comedies.';
            const expectedEntities = { genre: 'romantic comedy' };
            const result = extractEntities(preprocessText(input));
            expect(result).toEqual(expectedEntities);
        });
    });
});