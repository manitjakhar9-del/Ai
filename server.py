from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests

app = FastAPI()

API_KEY = os.getenv("GEMINI_API_KEY")

class Chat(BaseModel):
    message: str

@app.post("/chat")
def chat(req: Chat):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + API_KEY

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": req.message}
                ]
            }
        ]
    }

    r = requests.post(url, json=payload)
    return r.json()
