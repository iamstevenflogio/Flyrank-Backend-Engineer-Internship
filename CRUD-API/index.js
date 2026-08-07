const express = require('express');
const app = express();
const port = 3000;

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


