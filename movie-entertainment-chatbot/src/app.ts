import express from 'express';
import bodyParser from 'body-parser';
import chatRoutes from './api/routes/chat';
import recommendRoutes from './api/routes/recommend';
import { config } from './config/env';

const app = express();
const PORT = config.port || 3000;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use('/api/chat', chatRoutes);
app.use('/api/recommend', recommendRoutes);

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});