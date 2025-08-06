from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import shutil
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

MURF_API_KEY = os.getenv("MURF_API_KEY", "YOUR_MURF_API_KEY")

@app.get("/")
def read_homepage():
    return FileResponse("static/index.html")

class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
def generate_audio(req: TTSRequest):
    murf_url = "https://api.murf.ai/v1/speech/generate"
    headers = {
        "api-key": MURF_API_KEY,
        "accept": "application/json",
        "content-type": "application/json"
    }

    payload = {
        "voiceId": "en-US-terrell",
        "text": req.text,
        "format": "MP3"
    }

    try:
        response = requests.post(murf_url, headers=headers, json=payload)
        print("Murf API status:", response.status_code)
        print("Murf response:", response.text)

        if response.status_code == 200:
            data = response.json()
            return {"audio_url": data.get("audioFile")}
        else:
            return JSONResponse(status_code=500, content={"error": "Murf API failed", "details": response.text})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Request failed", "details": str(e)})

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": os.path.getsize(file_location)
    }
