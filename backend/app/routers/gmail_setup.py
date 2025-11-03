# app/routers/gmail_setup.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
import logging

from ..db import get_db
from ..services.gmail_webhook import setup_gmail_watch
from ..models import User
from ..security import verify_session_jwt

router = APIRouter(prefix="/gmail-setup", tags=["gmail-setup"])
logger = logging.getLogger("gmail_setup")

@router.post("/enable-notifications")
async def enable_notifications(request: Request, db: Session = Depends(get_db)):
    """Enable Gmail push notifications for the current user"""
    token = request.cookies.get("jwt_session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_data = verify_session_jwt(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    user = db.query(User).filter(User.sub == user_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    try:
        success = await setup_gmail_watch(user, db)
        
        if success:
            return {
                "status": "success", 
                "message": "Real-time email notifications enabled! New emails will be auto-fetched and categorized."
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to setup Gmail notifications")
            
    except Exception as e:
        logger.error("Setup notifications error: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")