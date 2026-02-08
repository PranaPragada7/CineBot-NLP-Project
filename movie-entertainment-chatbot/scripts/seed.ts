import { MongoClient } from 'mongodb';
import { readFileSync } from 'fs';
import path from 'path';

const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const client = new MongoClient(uri);

async function seedDatabase() {
    try {
        await client.connect();
        const database = client.db('movieChatbot');
        const conversationsCollection = database.collection('conversations');
        const userProfilesCollection = database.collection('user_profiles');
        const moviesCollection = database.collection('movies');

        // Load sample conversations
        const conversationsData = JSON.parse(readFileSync(path.join(__dirname, '../data/samples/conversations.json'), 'utf-8'));
        await conversationsCollection.insertMany(conversationsData);

        // Load sample user profiles
        const userProfilesData = JSON.parse(readFileSync(path.join(__dirname, '../data/samples/user_profiles.json'), 'utf-8'));
        await userProfilesCollection.insertMany(userProfilesData);

        // Load sample movies (if applicable)
        const moviesData = JSON.parse(readFileSync(path.join(__dirname, '../data/schemas/movie.json'), 'utf-8'));
        await moviesCollection.insertMany(moviesData);

        console.log('Database seeded successfully!');
    } catch (error) {
        console.error('Error seeding database:', error);
    } finally {
        await client.close();
    }
}

seedDatabase();