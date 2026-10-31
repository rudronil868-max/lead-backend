import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS Middleware (Netlify থেকে ডাটা নেওয়ার অনুমতি)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

class LeadData(BaseModel):
    name: str
    email: str
    phone: str = ""
    interest: str = "General inquiry"
    message: str

@app.get("/")
def home():
    return {"status": "Lead Backend is Running!"}

@app.post("/api/submit")
def submit_lead(lead: LeadData):
    if not BOT_TOKEN or not CHAT_ID:
        raise HTTPException(status_code=500, detail="Telegram Bot Token or Chat ID missing!")

    telegram_message = (
        "🆕 **New Lead Received!**\n\n"
        f"👤 **Name:** {lead.name}\n"
        f"📧 **Email:** {lead.email}\n"
        f"📞 **Phone:** {lead.phone if lead.phone else 'N/A'}\n"
        f"🏷️ **Interest:** {lead.interest}\n\n"
        f"💬 **Message:**\n{lead.message}"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": telegram_message,
        "parse_mode": "Markdown"
    }

    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            return {"success": True, "message": "Lead sent to Telegram!"}
        else:
            raise HTTPException(status_code=400, detail="Telegram delivery failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
