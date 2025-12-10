import app.models
from fastapi import FastAPI
from app.api.routes import tasks, auth, projects, sprints

import time
from contextvars import ContextVar
from fastapi import Request
from sqlalchemy import event
from sqlalchemy.engine import Engine
# Import your 'engine' variable here from your database setup file


app = FastAPI(title="Task Manager API")
app.include_router(tasks.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(sprints.router)


# Measure DB query performance using SQLAlchemy events and FastAPI middleware - Test purpose
query_metrics = ContextVar("query_metrics", default={"count": 0, "total_db_time": 0.0})


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    # Store the start time in the connection info
    conn.info.setdefault("query_start_time", []).append(time.perf_counter())

    # Optional: Print the actual SQL query
    # print(f"\n[DB QUERY START] {statement} | Params: {parameters}")


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    # Calculate time taken
    start_time = conn.info["query_start_time"].pop(-1)
    end_time = time.perf_counter()
    duration = end_time - start_time

    # Update the ContextVar metrics safely
    metrics = query_metrics.get()
    metrics["count"] += 1
    metrics["total_db_time"] += duration

    # Print individual query time
    print(f"[DB QUERY FINISH] Time: {duration:.5f}s")


# ---------------------------------------------------------
# 3. FastAPI Middleware (Resets counters & Prints Summary)
# ---------------------------------------------------------


@app.middleware("http")
async def db_performance_logger(request: Request, call_next):
    # Reset metrics at the start of the request
    token = query_metrics.set({"count": 0, "total_db_time": 0.0})

    req_start = time.perf_counter()

    try:
        response = await call_next(request)
        return response
    finally:
        # This block runs AFTER the response is sent
        req_end = time.perf_counter()
        total_req_time = req_end - req_start

        # Get the final DB stats for this request
        final_metrics = query_metrics.get()
        db_count = final_metrics["count"]
        db_time = final_metrics["total_db_time"]

        print(f"\n--- PERFORMANCE REPORT: {request.method} {request.url.path} ---")
        print(f"Total API Time:  {total_req_time:.5f}s")
        print(f"Total DB Queries: {db_count}")
        print(f"Total DB Time:    {db_time:.5f}s")
        print("-------------------------------------------------------------\n")

        # Clean up context var
        query_metrics.reset(token)
