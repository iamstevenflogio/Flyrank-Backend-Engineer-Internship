const express = require('express');
const app = express();
const port = 3000;
const swaggerUi = require('swagger-ui-express');
const openapiDocument = require('./openapi.json');

app.use('/docs', swaggerUi.serve, swaggerUi.setup(openapiDocument));

app.use(express.json());

// Database 
const Database = require('better-sqlite3');
const db = new Database('tasks.db')

db.prepare(`
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, 
        title TEXT NOT NULL, 
        done INTEGER NOT NULL DEFAULT 0
    )
`).run();

const rowCount = db.prepare(`SELECT COUNT(*) AS count FROM tasks`).get();

if (rowCount.count === 0) {
    const insert = db.prepare('INSERT INTO tasks (title, done) VALUES (?, ?)'); 
    insert.run('Learn Express basics', 0);
    insert.run('Create a Task API', 1);
    insert.run('Test endpoints in Insomnia', 1);
}

app.listen(port, () => {
  console.log(`it's alive on http://localhost:${port}`);
});

app.get('/', (req, res) => {
  res.send({
    "name": "Task API",
    "version": "1.0",
    endpoints: "[/tasks]"
  });
});

app.get('/health', (req, res) => {
    res.send({
        "status": "ok"
    })
});

app.get('/tasks', (req, res) => {
    const tasks = db.prepare(`SELECT * FROM tasks`).all(); // reads from tasks on the database

    res.json(tasks)
})

app.get('/tasks/:id', (req, res) => {
    const id = Number(req.params.id);
    const task = db.prepare(`SELECT * FROM tasks WHERE id = ?`).get(id); // selects task with ID from the db

    if (!task) {
        return res.status(404).json({
            error: `Task not found`
        });
    }
    res.json(task)
})

app.post('/tasks', (req, res) => {
    const { title } = req.body;

    if (!title || !title.trim()) {
        return res.status(400).json({
            error: "title is required and cannot be empty"
        });
    }

    // Insert into SQLite; SQLite assigns the id
    const result = db.prepare(`
        INSERT INTO tasks (title, done)
        VALUES (?, ?)
        `).run(title.trim(), 0);

    const newTask = db.prepare(`
        SELECT * FROM tasks WHERE id = ?`).get(result.lastInsertRowid);

    res.status(201).json(newTask)
});


app.put('/tasks/:id', (req, res) => {
    const id = Number(req.params.id);

    // Check if task exists
    const task = db.prepare(`
        SELECT * FROM tasks WHERE id = ?`).get(id)

    if (!task) {
        return res.status(404).json({
            error: `Task not found`
        });
    }

    const { title, done } = req.body || {}; 

    if (title === undefined && done === undefined) {
        return res.status(400).json({
            error: "request body must include title and/or done"
        });
    }

    // Start with existing database values
    let updatedTitle = task.title;
    let updatedDone = task.done;

    if (title !== undefined) {
        if (!title || !title.trim()) {
            return res.status(400).json({
                error: "title is required and cannot be empty"
            });
        }
        updatedTitle = title.trim();
    }

    if (done !== undefined) {
        if (typeof done !== 'boolean') {
            return res.status(400).json({
                error: "done must be a boolean"
            });
        }
        // SQLite stores Boolean values as 0 or 1
        updatedDone = done ? 1 : 0;
    }

    db.prepare(`
        UPDATE tasks
        SET title = ?, done = ?
        WHERE id = ?
        `).run(updatedTitle, updatedDone, id);

    const updatedTask = db.prepare(`
        SELECT * FROM tasks WHERE id = ?
        `).get(id);

    res.json(updatedTask);
});

app.delete('/tasks/:id', (req, res) => {
    const id = Number(req.params.id);

    const result = db.prepare(`
        DELETE FROM tasks WHERE id = ?
        `).run(id);

    if (result.changes === 0) {
        return res.status(404).json({
            error: "Task not found"
        });
    }

    res.status(204).send();
});



