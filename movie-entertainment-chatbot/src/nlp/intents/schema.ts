import { z } from 'zod';

const IntentSchema = z.object({
  name: z.string(),
  examples: z.array(z.string()),
  entities: z.array(z.string()).optional(),
});

const IntentsSchema = z.array(IntentSchema);

export type Intent = z.infer<typeof IntentSchema>;
export type Intents = z.infer<typeof IntentsSchema>;

export const intents: Intents = [
  {
    name: 'greet',
    examples: ['Hello', 'Hi there', 'Good morning'],
  },
  {
    name: 'recommend_movie',
    examples: ['Can you recommend a movie?', 'Suggest a film for me', 'What should I watch?'],
    entities: ['genre', 'year', 'actor'],
  },
  {
    name: 'get_movie_details',
    examples: ['Tell me about Inception', 'What is the plot of The Matrix?'],
    entities: ['movie_title'],
  },
  {
    name: 'goodbye',
    examples: ['Goodbye', 'See you later', 'Bye'],
  },
];