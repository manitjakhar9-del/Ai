print("Hello, World!")from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()

class Chat(BaseModel):
    message: str

@app.post("/chat")
def chat(req: Chat):
    r = model.generate_content(req.message)
    return {"reply": r.text}