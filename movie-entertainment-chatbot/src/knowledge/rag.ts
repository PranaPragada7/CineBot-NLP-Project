import { Retriever } from './retriever';
import { generateResponse } from '../nlg/hybridGenerator';
import { EmotionDetector } from '../emotion/emotionDetector';
import { RecommenderAPI } from '../integrations/recommenderAPI';

class RAG {
    private retriever: Retriever;
    private emotionDetector: EmotionDetector;
    private recommenderAPI: RecommenderAPI;

    constructor() {
        this.retriever = new Retriever();
        this.emotionDetector = new EmotionDetector();
        this.recommenderAPI = new RecommenderAPI();
    }

    async handleQuery(userInput: string, userId: string) {
        const emotion = this.emotionDetector.detectEmotion(userInput);
        const retrievedKnowledge = await this.retriever.retrieve(userInput);
        const response = await generateResponse(retrievedKnowledge, userInput);

        const recommendations = await this.recommenderAPI.getRecommendations(userId, emotion);

        return {
            response,
            recommendations,
            emotion
        };
    }
}

export default RAG;