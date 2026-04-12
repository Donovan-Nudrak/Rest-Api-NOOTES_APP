# Notes REST API

Backend HTTP API for user registration, session-based authentication, and personal notes. Users can create notes, list notes they own or that were shared with them, update accessible notes, delete their own notes, and share a note with another registered user by email. Responses are JSON; there is no HTML frontend in this repository.

## Tech Stack


| Component        | Usage                                                             |
| ---------------- | ----------------------------------------------------------------- |
| Flask            | Application object, blueprints, `request` / `jsonify` / `session` |
| Flask-SQLAlchemy | ORM, `db` instance, `db.create_all()`                             |
| SQLite           | File database at `database/notes_app.db` (development config)     |
| Werkzeug         | Password hashing and verification (`utils/security.py`)           |
| Flask `session`  | Cookie-backed server-side session after login                     |


## Architecture Overview

The code is split into four main layers:

- `**routes/**` — HTTP adapters. Read JSON bodies and `session`, call services, return `jsonify(...)` with HTTP status codes. No business rules beyond wiring.
- `**services/**` — Application logic: validation orchestration, database queries, commits, sharing rules, and structured return values (`status`, `message` or `errors`, `code`). Optional calls to `log_api_action` for auditing.
- `**models/**` — SQLAlchemy models (`User`, `Note`, association table `note_shares`) defining tables and relationships.
- `**utils/**` — Cross-cutting helpers: input validators (`validators.py`), user-facing strings (`messages.py`), password helpers (`security.py`), file logging (`logger.py`).

`app.py` loads configuration, registers blueprints, and runs `db.create_all()` inside an app context. `database/db.py` exports the shared `SQLAlchemy()` instance used by models and the app.

## Project Structure

```
├── app.py
├── config.py
├── bash_script.sh
├── database/
│   ├── db.py
│   └── notes_app.db          # created at runtime (SQLite)
├── models/
│   ├── user.py
│   └── note.py
├── routes/
│   ├── auth_routes.py
│   └── note_routes.py
├── services/
│   ├── auth_services.py
│   └── note_services.py
├── utils/
│   ├── validators.py
│   ├── messages.py
│   ├── security.py
│   └── logger.py
└── logs/
    └── api_activity.log      # created when logging runs
```

## Installation and Setup

```bash
git clone <repository-url>
cd NOTES_APP
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the development server (uses `DevelopmentConfig` from `config.py`):

```bash
python app.py
```

The default Flask development URL is `http://127.0.0.1:5000/`. Set `SECRET_KEY` in the environment for any non-local deployment; the app reads it via `os.environ.get('SECRET_KEY', ...)`.

## API Endpoints


| Method | Path                   | Description                                                 |
| ------ | ---------------------- | ----------------------------------------------------------- |
| GET    | `/`                    | Health-style JSON: `{"message": "API running"}`             |
| POST   | `/api/auth/register`   | Create account (`username`, `email`, `password` JSON)       |
| POST   | `/api/auth/login`      | Authenticate; sets session cookie                           |
| GET    | `/api/notes/`          | Returns notes for the session user (owned and shared)       |
| POST   | `/api/notes/create`    | Create a note for the session user                          |
| POST   | `/api/notes/share`     | Owner shares a note with another user by email              |
| GET    | `/api/notes/<note_id>` | Get one note if caller is owner or share recipient          |
| PUT    | `/api/notes/<note_id>` | Update `title` and/or `content` if owner or share recipient |
| DELETE | `/api/notes/<note_id>` | Delete note (owner only)                                    |


All JSON endpoints expect `Content-Type: application/json` where a body is used.

**Request JSON fields (from routes and services)**


| Endpoint                   | Body fields                                                                                                                                                                                                           |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST /api/auth/register`  | `username`, `email`, `password`                                                                                                                                                                                       |
| `POST /api/auth/login`     | `email`, `password`                                                                                                                                                                                                   |
| `POST /api/notes/create`   | `title`, `content`; optional `visibility` (read in `create_note` via `data.get("visibility", "private")`, not validated by `validate_create_note`)                                                                    |
| `POST /api/notes/share`    | `note_id`, `target_email`                                                                                                                                                                                             |
| `PUT /api/notes/<note_id>` | Optional `title` and/or `content`. `validate_update_note` only checks keys that are present; each supplied field must be a non-empty string with the same length bounds as create (`title` 1–100, `content` 1–10000). |


## Authentication

Login and register do not require a prior session. Successful `POST /api/auth/login` stores `user_id` in the Flask server-side session (`session["user_id"]` in `routes/auth_routes.py`). Note routes that use `session.get("user_id")` (create, list, share, and per-note GET/PUT/DELETE) expect that session cookie on the request.

Protected behavior is enforced in services (missing or unknown user, wrong password, note access) and reflected in HTTP status codes and JSON error bodies. There is no JWT or API-key layer in this codebase.

## Request and Response Examples

Field rules below match `utils/validators.py`.

### Register

`username`: string, 5–64 characters, `[A-Za-z0-9_]` only.  
`email`: string, length 5–254, single `@`, domain part must contain `.`.  
`password`: string, length 10–128, at least one lowercase, one uppercase, one digit, and one non-alphanumeric symbol.

```bash
curl -sS -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"jdoe_api","email":"jdoe@example.com","password":"Aa1!aaaaaaaa"}'
```

Success (example): HTTP `201`, body `{"message": "<user-created message>"}`.  
Failure: HTTP `400` or `409`, body `{"errors": [...]}` where `errors` is always a **list** of human-readable strings for this route.

### Login

`email` and `password` are checked by `validate_login`: same email string rules as register (length 5–254, exactly one `@`, `.` in the domain segment). `password` must be a string with length between 10 and 128 inclusive; register-time complexity (mixed case, digit, symbol) is **not** applied on login.

```bash
curl -sS -c cookies.txt -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jdoe@example.com","password":"Aa1!aaaaaaaa"}'
```

Success: HTTP `200`, body `{"message": "<login message>"}` and `Set-Cookie` stored in `cookies.txt` for later requests.

Failure: HTTP `400` with `{"errors": [...]}` for validation failures; HTTP `404` or `401` with `{"errors": "<single string>"}` when the user is missing or the password does not verify (`auth_services.login_user`).

### Create note

Requires session cookie from login.  
`title`: string, length 1–100.  
`content`: string, length 1–10000.  
`visibility` is read in `note_services.create_note` with default `"private"` if omitted (not validated by `validate_create_note`).

```bash
curl -sS -b cookies.txt -c cookies.txt -X POST http://127.0.0.1:5000/api/notes/create \
  -H "Content-Type: application/json" \
  -d '{"title":"Meeting notes","content":"Discuss release timeline.","visibility":"private"}'
```

Success: HTTP `201`, body `{"message": "<note-created message>"}`.  
Failure: HTTP `400` / `404` / etc., body `{"errors": ...}` (see next section).

### List and fetch notes

```bash
curl -sS -b cookies.txt http://127.0.0.1:5000/api/notes/
curl -sS -b cookies.txt http://127.0.0.1:5000/api/notes/1
```

When `user_id` is present in the session, list returns a JSON array of note objects (fields from `_serialize_note` in `note_services.py`: `id`, `title`, `content`, `user_id`, `owner_username`, `visibility`, `created_at`, `updated_at` as ISO strings). If there is no session, `get_notes` still returns a dict with `status`, `errors`, and `code`, and the list route responds with HTTP `200` and that JSON object as the body (same route always uses status 200 for this handler). Single-note GET returns one note object on success or `{"errors": ...}` with an error status when the service reports failure.

## Error Handling

For most failing auth and note operations, routes return `jsonify({"errors": errors})` with an HTTP status taken from the service `code`. The `errors` value is usually a **list of strings** (from `utils.messages` via validator enum lists), but some branches use a **single string** (for example direct `get_note_error_message` results in `note_services.py`). Some database failures surface the literal string `"IntegrityError"` in `errors`.

`GET /api/notes/` is different: the handler always responds with HTTP `200` and passes through either the note array or the service error dict, so that payload may include `status` and `code` alongside `errors` when there is no session user id.

Successful `POST` responses for register, login, create note, and share return `{"message": "..."}` with the status code from the service. Successful `DELETE` returns `jsonify({"message": message})` where `message` is a plain string, so the HTTP body is a **JSON string** (quoted text), not an object with a `message` key. Successful `GET /api/notes/<note_id>` returns one serialized note object. 

Human-readable text is centralized in `utils/messages.py` (enums and dictionaries, resolved through `get_user_error_message`, `get_note_error_message`, and success helpers).

## Design Decisions

- **Services layer** — Keeps route handlers thin, concentrates transactions and rules (ownership, sharing, validation order), and returns a small contract (`status`, `code`, plus `message`, `errors`, or serialized note data) that routes map to HTTP.
- **Session authentication** — Fits a cookie-based browser or API client without issuing tokens in code; `SECRET_KEY` secures session signing.
- **Validation and messages** — Validators return either `True` or a list of enum codes; services translate codes to strings via `messages.py`, so copy and language stay in one place and routes stay unaware of enum details.

## Testing

`bash_script.sh` is an optional shell integration script. It calls the live API with `curl`, maintains a cookie jar (`cookie.txt`), and appends outcomes to `success.txt` and `errors.txt`. It covers the root endpoint, invalid and valid registration, duplicate register, failed login, successful login, note validation failure, note creation, listing and CRUD by id, sharing with a second user registered without cookies, delete, and an unauthenticated `GET /api/notes/` check.

Requirements: Bash, `curl`, and `python3` (used to parse a note id from list JSON). Override the base URL with `BASE_URL`, for example:

```bash
BASE_URL=http:localhost:5000 ./bash_script.sh
```

This is a manual smoke-style flow, not a pytest suite.

## Notes

- Tables are created automatically when the application module loads: `with app.app_context(): db.create_all()` in `app.py`. There is no separate SQL migration folder in the repository.
- The project is **API-only**; no static site or SPA is included.

