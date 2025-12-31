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

    # Load history
    cur.execute(
        "SELECT role, content FROM chats WHERE session_id=%s ORDER BY id",
        (req.session_id,)
    )
    rows = cur.fetchall()

    messages = [{"role":"system","content":"You are Manit AI. You remember everything the user says."}]

    for r,c in rows:
        messages.append({"role":r,"content":c})

    messages.append({"role":"user","content":req.message})

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    reply = res.choices[0].message.content

    # Save both user + AI
    cur.execute("INSERT INTO chats (session_id, role, content) VALUES (%s,'user',%s)",
                (req.session_id, req.message))
    cur.execute("INSERT INTO chats (session_id, role, content) VALUES (%s,'assistant',%s)",
                (req.session_id, reply))
    db.commit()

    return {"reply": reply}
