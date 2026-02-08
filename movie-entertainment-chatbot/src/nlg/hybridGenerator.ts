import { Template } from './templates';
import { getResponseFromLLM } from '../integrations/llm';
import { getMovieRecommendations } from '../recommender/engine';
import { detectEmotion } from '../emotion/emotionDetector';
import { getContextualResponse } from '../dialogue/context';
import { getUserIntent } from '../nlp/intents/classifier';
import { extractEntities } from '../nlp/entities/extractors';

export class HybridGenerator {
    async generateResponse(userInput: string, userProfile: any) {
        const intent = await getUserIntent(userInput);
        const entities = extractEntities(userInput);
        const emotion = detectEmotion(userInput);
        const contextResponse = getContextualResponse(userProfile);

        let response;

        if (intent === 'recommend_movie') {
            const recommendations = await getMovieRecommendations(userProfile);
            response = Template.movieRecommendation(recommendations, emotion);
        } else {
            const llmResponse = await getResponseFromLLM(userInput, contextResponse);
            response = Template.defaultResponse(llmResponse, emotion);
        }

        return response;
    }
}