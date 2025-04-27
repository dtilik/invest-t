#!/usr/bin/env python3
"""
API for the Tinkoff trading bot
Provides a simple FastAPI server to interact with the trading bot from a web UI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from bot import TradingBot

app = FastAPI(title="Trading Bot API", description="API for managing Tinkoff Invest trading bot")

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the trading bot
bot = TradingBot()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Trading Bot API is running"}

@app.get("/accounts")
def list_accounts():
    """List all available accounts"""
    accounts = bot.list_accounts()
    if accounts is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve accounts")
    return {"accounts": accounts}

@app.post("/accounts")
def create_account():
    """Create a new account"""
    account_id = bot.create_new_account()
    if account_id:
        return {"status": "created", "account_id": account_id}
    else:
        # In production mode, we can't create accounts directly
        return {
            "status": "info", 
            "message": "In production mode, accounts must be created through the Tinkoff website"
        }

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
