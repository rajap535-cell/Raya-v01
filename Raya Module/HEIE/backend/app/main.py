from fastapi import FastAPI
from app.routes import user_routes
from app.routes import daily_routes
from fastapi.responses import FileResponse
app = FastAPI()
import os

app.include_router(user_routes.router)
app.include_router(daily_routes.router)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.get("/")
def root():
    return {"message": "HEIE Backend Running"}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)