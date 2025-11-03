# app/services/gmail_webhook.py
import json
import base64
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from ..models import User, GoogleAccount
from .email_service import fetch_and_store_emails

logger = logging.getLogger("gmail_webhook")

async def setup_gmail_watch(user: User, db: Session) -> bool:
    """Set up Gmail push notifications for a user"""
    import requests
    from ..routers.gmail_calendar import refresh_google_token, _auth_headers
    
    google_account = db.query(GoogleAccount).filter(GoogleAccount.user_id == user.id).first()
    if not google_account:
        return False
    
    try:
        access_token = await refresh_google_token(google_account, db)
        headers = _auth_headers(access_token)
        
        # Set up Gmail watch
        watch_url = "https://gmail.googleapis.com/gmail/v1/users/me/watch"
        watch_data = {
            "topicName": "projects/forward-bucksaw-412320/topics/gmail-inbox",
            "labelIds": ["INBOX"]
        }
        
        response = requests.post(watch_url, headers=headers, json=watch_data, timeout=30)
        
        if response.status_code == 200:
            logger.info("Gmail watch setup successful for user %s", user.id)
            return True
        else:
            logger.error("Gmail watch setup failed: %s", response.text)
            return False
            
    except Exception as e:
        logger.error("Error setting up Gmail watch: %s", str(e))
        return False

async def handle_gmail_notification(notification_data: Dict[str, Any], db: Session):
    """Handle incoming Gmail push notification"""
    try:
        # Decode the Pub/Sub message
        message = notification_data.get("message", {})
        data = message.get("data", "")
        
        if data:
            decoded_data = json.loads(base64.b64decode(data).decode())
            email_address = decoded_data.get("emailAddress")
            history_id = decoded_data.get("historyId")
            
            logger.info("Gmail notification: %s, historyId: %s", email_address, history_id)
            
            if email_address:
                # Find user by email
                user = db.query(User).filter(User.email == email_address).first()
                if user:
                    # Fetch and categorize new emails
                    new_emails = await fetch_and_store_emails(user, db, max_emails=5)
                    logger.info("Auto-fetched %d new emails for %s", new_emails, email_address)
                    
                    # Log titles of newly received emails
                    await log_new_email_titles(user, db)
                else:
                    logger.warning("User not found for email: %s", email_address)
                    
    except Exception as e:
        logger.error("Error handling Gmail notification: %s", str(e))

async def log_new_email_titles(user: User, db: Session):
    """Log titles of the most recent emails for the user"""
    try:
        from ..models import Email
        from datetime import datetime, timedelta
        
        # Get emails from the last 5 minutes (recently fetched)
        recent_time = datetime.utcnow() - timedelta(minutes=5)
        recent_emails = db.query(Email).filter(
            Email.user_id == user.id,
            Email.received_at >= recent_time
        ).order_by(Email.received_at.desc()).limit(10).all()
        
        if recent_emails:
            logger.info("=== NEW EMAIL TITLES RECEIVED ===")
            for email in recent_emails:
                logger.info("📧 Email Title: %s (From: %s)", email.subject or "(No Subject)", email.sender_email)
            logger.info("=== END EMAIL TITLES ===")
            
            # Also print to console for immediate visibility
            print("\n=== NEW GMAIL RECEIVED ===")
            for email in recent_emails:
                print(f"📧 {email.subject or '(No Subject)'} - From: {email.sender_email}")
            print("=== END GMAIL TITLES ===\n")
        
    except Exception as e:
        logger.error("Error logging email titles: %s", str(e))