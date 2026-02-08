import { UserContext } from './types'; // Assuming you have a UserContext type defined in types/index.ts

class DialogueContext {
    private context: Map<string, UserContext>;

    constructor() {
        this.context = new Map();
    }

    // Set user context
    public setUserContext(userId: string, userContext: UserContext): void {
        this.context.set(userId, userContext);
    }

    // Get user context
    public getUserContext(userId: string): UserContext | undefined {
        return this.context.get(userId);
    }

    // Update user context with new information
    public updateUserContext(userId: string, newContext: Partial<UserContext>): void {
        const currentContext = this.getUserContext(userId);
        if (currentContext) {
            this.context.set(userId, { ...currentContext, ...newContext });
        }
    }

    // Clear user context
    public clearUserContext(userId: string): void {
        this.context.delete(userId);
    }
}

export default DialogueContext;