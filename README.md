## Generate database
```bash
alembic init migrations
alembic revision --autogenerate -m "initial tables"
alembic upgrade head
```

## Start app
```bash
uvicorn app.main:app --reload
```

## Seed data
```bash
python -m app.core.seed --truncate
```

---

# List with pagination only
GET /projects?page=1&page_size=20

# Filter by status
GET /projects?status=active&page=1

# Search in title/description
GET /projects?search=backend&page=1

# Sort by title ascending
GET /projects?sort_by=title&order=asc

# Combine all
GET /projects?status=active&search=api&sort_by=updated_at&order=desc&page=2&page_size=10

# Single resource endpoints (NO pagination)
POST /projects          # Returns single project
GET /projects/123       # Returns single project
PATCH /projects/123     # Returns single updated project
DELETE /projects/123 