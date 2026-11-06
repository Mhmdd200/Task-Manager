import logging

from fastapi import FastAPI
from app.exception_handlers import handle_crash
from app.middleware import log_requests
from app.routers import auth, projects, users

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Task Manager Api")
app.add_exception_handler(Exception, handle_crash)
app.middleware("http")(log_requests)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)

@app.get("/health")
def health():
    return {"status": "ok"}
