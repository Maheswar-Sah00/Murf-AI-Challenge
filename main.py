from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# CORS middleware to allow frontend JS to call backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve HTML/CSS/JS from static folder
app.mount("/static", StaticFiles(directory="static"), name="static")
from dotenv import load_dotenv
load_dotenv()
# Load your Murf API key from environment variable
MURF_API_KEY = os.getenv("MURF_API_KEY", "YOUR_MURF_API_KEY")  # Change this or load from .env

# Homepage (serves HTML file)
@app.get("/")
def read_homepage():
    return FileResponse("static/index.html")

# Model for incoming text
class TTSRequest(BaseModel):
    text: str

# POST endpoint to call Murf API
@app.post("/tts")
def generate_audio(req: TTSRequest):
    murf_url = "https://api.murf.ai/v1/speech/generate"
    headers = {
        "api-key": MURF_API_KEY,
        "accept": "application/json",
        "content-type": "application/json"
    }

    payload = {
        "voiceId": "en-US-terrell",  # You can try other voices from Murf
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
