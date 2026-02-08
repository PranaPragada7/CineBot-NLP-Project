export interface User {
    id: string;
    name: string;
    preferences: string[];
    favoriteGenres: string[];
}

export interface Movie {
    id: string;
    title: string;
    genres: string[];
    releaseDate: string;
    rating: number;
    overview: string;
}

export interface ChatMessage {
    userId: string;
    message: string;
    timestamp: Date;
}

export interface Intent {
    name: string;
    confidence: number;
}

export interface Entity {
    name: string;
    value: string;
}

export interface Recommendation {
    movie: Movie;
    reason: string;
}

export interface Emotion {
    type: string;
    confidence: number;
}

export interface Context {
    previousMessages: ChatMessage[];
    currentIntent: Intent | null;
    currentEntities: Entity[];
}