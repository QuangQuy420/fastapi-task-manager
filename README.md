# Task Management by FastAPI

FastAPI.

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
docker compose exec api alembic upgrade head
```

### 1.5. Run seed data manually (Optional)
```bash
docker compose exec api python -m app.core.seed
```

### You can now access your API at http://localhost:8000/docs to check the document from Swagger.

---

