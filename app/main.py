from fastapi import FastAPI
from app.core.db import Base, engine
from app.api.routes import tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")
app.include_router(tasks.router)
