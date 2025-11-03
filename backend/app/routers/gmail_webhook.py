# app/routers/gmail_webhook.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
import logging
import json
from datetime import datetime

from ..db import get_db
from ..services.gmail_webhook import handle_gmail_notification, setup_gmail_watch
from ..models import User
from ..security import verify_session_jwt

router = APIRouter(prefix="/gmail", tags=["gmail"])
logger = logging.getLogger("gmail_webhook")

@router.post("/webhook")
async def gmail_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Gmail push notifications"""
    try:
        # Log all incoming requests
        headers = dict(request.headers)
        
        # Handle empty body or malformed JSON
        try:
            body = await request.body()
            if not body:
                logger.warning("Empty webhook body received")
                return {"status": "success", "message": "Empty body"}
            
            notification_data = json.loads(body.decode())
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in webhook: %s", str(e))
            return {"status": "error", "error": "Invalid JSON"}
        
        logger.info("=== GMAIL WEBHOOK RECEIVED ===")
        logger.info("Headers: %s", headers)
        logger.info("Body: %s", notification_data)
        
        await handle_gmail_notification(notification_data, db)
        
        logger.info("Webhook processed successfully")
        return {"status": "success", "received_at": str(datetime.now())}
        
    except Exception as e:
        logger.error("Webhook error: %s", str(e))
        return {"status": "error", "error": str(e)}

@router.get("/webhook-test")
async def webhook_test():
    """Test endpoint to verify webhook is reachable"""
    logger.info("Webhook test endpoint called")
    return {
        "status": "webhook_reachable", 
        "message": "Gmail webhook endpoint is working",
        "timestamp": str(datetime.now())
    }

@router.post("/setup-notifications")
async def setup_notifications(request: Request, db: Session = Depends(get_db)):
    """Set up Gmail push notifications for current user"""
    token = request.cookies.get("jwt_session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_data = verify_session_jwt(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    user = db.query(User).filter(User.sub == user_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    success = await setup_gmail_watch(user, db)
    
    if success:
        return {"status": "success", "message": "Gmail notifications enabled"}
    else:
        raise HTTPException(status_code=500, detail="Failed to setup notifications")