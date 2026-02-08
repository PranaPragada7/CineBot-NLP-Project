import { SentimentAnalyzer } from 'natural';
import { PorterStemmer } from 'natural';

// Initialize the sentiment analyzer
const analyzer = new SentimentAnalyzer('English', PorterStemmer, 'afinn');

// Function to analyze sentiment of a given text
export const analyzeSentiment = (text: string): { score: number; mood: string } => {
    const score = analyzer.getSentiment(text.split(' '));
    let mood = 'neutral';

    if (score > 0) {
        mood = 'positive';
    } else if (score < 0) {
        mood = 'negative';
    }

    return { score, mood };
};