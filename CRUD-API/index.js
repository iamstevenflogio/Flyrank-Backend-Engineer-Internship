const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

// In-memory data: this resets when we restart server
const tasks = [
    {id: 1, title: "Learn Express basics", done: false},
    {id: 2, title: "Create a Task API", done: true},
    {id: 3, title: "Test endpoints in Insomnia", done: true},
]

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



