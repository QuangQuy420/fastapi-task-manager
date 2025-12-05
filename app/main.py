
import app.models
from fastapi import FastAPI
from app.api.routes import tasks, auth


app = FastAPI(title="Task Manager API")
app.include_router(tasks.router)
app.include_router(auth.router)
