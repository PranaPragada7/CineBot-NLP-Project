import NodeCache from 'node-cache';

class Cache {
    private cache: NodeCache;

    constructor(ttl: number) {
        this.cache = new NodeCache({ stdTTL: ttl });
    }

    set(key: string, value: any): void {
        this.cache.set(key, value);
    }

    get(key: string): any {
        return this.cache.get(key);
    }

    del(key: string): void {
        this.cache.del(key);
    }

    flushAll(): void {
        this.cache.flushAll();
    }
}

export default Cache;