from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes import user_routes
from app.routes import daily_routes

app = FastAPI()

# -------------------------------
# 📁 PATH SETUP (IMPORTANT)
# -------------------------------

CURRENT_FILE = os.path.abspath(__file__)

APP_DIR = os.path.dirname(CURRENT_FILE)              # backend/app
BACKEND_DIR = os.path.dirname(APP_DIR)               # backend
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)          # HEIE

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
INDEX_FILE = os.path.join(FRONTEND_DIR, "index.html")

# -------------------------------
# 🔗 ROUTES
# -------------------------------

app.include_router(user_routes.router)
app.include_router(daily_routes.router)

# -------------------------------
# 🌐 ROOT
# -------------------------------

from pathlib import Path
from fastapi.responses import FileResponse

@app.get("/")
def root():
    base_dir = Path(__file__).resolve().parent.parent  # goes to backend/

    file_path = base_dir / "frontend" / "index.html"

    if not file_path.exists():
        return {"error": f"Frontend not found at {file_path}"}

    return FileResponse(file_path)
# -------------------------------
# 📊 DASHBOARD (Frontend)
# -------------------------------

@app.get("/dashboard")
def serve_dashboard():
    current_file = os.path.abspath(__file__)
    app_dir = os.path.dirname(current_file)          # backend/app
    backend_dir = os.path.dirname(app_dir)           # backend

    file_path = os.path.join(backend_dir, "frontend", "index.html")

    if not os.path.exists(file_path):
        return {"error": f"Frontend not found at {file_path}"}

    return FileResponse(file_path)

# -------------------------------
# 🔓 CORS (for frontend calls)
# -------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)