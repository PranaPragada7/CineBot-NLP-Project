import { Router } from 'express';
import { handleUserMessage } from '../../controllers/chatController';

const router = Router();

router.post('/chat', handleUserMessage);

export default router;