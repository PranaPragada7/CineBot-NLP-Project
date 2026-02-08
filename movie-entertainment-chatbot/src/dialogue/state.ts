import { Intent, Entity } from '../types/index';

export interface DialogueState {
    currentIntent: Intent | null;
    entities: Entity[];
    context: Record<string, any>;
    previousMessages: string[];
    userEmotion: string | null;
}

export class StateManager {
    private state: DialogueState;

    constructor() {
        this.state = {
            currentIntent: null,
            entities: [],
            context: {},
            previousMessages: [],
            userEmotion: null,
        };
    }

    public updateIntent(intent: Intent): void {
        this.state.currentIntent = intent;
    }

    public addEntity(entity: Entity): void {
        this.state.entities.push(entity);
    }

    public updateContext(key: string, value: any): void {
        this.state.context[key] = value;
    }

    public addMessage(message: string): void {
        this.state.previousMessages.push(message);
    }

    public setUserEmotion(emotion: string): void {
        this.state.userEmotion = emotion;
    }

    public getState(): DialogueState {
        return this.state;
    }

    public resetState(): void {
        this.state = {
            currentIntent: null,
            entities: [],
            context: {},
            previousMessages: [],
            userEmotion: null,
        };
    }
}