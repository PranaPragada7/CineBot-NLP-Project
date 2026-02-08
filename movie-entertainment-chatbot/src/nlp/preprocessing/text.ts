import { Tokenizer } from 'some-tokenizer-library'; // Replace with actual tokenizer library
import { normalize } from 'some-normalization-library'; // Replace with actual normalization library

export class TextPreprocessor {
    private tokenizer: Tokenizer;

    constructor() {
        this.tokenizer = new Tokenizer();
    }

    public preprocess(text: string): string[] {
        const normalizedText = this.normalizeText(text);
        return this.tokenizeText(normalizedText);
    }

    private normalizeText(text: string): string {
        return normalize(text.toLowerCase().trim());
    }

    private tokenizeText(text: string): string[] {
        return this.tokenizer.tokenize(text);
    }
}