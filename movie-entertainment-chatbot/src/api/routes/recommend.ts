import { Router } from 'express';
import { getRecommendations } from '../../recommender/engine';
import { EmotionDetector } from '../../emotion/emotionDetector';
import { UserProfile } from '../../data/samples/user_profiles.json';

const router = Router();
const emotionDetector = new EmotionDetector();

router.post('/recommend', async (req, res) => {
    const { userId, userInput } = req.body;

    if (!userId || !userInput) {
        return res.status(400).json({ error: 'User ID and input are required.' });
    }

    const userProfile = UserProfile.find(profile => profile.id === userId);
    const userEmotion = emotionDetector.detect(userInput);
    
    try {
        const recommendations = await getRecommendations(userProfile, userEmotion);
        return res.status(200).json({ recommendations });
    } catch (error) {
        return res.status(500).json({ error: 'Failed to fetch recommendations.' });
    }
});

export default router;