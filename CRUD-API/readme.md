# Task API

A CRUD Task API built with Node.js, Express, PostgreSQL, and Docker Compose.

The API supports creating, reading, updating, and deleting tasks. It uses PostgreSQL for persistent storage and starts the API plus database together with Docker Compose.

## Run the project

### Requirements

- Docker Desktop
- Git

### Setup

Copy the example environment file:

```bash
cp .env.example .env
```

> PowerShell alternative:

```powershell
Copy-Item .env.example .env
```

### Start the full stack

```bash
docker compose up --build
```

The API runs at:

- API: http://localhost:3000
- Swagger UI: http://localhost:3000/docs
- Health check: http://localhost:3000/health

To stop the stack:

```bash
docker compose down
```

## Environment variables

Create a `.env` file based on `.env.example`.

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string used by the API |

Example value for local manual development:

```env
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
```

Inside Docker Compose, the API connects to PostgreSQL using the `db` service name:

```env
DATABASE_URL=postgres://postgres:dev@db:5432/tasks
```

> `.env` is ignored by Git. Do not commit secrets.

## Endpoints

| Method | Path | Description | Success status | Error status |
| --- | --- | --- | --- | --- |
| GET | `/` | Returns API metadata | `200` | - |
| GET | `/health` | Returns API health status | `200` | - |
| GET | `/tasks` | Returns all tasks | `200` | `500` on server error |
| GET | `/tasks/:id` | Returns one task by ID | `200` | `404` if task does not exist |
| POST | `/tasks` | Creates a new task | `201` | `400` if title is missing or empty |
| PUT | `/tasks/:id` | Updates a task title and/or done status | `200` | `400` for invalid body, `404` if task does not exist |
| DELETE | `/tasks/:id` | Deletes a task | `204` | `404` if task does not exist |

## Example request

Create a task:

```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

Example response:

```http
HTTP/1.1 201 Created
Content-Type: application/json; charset=utf-8

{"id":4,"title":"Buy milk","done":false}
```

Get all tasks:

```bash
curl -i http://localhost:3000/tasks
```

## Database persistence

PostgreSQL runs in the `db` Docker Compose service. The `taskdata` Docker volume stores Postgres data outside the database container.

This means tasks remain available after a full restart:

```bash
docker compose down
docker compose up
```

For example, a task created before the restart remains available through:

```bash
curl -i http://localhost:3000/tasks
```

## Database screenshot

Add your Postgres screenshot below. It should show the `tasks` table and its rows, for example using:

```bash
docker compose exec db psql -U postgres -d tasks
```

Then run:

```sql
\dt
SELECT * FROM tasks;
```

![PostgreSQL tasks table](./postgres-screenshot.png)

## Project structure

```text
.
├── index.js          # Express routes and application startup
├── db.js             # PostgreSQL queries and database initialization
├── Dockerfile        # API container image instructions
├── compose.yaml      # API + Postgres stack definition
├── .env.example      # Example environment variables
└── openapi.json      # Swagger/OpenAPI documentation
```

## Notes

- PostgreSQL automatically creates the `tasks` table if it does not exist.
- The API seeds three starter tasks only when the table is empty.
- All database queries use parameterized PostgreSQL placeholders such as `$1`, `$2`, and `$3`.
- Task IDs are generated automatically by PostgreSQL using `SERIAL PRIMARY KEY`.
- The API behavior remains the same even though its storage changed from memory, to SQLite, to containerized PostgreSQL.
