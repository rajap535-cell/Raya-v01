# disease_service.py
from fastapi import FastAPI, File, UploadFile
import os, uuid

app = FastAPI()
UPLOAD_DIR = "uploads_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    fname = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, fname)
    with open(path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"status": "saved", "filename": fname, "message": "Image saved for training and analysis"}
