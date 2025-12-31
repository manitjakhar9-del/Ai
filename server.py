from fastapi import FastAPI
from pydantic import BaseModel
import os
import psycopg2
from groq import Groq

app = FastAPI()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id SERIAL PRIMARY KEY,
    session_id TEXT,
    role TEXT,
    content TEXT
)
""")
conn.commit()

class Chat(BaseModel):
    session_id: str
    message: str

@app.get("/")
def root():
    return {"status": "Manit AI running with memory"}

@app.post("/chat")
def chat(req: Chat):
    cur.execute(
        "SELECT role, content FROM chats WHERE session_id=%s ORDER BY id",
        (req.session_id,)
    )
    history = cur.fetchall()

    messages = [{"role": r, "content": c} for r,c in history]
    messages.append({"role":"user","content":req.message})

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    reply = completion.choices[0].message.content

    cur.execute("INSERT INTO chats VALUES (DEFAULT,%s,%s,%s)",
        (req.session_id,"user",req.message))
    cur.execute("INSERT INTO chats VALUES (DEFAULT,%s,%s,%s)",
        (req.session_id,"assistant",reply))
    conn.commit()

    return {"reply": reply}
