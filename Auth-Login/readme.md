# Auth · Login & Protect API

A secure Express.js API built with Supabase Auth for user signup, login, logout, JWT verification, protected routes, and Swagger UI documentation.

## Overview

This project implements a complete authentication flow using Supabase Auth and Express. It includes public and protected endpoints, reusable authentication middleware, token-based access control, and interactive API documentation through Swagger UI.

## Features

- User signup with email and password validation. [1]
- User login with JWT access token and refresh token responses. [2]
- Public route accessible without authentication. [3]
- Protected profile and dashboard routes secured with bearer-token middleware. [4]
- Logout endpoint protected by JWT verification. [5]
- Swagger UI documentation at `/docs` with JWT bearer authorization support. [6]

## Tech Stack

- Node.js
- Express.js
- Supabase Auth
- Swagger UI Express
- OpenAPI 3.0

## Project Structure

```bash
.
├── server.js
├── openapi.json
├── package.json
├── .env
└── screenshots/
```

## Environment Variables

Create a `.env` file in the project root with the following values:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
PORT=3000
```

The project uses the Supabase project URL and anon key for authentication requests, as required by the assignment setup.

## Installation

1. Clone the repository.
2. Install dependencies.
3. Add your `.env` file.
4. Start the server.

```bash
npm install
npm install swagger-ui-express
node server.js
```

## API Endpoints

| Method | Endpoint               | Access    | Description                                                       |
| ------ | ---------------------- | --------- | ----------------------------------------------------------------- |
| GET    | `/`                    | Public    | Health check endpoint.                                            |
| POST   | `/auth/signup`         | Public    | Register a new user with email and password. [1]                  |
| POST   | `/auth/login`          | Public    | Log in and receive access and refresh tokens. [1]                 |
| GET    | `/public/info`         | Public    | Returns a public welcome message. [1]                             |
| GET    | `/protected/profile`   | Protected | Returns verified user metadata. [1]                               |
| GET    | `/protected/dashboard` | Protected | Example protected route using shared middleware. [1]              |
| POST   | `/auth/logout`         | Protected | Logs out the authenticated user and returns `204 No Content`. [1] |
| GET    | `/docs`                | Public    | Swagger UI documentation. [1]                                     |

## Stage Summary

### Stage 1 — Signup and Login

Implemented `POST /auth/signup` and `POST /auth/login` using Supabase Auth. The API validates missing `email` or `password`, returns `201 Created` for successful signup, returns `200 OK` with `access_token` and `refresh_token` for successful login, and returns `401` for invalid credentials.

### Stage 2 — Public and Protected Routes

Added `GET /public/info` as a public endpoint and created `GET /protected/profile` with bearer-token presence checks. At this stage, the protected route only required a token to be present in the `Authorization` header and returned `401` if the header was missing or malformed.

### Stage 3 — JWT Verification

Upgraded `GET /protected/profile` to verify the token by calling `supabase.auth.getUser(token)`. Valid tokens return safe user metadata (`id`, `email`, `created_at`), while invalid or expired tokens return `401 Unauthorized`.

### Stage 4 — Auth Middleware and Logout

Extracted token verification into reusable Express middleware and applied it to multiple protected routes. Added `POST /auth/logout` as a protected endpoint that calls Supabase sign-out and returns `204 No Content` on success.

### Stage 5 — Swagger UI Documentation

Created `openapi.json` with JWT bearer authentication under `securitySchemes`, linked it to protected endpoints and logout, and served the docs using `swagger-ui-express` at `/docs`. Swagger UI supports JWT authorization through the **Authorize** button, allowing protected routes to be tested directly in the browser.

## Authentication Flow

1. Sign up with email and password.
2. Log in to receive an access token and refresh token. [1]
3. Send the access token in the `Authorization` header as `Bearer <token>` when accessing protected routes. [1]
4. Use the same bearer token in Swagger UI via the **Authorize** modal to test protected endpoints in the browser. [1]

## Swagger UI

Swagger UI is available at:

```bash
http://localhost:3000/docs
```

Protected endpoints are marked with a lock icon because the OpenAPI spec defines a bearer authentication scheme with `type: http`, `scheme: bearer`, and `bearerFormat: JWT`. This allows JWT-based testing directly inside the docs interface. [1]

## Screenshots

The screenshots below document the implementation and testing of each stage in the authentication workflow.

### Stage 1 — Signup and Login

Successful signup and login flow using Supabase Auth. The login endpoint returns an access token and refresh token for authenticated requests.

![Stage 1 — Signup and Login](screenshot/Stage%201-screenshot.png)

---

### Stage 2 — Public and Protected Routes

Public endpoint access and protected-route validation. Requests without a bearer token are rejected with `401 Unauthorized`.

![Stage 2 — Public and Protected Routes](screenshot/Stage%202-screenshot.png)

---

### Stage 3 — JWT Token Verification

Protected profile access after Supabase verifies a valid JWT. The response returns safe user metadata: user ID, email, and account creation date.

![Stage 3 — JWT Token Verification](screenshot/Stage%203-screenshot.png)

---

### Stage 4 — Authentication Middleware and Logout

Reusable authentication middleware was implemented and applied to protected routes, including the logout endpoint. The logout endpoint returns `204 No Content` after a successful authenticated sign-out.

> **Screenshot not available for Stage 4.**

---

### Stage 5 — Swagger UI with Bearer Authentication

Swagger UI is served at `/docs` with JWT bearer authorization enabled. The protected profile endpoint was successfully tested through the browser using the **Authorize** flow.

![Stage 5 — Swagger UI Bearer Authentication](screenshot/Stage%205-screenshot.png)

## Notes

- Do not commit real access tokens, refresh tokens, or sensitive `.env` values to GitHub.
- Use the Supabase anon key, not the service role key, for this assignment setup.
- If email confirmation is enabled in Supabase Auth, new accounts may need verification before first login.

## Author

**Steven Flogio**  
Backend Track Intern  
Flyrank Internship
