# app/routers/webhook_logs.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime
import json

from ..db import get_db

router = APIRouter(prefix="/webhook-logs", tags=["webhook-logs"])

# Store recent webhook calls in memory (for testing)
recent_webhooks = []

@router.get("/recent")
async def get_recent_webhooks():
    """Get recent webhook calls for debugging"""
    return {"webhooks": recent_webhooks[-10:]}  # Last 10 calls

@router.post("/log")
async def log_webhook_call(request: Request):
    """Log webhook call for debugging"""
    try:
        body = await request.json()
        webhook_log = {
            "timestamp": str(datetime.now()),
            "headers": dict(request.headers),
            "body": body,
            "method": request.method,
            "url": str(request.url)
        }
        
        recent_webhooks.append(webhook_log)
        
        # Keep only last 50 entries
        if len(recent_webhooks) > 50:
            recent_webhooks.pop(0)
            
        return {"status": "logged", "count": len(recent_webhooks)}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}