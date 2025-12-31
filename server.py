import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class Chat(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "Manit AI is running"}

@app.post("/chat")
def chat(req: Chat):
    try:
        response = client.chat.completions.create(
            model="groq/llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are Manit AI, a powerful helpful assistant."},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7,
            max_tokens=512
        )

        return {"reply": response.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}
