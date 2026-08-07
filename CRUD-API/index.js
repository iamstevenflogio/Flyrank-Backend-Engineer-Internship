const express = require('express');
const app = express();
const port = 3000;

// In-memory data: this resets when we restart server
const tasks = [
    {id: 1, title: "Learn Express basics", done: false},
    {id: 2, title: "Create a Task API", done: true},
    {id: 3, title: "Test endpoints in Insomnia", done: true}
]

app.listen(port, () => {
  console.log(`it's alive on http://localhost:${port}`);
});

app.get('/', (req, res) => {
  res.send({
    "name": "Task API",
    "version": "1.0",
    "endpoints": "[/tasks]"
  });
});

app.get('/health', (req, res) => {
    res.send({
        "status": "ok"
    })
});

app.get('/tasks', (req, res) => {
    res.send({tasks})
})

app.get('/tasks/:id', (req, res) => {
    const id = Number(req.params.id);
    const task = tasks.find((task) => task.id === id);

    if (!task) {
        return res.status(404).json(`error: Task ${id} not found`)
    }
    res.send(task)
})




