import { SentimentAnalyzer } from 'sentiment';
import { Emotion } from '../types/index';

export class EmotionDetector {
    private sentimentAnalyzer: SentimentAnalyzer;

    constructor() {
        this.sentimentAnalyzer = new SentimentAnalyzer();
    }

    public detectEmotion(text: string): Emotion {
        const sentimentResult = this.sentimentAnalyzer.analyze(text);
        const score = sentimentResult.score;

        if (score > 0) {
            return { emotion: 'positive', score };
        } else if (score < 0) {
            return { emotion: 'negative', score };
        } else {
            return { emotion: 'neutral', score };
        }
    }
}