from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.api.routes import router as api_router
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t%(message)s"
)

app = FastAPI(title=settings.PROJECT_NAME)

# Include API routes under prefix /api
app.include_router(api_router, prefix="/api")

# Configure templates path relative to this file
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Renders the web-based test interface for Northstar One.
    """
    return templates.TemplateResponse("index.html", {"request": request, "project_name": settings.PROJECT_NAME})

@app.get("/health")
async def health_check():
    """
    Standard application health endpoint.
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "model": settings.LLM_MODEL
    }
