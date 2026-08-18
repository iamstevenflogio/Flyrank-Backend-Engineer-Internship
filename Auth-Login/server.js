import express from 'express';
import dotenv from 'dotenv';
import { createClient } from '@supabase/supabase-js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_KEY
);

app.use(express.json());

app.get('/', (req, res) => {
    res.json({
        message: 'Server running and Supabase client initialized',
    });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});