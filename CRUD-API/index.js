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
    res.json(tasks)
})

app.get('/tasks/:id', (req, res) => {
    const id = Number(req.params.id);
    const task = tasks.find((task) => task.id === id);

    if (!task) {
        return res.status(404).json({
            error: `Task ${id} not found`
        });
    }
    res.send(task)
})

// Stage 3
app.post('/tasks', (req, res) => {
    const { title } = req.body;

    if (!title || !title.trim()) {
        return res.status(400).json({
            error: "title is required and cannot be empty"
        });
    }

    const nextId = 
        tasks.length > 0
            ? Math.max(...tasks.map(task => task.id)) + 1
            : 1;

    const newTask = { 
        id: nextId,
        title: title.trim(),
        done: false
    };

    tasks.push(newTask)

    res.status(201).json(newTask)

});

// Stage 4
app.put('/tasks/:id', (req, res) => {
    const id = Number(req.params.id);
    const task = tasks.find(task => task.id === id);

    if (!task) {
        return res.status(404).json({
            error: `Task ${id} not found`
        });
    }

    const { title, done } = req.body || {}; 

    if (title === undefined && done === undefined) {
        return res.status(400).json({
            error: "request body must include title and/or done"
        });
    }

    if (title !== undefined) {
        if (!title || !title.trim()) {
            return res.status(400).json({
                error: "title is required and cannot be empty"
            });
        }
        task.title = title.trim();
    }

    if (done !== undefined) {
        if (typeof done !== 'boolean') {
            return res.status(400).json({
                error: "done must be a boolean"
            });
        }
        task.done = done;
    }

    res.json(task);
});

app.delete('/tasks/:id', (req, res) => {
    const id = Number(req.params.id);
    const index = tasks.findIndex(task => task.id === id);

    if (index === -1) {
        return res.status(404).json({
            error: `Task ${id} not found`
        });
    }

    tasks.splice(index, 1);

    res.status(204).send();
});



