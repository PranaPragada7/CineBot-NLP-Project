import { Entity } from './extractors';

interface ResolvedEntity {
    name: string;
    value: string | number | boolean;
}

export function resolveEntity(entity: Entity): ResolvedEntity | null {
    switch (entity.type) {
        case 'movie':
            return {
                name: 'Movie',
                value: entity.value,
            };
        case 'actor':
            return {
                name: 'Actor',
                value: entity.value,
            };
        case 'genre':
            return {
                name: 'Genre',
                value: entity.value,
            };
        case 'year':
            return {
                name: 'Year',
                value: entity.value,
            };
        default:
            return null;
    }
}

export function resolveEntities(entities: Entity[]): ResolvedEntity[] {
    return entities.map(resolveEntity).filter((resolved) => resolved !== null) as ResolvedEntity[];
}