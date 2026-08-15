const express = require('express');
const app = express();
const port = 3000;
const swaggerUi = require('swagger-ui-express');
const openapiDocument = require('./openapi.json');

const {
    initDb,
    getAllTasks,
    getTaskById,
    createTask,
    updateTask,
    deleteTask,
} = require('./db')

app.use('/docs', swaggerUi.serve, swaggerUi.setup(openapiDocument));
app.use(express.json());

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

app.get('/tasks', async (req, res) => {
    try {
        const tasks = await getAllTasks();
        res.json(tasks);
    } catch (err) {
        res.status(500).json({ 
            error: 'Internal server error'
        })
    }
});

app.get('/tasks/:id', async (req, res) => {
    try {
        const id = Number(req.params.id);
        const task = await getTaskById(id);

        if (!task) {
            return res.status(404).json({
                error: `Task not found`
            });
        }

        res.json(task)
    } catch (err) {
        res.status(500).json({ 
            error: 'Internal server error' 
        });
    }
    });

    app.post('/tasks', async (req, res) => {
        try {
            const { title } = req.body;

            if (!title || !title.trim()) {
                return res.status(400).json({
                    error: "title is required and cannot be empty"
                });
            }

            const newTask = await createTask(title.trim());
            res.status(201).json(newTask)
        } catch (err) {
            res.status(500).json({ 
                error: 'Internal server error'
            });
        }
    });

    app.put('/tasks/:id', async (req, res) => {
        try {
            const id = Number(req.params.id);
            const task = await getTaskById(id);

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
                updatedDone = done;
            }

            const updatedTask = await updateTask(id, updatedTitle, updatedDone); 
                res.json(updatedTask);
        } catch(err) {
            res.status(500).json({ error: 'Internal server error' });
        }
});

app.delete('/tasks/:id', async (req, res) => {
    try {
        const id = Number(req.params.id);
        const deletedCount = await deleteTask(id);

        if (deletedCount === 0) {
            return res.status(404).json({
                error: "Task not found"
            });
        }
        res.status(204).send();
    } catch (err) {
        res.status(500).json({
            error: 'Internal server error'
        });
    }
});

initDb() 
    .then(() => {
        app.listen(port, () => {
            console.log(`It's alive on http://localhost:${port}`);
        });
    })
    .catch((err) => {
        console.error('Failed to start app:', err);
        process.exit(1);
    });





