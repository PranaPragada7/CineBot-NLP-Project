import { EntityExtractor } from './baseExtractor';
import { MovieEntity, GenreEntity, ActorEntity } from '../types/entities';

export class MovieEntityExtractor extends EntityExtractor {
    extract(text: string): MovieEntity[] {
        const movieEntities: MovieEntity[] = [];
        // Logic to extract movie entities from the text
        // Example: Regex or NLP model to identify movie titles
        return movieEntities;
    }
}

export class GenreEntityExtractor extends EntityExtractor {
    extract(text: string): GenreEntity[] {
        const genreEntities: GenreEntity[] = [];
        // Logic to extract genre entities from the text
        // Example: Predefined list of genres to match against
        return genreEntities;
    }
}

export class ActorEntityExtractor extends EntityExtractor {
    extract(text: string): ActorEntity[] {
        const actorEntities: ActorEntity[] = [];
        // Logic to extract actor entities from the text
        // Example: Named entity recognition to identify actor names
        return actorEntities;
    }
}