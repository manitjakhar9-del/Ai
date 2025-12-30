from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests

app = FastAPI()

GROQ_KEY = os.getenv("GROQ_API_KEY")

class Chat(BaseModel):
    message: str

@app.post("/chat")
def chat(req: Chat):
    headers = {
        "Authorization": "Bearer " + GROQ_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role":"system","content":"You are a helpful AI assistant."},
            {"role":"user","content": req.message}
        ]
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    return {"reply": r.json()["choices"][0]["message"]["content"]}
