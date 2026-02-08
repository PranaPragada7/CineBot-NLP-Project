import { Context } from '../context';
import { State } from '../state';
import { generateResponse } from '../../nlg/hybridGenerator';
import { recommendMovies } from '../../recommender/engine';
import { EmotionDetector } from '../../emotion/emotionDetector';

class HybridPolicy {
    private context: Context;
    private state: State;
    private emotionDetector: EmotionDetector;

    constructor(context: Context, state: State) {
        this.context = context;
        this.state = state;
        this.emotionDetector = new EmotionDetector();
    }

    public async handleUserInput(userInput: string) {
        const emotion = this.emotionDetector.detect(userInput);
        this.state.updateEmotion(emotion);

        const intent = await this.state.getIntent(userInput);
        const entities = await this.state.extractEntities(userInput);

        if (intent === 'recommend_movie') {
            const recommendations = await recommendMovies(entities);
            return this.generateResponse(recommendations);
        } else {
            const response = await generateResponse(userInput, this.context);
            return response;
        }
    }

    private generateResponse(recommendations: any) {
        if (recommendations.length > 0) {
            return `I recommend these movies: ${recommendations.join(', ')}`;
        } else {
            return "I'm sorry, I couldn't find any recommendations for you.";
        }
    }
}

export default HybridPolicy;