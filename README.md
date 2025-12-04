## Start app
```bash
uvicorn app.main:app --reload
```

## Seed data
```bash
python -m app.core.seed --count 100000 --batch-size 5000 --truncate
```