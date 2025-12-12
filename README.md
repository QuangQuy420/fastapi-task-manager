# Task Management by FastAPI

Building REST APIs with FastAPI

---

## 1. How to Start the Application with Docker (Recommended for WSL or Linux environments)

### 1.1. Clone the project
```bash
git clone git@github.com:QuangQuy420/fastapi-task-manager.git
cd fastapi-task-manager
```

### 1.2. Configure .env
```bash
cp .env.example .env
```

### 1.3. Build and Start
```bash
docker compose up -d --build
```

### 1.4. Run Migrations manually
```bash
docker compose exec api mkdir migrations/versions
docker compose exec api alembic revision --autogenerate -m "init_db"
docker compose exec api alembic upgrade head
```

### 1.5. Run seed data manually (Optional - If it occurs an error, run it again)
```bash
docker compose exec api python -m app.core.seed
```

### You can now access your API at http://localhost:8000/docs to check the document from Swagger.

### 1.5. Stop Application
```bash
docker compose down
```

---

## 2. Test API (Using Postman or http://localhost:8000/docs)

### 2.1. Register/Sign In
```bash
POST /api/auth/register
Body (example):
{
  "email": "quy@example.com",
  "fullname": "quy",            # Optinal           
  "password": "secret123"
}

Response:
{
    "id": 167
    "email": "quy@gmail.com",
    "full_name": null,
}
```

### 2.2. Login to get token
```bash
POST /api/auth/login
Body (example):
{
  "username": "quy@example.com",
  "password": "secret123"
}

Response:
{
  "access_token": "<access_token_here>"
  "token_type": "bearer"
}
```

### 2.3. Logout
```bash
POST /api/auth/logout
Header: Authorization: Bearer <access_token_here>

Response:
{
    "detail": "Logged out successfully"
}
```

### 2.4. Refresh access token and rotate refresh token
```bash
POST /api/auth/refresh

Response:
{
  "access_token": "<access_token_here>"
  "token_type": "bearer"
}
```

### 2.5. Create a project
```bash
POST /api/projects/
Header: Authorization: Bearer <access_token_here>

Body (example):
{
    "title": "Project 8",
    "description": "FastAPI framework", # Optional
    "status": "planned" # Optinal <planned/active/completed/cancelled/archived>
}

Response:
{
    "title": "Project 8",
    "description": "FastAPI framework",
    "status": "planned",
    "id": 51,
    "managed_by": 77,
    "created_at": "2025-12-12T02:20:08.888045",
    "updated_at": "2025-12-12T02:20:08.888045"
}
```

### 2.6. Get all Projects of user
```bash
GET /api/projects
Header: Authorization: Bearer <access_token>

Response:
{
    "items": [
        {...Project},
        {...Project}
    ],
    "total": 2,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
}

```

### 2.7. Retrieve a Project
```bash
GET /api/projects/{project_id}/
Header: Authorization: Bearer <access_token>

Response:
{
    "title": "Project 8",
    "description": "FastAPI framework",
    "status": "planned",
    "id": 51,
    "managed_by": 77,
    "created_at": "2025-12-12T02:20:08.888045",
    "updated_at": "2025-12-12T02:20:08.888045",
    "sprints": [
        {...sprint},
        {...sprint},
    ]
}
```

### 2.8. Update a project
```bash
PATCH /api/projects/{project_id}
Header: Authorization: Bearer <access_token>

Body (example):
{
    "title": "Project 8",
    "description": "FastAPI framework", # Optional
    "status": "planned" # Optinal <planned/active/completed/cancelled/archived>
}

Response:
{
    "title": "Project 8",
    "description": "FastAPI framework",
    "status": "planned",
    "id": 51,
    "managed_by": 77,
    "created_at": "2025-12-12T02:20:08.888045",
    "updated_at": "2025-12-12T02:20:08.888045"
}
```

### 2.9. Delete a project (Soft Delete)
```bash
DELETE /api/projects/{project_id}
Header: Authorization: Bearer <access_token>

Response: 204 No Content
```

### 2.10. Creata a Sprint
```bash
POST api/projects/{project_id}/sprints/
Header: Authorization: Bearer <access_token>

Body (example):
{
    "title": "Sprint 2",
    "description": "FastAPI framework", # Optinal
    "status": "new",                    # Optinal <new/planned/active/completed/cancelled/archived>
    "start_date": "2025-12-05",
    "end_date": "2025-12-19"
}

Response:
{
    "title": "Sprint 2",
    "description": "FastAPI framework",
    "status": "new",
    "start_date": "2025-12-05",
    "end_date": "2025-12-19",
    "id": 501,
    "project_id": 52,
    "created_at": "2025-12-12T02:40:30.679790",
    "updated_at": "2025-12-12T02:40:30.679790"
}
```

### 2.11. Get all sprints in project
```bash
GET /api/projects/{project_id}/sprints
Header: Authorization: Bearer <access_token>

Response: 
"items": [
        {...sprint},
        {...sprint},
    ],
    "total": 2,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
}
```

### 2.12. Get sprint detail
```bash
GET /api/sprints/{sprint_id}
Header: Authorization: Bearer <access_token>

Response:
{
    "title": "Away provide system character.",
    "description": "Four sell pick sound with research.",
    "status": "new",
    "start_date": "2025-12-02",
    "end_date": "2025-12-11",
    "id": 159,
    "project_id": 16,
    "created_at": "2025-12-12T02:05:02.806129",
    "updated_at": "2025-12-12T02:05:02.806129"
}
```

### 2.13. Update a sprint
```bash
PATCH /api/sprints/{sprint_id}
Header: Authorization: Bearer <access_token>

Body (example):
{
    "title": "Sprint 2",
    "description": "FastAPI framework", # Optinal
    "status": "new",                    # Optinal <new/planned/active/completed/cancelled/archived>
    "start_date": "2025-12-05",
    "end_date": "2025-12-19"
}

Response:
{
    "title": "Sprint 2",
    "description": "FastAPI framework",
    "status": "new",
    "start_date": "2025-12-05",
    "end_date": "2025-12-19",
    "id": 501,
    "project_id": 52,
    "created_at": "2025-12-12T02:40:30.679790",
    "updated_at": "2025-12-12T02:40:30.679790"
}
```

### 2.14. Delete a sprint
```bash
DELETE /api/sprints/{sprint_id}/
Header: Authorization: Bearer <access_token>

Response: 204 No Content
```

### 2.15. Creata a task
```bash
POST /api/projects/{project_id}/tasks/
Header: Authorization: Bearer <access_token>

Body (example):
{
  "title": "Task 1",
  "description": "description Task 1",      # Optinal
  "status": "new",                          # Optinal <new/todo/in_progress/review/in_testing/done>
  "priority": 3,                            # Optinal <1/2/3/4>
  "assigned_to": 1,                         # Optinal              
  "due_date": "2025-12-11T03:50:47.944080", # Optinal
  "sprint_id": null,                        # Optinal
  "parent_id": 500002                       # Optinal
}

Response:
{
    "title": "Task 1",
    "description": "description Task 1",
    "status": "new",
    "priority": 3,
    "assigned_to": null,
    "due_date": "2025-12-11T03:50:47.944080",
    "id": 5001,
    "project_id": 53,
    "sprint_id": null,
    "parent_id": null,
    "created_at": "2025-12-12T02:53:40.444352",
    "updated_at": "2025-12-12T02:53:40.444352"
}
```

### 2.16. Get all tasks of project
```bash
GET /api/projects/{project_id}/tasks/
Header: Authorization: Bearer <access_token>

Response:
{
    "items": [
        {...task},
        {...task},
    ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
}
```

### 2.17. Get task detail
```bash
GET /api/tasks/{task_id}
Header: Authorization: Bearer <access_token>

Response:
{
    "title": "Full garden much piece.",
    "description": "Standard financial anyone style myself. Hard store without sound couple what present wind.",
    "status": "done",
    "priority": 3,
    "assigned_to": 134,
    "due_date": "2026-05-04T02:05:03.041631",
    "id": 1581,
    "project_id": 16,
    "sprint_id": 153,
    "parent_id": null,
    "created_at": "2025-12-12T02:05:03.041633",
    "updated_at": "2025-12-12T02:05:03.041633"
}
```

### 2.18. Update task
```bash
PATCH /api/tasks/{task_id}
Header: Authorization: Bearer <access_token>

Body (example):
{
  "title": "Task 1",
  "description": "description Task 1",      # Optinal
  "status": "new",                          # Optinal <new/todo/in_progress/review/in_testing/done>
  "priority": 3,                            # Optinal <1/2/3/4>
  "assigned_to": 1,                         # Optinal              
  "due_date": "2025-12-11T03:50:47.944080", # Optinal
  "sprint_id": null,                        # Optinal
  "parent_id": 500002                       # Optinal
}

Response:
{
    "title": "Task 1",
    "description": "description Task 1",
    "status": "new",
    "priority": 3,
    "assigned_to": null,
    "due_date": "2025-12-11T03:50:47.944080",
    "id": 5001,
    "project_id": 53,
    "sprint_id": null,
    "parent_id": null,
    "created_at": "2025-12-12T02:53:40.444352",
    "updated_at": "2025-12-12T02:53:40.444352"
}
```

### 2.19. Delete task
```bash
DELETE /api/tasks/{task_id}
Header: Authorization: Bearer <access_token>

Response: 204 No Content
```

---
