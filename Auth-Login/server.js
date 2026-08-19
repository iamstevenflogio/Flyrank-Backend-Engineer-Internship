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

// Let the front gates open! POST routes lets users register their keys and come back with them.
// POST /auth/signup
app.post("/auth/signup", async (req,res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ error: "Email and password are required" });
    }

    const { data, error } = await supabase.auth.signUp({ email, password, });

    if (error) {
        return res.status(400).json({ error: error.message })
    }

    return res.status(201).json(data.user);
});

// POST /auth/login
app.post("/auth/login", async (req,res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return res.status(400).json({ error: "Email and password are required" })
    }

    const { data, error } = await supabase.auth.signInWithPassword  ({ email, password, });

    if (error) {
        return res.status(401).json({ error: "Invalid login credentials" });
    }
        return res.status(200).json({
            access_token: data.session.access_token, 
            refresh_token: data.session.refresh_token,
        });
});

// GET /public/info
app.get('/public/info', (req, res) => {
    return res.status(200).json({
        message: 'Welcome stranger! This info is public.',
    });
});

// the guard door inspects the visitor's pass - and turns away forgeries
app.get('/protected/profile', async (req, res) => {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({
            error: 'Access token required',
        });
    }

    const token = authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({
            error: 'Access token required',
        });
    }

    const { data, error } = await supabase.auth.getUser(token);

    if (error || !data.user) {
        return res.status(401).json({
            error: 'Invalid or expired token',
        });
    }

    return res.status(200).json({
        id: data.user.id,
        email: data.user.email,
        created_at: data.user.created_at,
    });
});





app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
