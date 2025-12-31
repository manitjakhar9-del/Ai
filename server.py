from fastapi import FastAPI
from pydantic import BaseModel
import os
import psycopg2
from groq import Groq

app = FastAPI()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
db = psycopg2.connect(os.environ["DATABASE_URL"])
cur = db.cursor()

class Chat(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
def chat(req: Chat):

    # Load full memory from Neon
    cur.execute(
        "SELECT role, message FROM chats WHERE chat_id=%s ORDER BY created_at",
        (req.session_id,)
    )
    rows = cur.fetchall()

    messages = [
        {"role":"system","content":"You are Manit AI. You remember everything the user says."}
    ]

    for r, m in rows:
        messages.append({"role": r, "content": m})

    # Add new user message
    messages.append({"role":"user","content":req.message})

    # Call Groq with full history
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    reply = res.choices[0].message.content

    # Save both user and AI to Neon
    cur.execute(
        "INSERT INTO chats (chat_id, role, message) VALUES (%s, %s, %s)",
        (req.session_id, "user", req.message)
    )
    cur.execute(
        "INSERT INTO chats (chat_id, role, message) VALUES (%s, %s, %s)",
        (req.session_id, "assistant", reply)
    )
    db.commit()

    return {"reply": reply}
