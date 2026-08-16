require('dotenv').config();
const { Pool } = require('pg')

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
});

async function initDb() {
    await pool.query(`
        CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL, 
        done BOOLEAN NOT NULL DEFAULT FALSE
        )
    `);

    const countResult = await pool.query(
        `SELECT COUNT(*)::int AS count FROM tasks`
    );

    if (countResult.rows[0].count === 0) {
        await pool.query(
            `
            INSERT INTO tasks (title, done)
            VALUES 
                ($1, $2),
                ($3, $4),
                ($5, $6)
            `,
            [
                'Learn Express basics', false,
                'Create a Task API', true,
                'Test endpoints in Insomnia', true
            ]
        );
    }
}

async function getAllTasks() {
    const result = await pool.query(`SELECT * FROM tasks`);
    return result.rows
}

async function getTaskById(id) {
    const result = await pool.query(
        `SELECT * FROM tasks WHERE id = $1`, [id]
    );
    return result.rows[0] || null;
}

async function createTask(title) {
    const result = await pool.query(
        `
        INSERT INTO tasks (title, done)
        VALUES ($1, $2)
        RETURNING id, title, done
        `,
        [title, false]
    );
    return result.rows[0];
}   

async function updateTask(id, title, done) {
    const result = await pool.query(
        `
        UPDATE tasks
        SET title = $1, done = $2
        WHERE id  = $3
        RETURNING id, title, done
        `,
        [title, done, id]
    );
    return result.rows[0] || null;
}

async function deleteTask(id) {
    const result = await pool.query(
        `DELETE FROM tasks WHERE id = $1`,
        [id]
    );
    return result.rowCount;
}

module.exports = {
    initDb, 
    getAllTasks,
    getTaskById,
    createTask,
    updateTask,
    deleteTask
};