import os
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq

# Load API key from Render environment variable
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = FastAPI()

class Chat(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "Manit AI is running"}

@app.post("/chat")
def chat(req: Chat):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are Manit AI. You simulate real life and RPG worlds."},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7,
            max_tokens=1024
        )

        return {"reply": response.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}
