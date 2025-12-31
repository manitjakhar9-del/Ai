from fastapi import FastAPI
from pydantic import BaseModel
import os
from groq import Groq

app = FastAPI()

# Load Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class Chat(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "Manit AI is running"}

@app.post("/chat")
def chat(req: Chat):
    try:
        response = client.chat.completions.create(
            model="groq/openai/gpt-oss-120b"
            messages=[
                {"role": "system", "content": "You are Manit AI, a powerful RPG simulation and assistant."},
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
