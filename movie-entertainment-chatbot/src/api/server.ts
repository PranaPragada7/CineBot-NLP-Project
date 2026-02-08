import express from 'express';
import bodyParser from 'body-parser';
import chatRoutes from './routes/chat';
import recommendRoutes from './routes/recommend';
import { createServer } from 'http';

const app = express();
const server = createServer(app);

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use('/api/chat', chatRoutes);
app.use('/api/recommend', recommendRoutes);

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

export default server;