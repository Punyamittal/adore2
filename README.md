# adore2 — Task Manager Backend Assignment

This project is a small **FastAPI** service backed by **SQLite** (via **SQLAlchemy**) for managing hierarchical tasks. It is meant to assess Python skills through **Level 1** (easier to moderate) and **Level 2** (moderate to hard) coding tasks.

Your goal is to implement the required behavior so every route behaves as described, keep dependencies declared in `requirements.txt`, and verify behavior using the interactive docs at `/docs`.

---

## Table of contents

1. [Tech stack](#tech-stack)
2. [Repository layout](#repository-layout)
3. [Prerequisites](#prerequisites)
4. [Setup and run](#setup-and-run)
5. [Database](#database)
6. [Data model](#data-model)
7. [API overview](#api-overview)
8. [Assignment questions vs code](#assignment-questions-vs-code)
9. [Question reference (official brief)](#question-reference-official-brief)
10. [Tips and troubleshooting](#tips-and-troubleshooting)
11. [Upstream and license](#upstream-and-license)

---

## Tech stack

| Piece | Role |
|--------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | HTTP API and OpenAPI (`/docs`) |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server |
| [SQLAlchemy 1.4](https://docs.sqlalchemy.org/en/14/) | ORM and queries |
| [Pydantic v2](https://docs.pydantic.dev/) | Request/response validation |
| [RapidFuzz](https://github.com/maxbachmann/RapidFuzz) | Fuzzy name matching (Question 6) |
| SQLite (`tasks.db`) | Persistent storage (file created next to `app` when the server runs) |

---

## Repository layout

```
storewise-backend-assignment/
├── README.md                 # This file
├── LICENSE
├── requirements.txt          # Pin your dependencies here
└── app/
    ├── main.py               # FastAPI app, routes, DB session, Question 8 route logic
    ├── models.py             # SQLAlchemy `Task` model and engine
    └── task_logic.py         # Pure functions for Questions 2–3, 5–7, 9 (and helper Q4 logic if used)
```

**Naming note:** The original assignment text sometimes refers to `tasks_logic.py`. In this repository the module is **`task_logic.py`**, imported in `main.py` as `from task_logic import *`.

---

## Prerequisites

- **Python 3.9+** recommended (3.10+ is commonly used with these pins).
- **pip** available on your PATH ([pip installation](https://pip.pypa.io/en/stable/installation/)).

---

## Setup and run

### 1. Clone and enter the project

```bash
git clone https://github.com/achalagarwal/storewise-backend-assignment
cd storewise-backend-assignment
```

If you are new to folders and the terminal, this video may help: [YouTube — navigation basics](https://youtu.be/D1Oe7b0RaFA?si=7XZi6mmUy0bbWacj).

### 2. (Recommended) Create a virtual environment

Using a venv avoids changing your global Python packages.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

From the **project root** (folder that contains `requirements.txt`):

```bash
pip install -r requirements.txt
```

You can instead install each package listed in `requirements.txt` manually if you prefer.

### 4. Start the API from the `app` directory

The application imports `models` and `task_logic` as sibling modules, so run commands with **`app` as the working directory**.

```bash
cd app
fastapi dev
```

Alternatives:

```bash
cd app
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Or run `main.py` if your environment is configured to launch it (the supported path above is `fastapi dev` or `uvicorn`).

### 5. Open the docs

When the terminal shows **Application startup complete**, open:

- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- Alternative ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

**Replit:** Use the Networks / ports panel to expose internal port **8000** as external **8000** if needed.

![Server running](image.png)

---

## Database

- **URL:** `sqlite:///./tasks.db` (see `app/models.py`).
- **File location:** `tasks.db` is typically created in the **current working directory** when the app starts (often `app/` if you start the server from there).
- **Schema:** Tables are created with `Base.metadata.create_all(bind=engine)` on startup in `main.py`.

You normally **do not commit** `tasks.db` to version control; reviewers can start a fresh database and use `POST /tasks` to seed data.

---

## Data model

The `tasks` table is defined in `app/models.py`. Fields:

| Column | Type | Notes |
|--------|------|--------|
| `id` | Integer | Primary key |
| `name` | String | Task title |
| `description` | String | Optional text |
| `due_date` | DateTime | Deadline |
| `priority` | Integer | Lower value = higher priority (per assignment wording) |
| `status` | String | e.g. `pending`, `completed` |
| `parent_id` | Integer, nullable | Self-referential FK to `tasks.id` |
| `created_at` | DateTime | Default UTC time at insert |
| `duration` | Integer | Minutes (used in Question 9 simulation) |

---

## API overview

Base URL (local): `http://127.0.0.1:8000`

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Welcome message and doc hint |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task (JSON body) |
| DELETE | `/tasks/{task_id}` | Delete task by id (path parameter) |
| GET | `/tasks/question2` | Tasks grouped by `parent_id`, newest first within each group |
| GET | `/tasks/question3` | Tasks due **today or tomorrow** with **priority 1** |
| GET | `/tasks/question4` | Tasks that have **no subtasks** (SQL join in `main.py`) |
| GET | `/tasks/question5/{task_id}` | Sibling count for the given task |
| GET | `/tasks/question6/{query}` | Fuzzy match on task **names** (`query` is a path segment; URL-encode spaces) |
| GET | `/tasks/question7` | Query: `task_id_a`, `task_id_b` — subtask relationship or `NONE` |
| GET | `/tasks/question8` | Filtered tasks + optional `sort_by` / `sort_desc` (see below) |
| POST | `/tasks/question9/{worker_threads}` | Thread-pool simulation using `duration` |

### Create task (`POST /tasks`)

JSON body fields:

| Field | Required | Description |
|--------|----------|-------------|
| `name` | Yes | Task name |
| `description` | No | Description |
| `due_date` | Yes | ISO 8601 string, e.g. `2026-04-10T14:30:00` ([ISO 8601](https://en.wikipedia.org/wiki/ISO_8601)) |
| `priority` | No (default `1`) | Lower = higher priority |
| `status` | No (default `pending`) | Current status |
| `parent_id` | No | Parent task id |
| `duration` | No (default `0`) | Duration in minutes |

### Delete task (`DELETE /tasks/{task_id}`)

The implementation uses the **path parameter** `task_id`. Some assignment PDFs mention a JSON body; this codebase deletes by **URL path only**.

### Question 8 query parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `sort_by` | `created_at` | One of: `created_at`, `due_date`, `priority`, `name`, `id`, `status` |
| `sort_desc` | `false` | Sort descending when `true` |

Filters applied in the route (SQLAlchemy / SQLite):

- `created_at` from **2024-08-26 00:00:00** through **2024-09-09 23:59:59** (inclusive end of day).
- Exclude rows whose `status` equals **`completed`** (case-insensitive).
- Exclude tasks created on **Sunday** (`strftime('%w', created_at) == '0'` in SQLite).

### Question 9 (`POST /tasks/question9/{worker_threads}`)

- `worker_threads`: number of worker threads (must be ≥ 1).
- Each task’s simulated work time is **`duration / 10`** seconds (sleep), run concurrently up to the pool size.

---

## Assignment questions vs code

| Question | Where to implement | How it is exposed |
|----------|-------------------|-------------------|
| 1 | No code required | Use `GET/POST/DELETE /tasks` via `/docs` |
| 2 | `task_logic.py` → `question2` | `GET /tasks/question2` |
| 3 | `task_logic.py` → `question3` | `GET /tasks/question3` |
| 4 | Prefer SQL in `main.py` (join) | `GET /tasks/question4` |
| 5 | `task_logic.py` → `question5` | `GET /tasks/question5/{task_id}` |
| 6 | `task_logic.py` → `question6` (+ dependency in `requirements.txt`) | `GET /tasks/question6/{query}` |
| 7 | `task_logic.py` → `question7` | `GET /tasks/question7?task_id_a=&task_id_b=` |
| 8 | Router in `main.py` only (SQLAlchemy query) | `GET /tasks/question8` |
| 9 | `task_logic.py` → `question9` | `POST /tasks/question9/{worker_threads}` |

---

## Question reference (official brief)

### Level 1

**Question 1:** Call the API to list tasks, create a task, and delete a task.

**Question 2:** Group by `parent_id`, sort by creation date **descending** within each group. Logic belongs in **`task_logic.py`**, not in `main.py` for this part.

**Question 3:** Tasks with **due date today or tomorrow** and **priority 1**.

**Question 4:** Tasks with **no child tasks** (interpretation: no other task lists this task as `parent_id`). A SQL **join** is the suggested approach.

**Question 5:** Count **siblings** (same `parent_id`), excluding the task itself; task id comes from the route.

### Level 2

**Question 6:** **Fuzzy search** on task names; any library is allowed.

**Question 7:** For two tasks, determine which is a **subtask** of the other (transitive ancestry). Return **NONE** if unrelated.

**Question 8:** Implement in **`main.py`** router using **SQL** (via SQLAlchemy):

- Created between **26 August 2024** and **9 September 2024**
- Exclude **completed** tasks
- Exclude tasks created on **Sunday**

**Question 9:** **Asynchronous-style** execution with a **thread pool** of size `worker_threads`; simulated duration **`duration / 10`** seconds per task.

---

## Tips and troubleshooting

- **`ModuleNotFoundError` for `models` or `task_logic`:** Run the server from the **`app`** directory, or set `PYTHONPATH` to include `app`.
- **Port already in use:** Use another port, e.g. `uvicorn main:app --port 8001`.
- **Path parameter with spaces (Question 6):** Encode the query (e.g. `my%20task`) or use a client that URL-encodes automatically.
- **`fromisoformat` errors on `due_date`:** Use a valid ISO string; for UTC you may use `2026-04-10T14:30:00+00:00`.

---

## Upstream and license

Original template: [github.com/achalagarwal/storewise-backend-assignment](https://github.com/achalagarwal/storewise-backend-assignment)

See `LICENSE` in this repository for license text.

Good luck with the assignment.
