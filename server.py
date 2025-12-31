import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

# ------------------------
# FastAPI App
# ------------------------
app = FastAPI()

# Allow Netlify & all browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Groq Client
# ------------------------
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ------------------------
# Request Body
# ------------------------
class Chat(BaseModel):
    message: str

# ------------------------
# Root
# ------------------------
@app.get("/")
def home():
    return {"status": "Manit AI is running"}

# ------------------------
# Chat API
# ------------------------
@app.post("/chat")
def chat(req: Chat):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",   # WORKING MODEL
            messages=[
                {"role": "system", "content": "You are Manit AI, a powerful RPG and world simulation AI."},
                {"role": "user", "content": req.message}
            ]
        )

        return {
            "reply": response.choices[0].message.content
        }

    except Exception as e:
        return {
            "error": str(e)
        }
