import { Configuration, OpenAIApi } from 'openai';
import { EmotionDetector } from '../emotion/emotionDetector';
import { HybridGenerator } from '../nlg/hybridGenerator';

class LLMIntegration {
    private openai: OpenAIApi;
    private emotionDetector: EmotionDetector;
    private hybridGenerator: HybridGenerator;

    constructor(apiKey: string) {
        const configuration = new Configuration({
            apiKey: apiKey,
        });
        this.openai = new OpenAIApi(configuration);
        this.emotionDetector = new EmotionDetector();
        this.hybridGenerator = new HybridGenerator();
    }

    async generateResponse(prompt: string, userEmotion: string): Promise<string> {
        const emotionBasedPrompt = this.adjustPromptForEmotion(prompt, userEmotion);
        const response = await this.openai.createChatCompletion({
            model: 'gpt-3.5-turbo',
            messages: [{ role: 'user', content: emotionBasedPrompt }],
        });

        return response.data.choices[0].message.content;
    }

    private adjustPromptForEmotion(prompt: string, emotion: string): string {
        switch (emotion) {
            case 'happy':
                return `In a cheerful tone, ${prompt}`;
            case 'sad':
                return `In a comforting tone, ${prompt}`;
            case 'angry':
                return `In a calm and soothing tone, ${prompt}`;
            default:
                return prompt;
        }
    }

    async getEmotionBasedResponse(userInput: string): Promise<string> {
        const detectedEmotion = this.emotionDetector.detect(userInput);
        const response = await this.generateResponse(userInput, detectedEmotion);
        return response;
    }
}

export default LLMIntegration;