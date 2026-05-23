from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os

from app.routes import user_routes
from app.routes import daily_routes

app = FastAPI()

# -------------------------------
# PATH SETUP
# -------------------------------

CURRENT_FILE = os.path.abspath(__file__)

APP_DIR = os.path.dirname(CURRENT_FILE)
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

FRONTEND_DIR = os.path.join(BACKEND_DIR, "frontend")

# -------------------------------
# ROUTES
# -------------------------------

app.include_router(user_routes.router)
app.include_router(daily_routes.router)

# -------------------------------
# STATIC FRONTEND
# -------------------------------

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# -------------------------------
# CORS
# -------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)