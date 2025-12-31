from fastapi import FastAPI
from pydantic import BaseModel
import os
import psycopg2
from groq import Groq

app = FastAPI()

# ---- Groq Client ----
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ---- Neon DB Connection ----
db = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = db.cursor()

# ---- Request Model ----
class Chat(BaseModel):
    session_id: str
    message: str

# ---- Chat Endpoint ----
@app.post("/chat")
def chat(req: Chat):

    # Load full memory from Neon
    cur.execute(
        "SELECT role, message FROM chats WHERE chat_id=%s ORDER BY created_at ASC",
        (req.session_id,)
    )
    rows = cur.fetchall()

    messages = [
        {
            "role": "system",
            "content": "You are Manit AI. You remember everything the user says. If the user asks about a past number or fact, you must recall it."
        }
    ]

    # Load old messages
    for role, msg in rows:
        messages.append({"role": role, "content": msg})

    # Add new user message
    messages.append({"role": "user", "content": req.message})

    # Call Groq (WORKING MODEL)
    res = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=messages,
        temperature=0.7
    )

    reply = res.choices[0].message.content

    # Save user message
    cur.execute(
        "INSERT INTO chats (chat_id, role, message) VALUES (%s, %s, %s)",
        (req.session_id, "user", req.message)
    )

    # Save AI reply
    cur.execute(
        "INSERT INTO chats (chat_id, role, message) VALUES (%s, %s, %s)",
        (req.session_id, "assistant", reply)
    )

    db.commit()

    return {"reply": reply}
