# app/services/email_service.py
import requests
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models import User, GoogleAccount, Email, Category
from ..routers.gmail_calendar import refresh_google_token, _auth_headers

logger = logging.getLogger("email_service")

async def fetch_and_store_emails(user: User, db: Session, max_emails: int = 50) -> int:
    """Fetch emails from Gmail and store in database"""
    
    google_account = db.query(GoogleAccount).filter(GoogleAccount.user_id == user.id).first()
    if not google_account:
        logger.warning("No Google account found for user %s", user.id)
        return 0

    try:
        access_token = await refresh_google_token(google_account, db)
        headers = _auth_headers(access_token)

        # Get messages list
        messages_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        params = {"maxResults": max_emails}
        response = requests.get(messages_url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            logger.error("Failed to fetch messages: %s", response.text)
            return 0

        messages_data = response.json()
        stored_count = 0

        for msg in messages_data.get("messages", []):
            gmail_id = msg["id"]
            
            # Check if email already exists
            existing = db.query(Email).filter(Email.gmail_id == gmail_id).first()
            if existing:
                continue

            # Fetch full message details
            message_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{gmail_id}"
            msg_response = requests.get(message_url, headers=headers, params={"format": "full"}, timeout=30)
            
            if msg_response.status_code != 200:
                continue

            msg_data = msg_response.json()
            
            # Parse email data
            email_data = _parse_email_data(msg_data, user.id)
            if email_data:
                email = Email(**email_data)
                db.add(email)
                stored_count += 1
                
                # Log email title immediately when stored
                logger.info("📧 New Email Stored: '%s' from %s", 
                           email_data.get('subject', '(No Subject)'), 
                           email_data.get('sender_email', 'Unknown'))
                print(f"📧 NEW EMAIL: {email_data.get('subject', '(No Subject)')} - From: {email_data.get('sender_email', 'Unknown')}")

        db.commit()
        logger.info("Stored %d new emails for user %s", stored_count, user.id)
        
        # Print summary of new emails
        if stored_count > 0:
            print(f"\n✅ Successfully stored {stored_count} new emails for user {user.id}")
        
        # Auto-categorize new emails
        if stored_count > 0:
            try:
                from .email_categorizer import EmailCategorizerService
                email_categorizer = EmailCategorizerService()
                categorized = await email_categorizer.categorize_emails(db, user, limit=min(stored_count, 4))
                logger.info("Auto-categorized %d emails for user %s", categorized, user.id)
                print(f"🏷️  Auto-categorized {categorized} emails")
            except Exception as e:
                logger.error("Auto-categorization failed: %s", str(e))
        
        return stored_count

    except Exception as e:
        logger.error("Error fetching emails for user %s: %s", user.id, str(e))
        db.rollback()
        return 0

def _parse_email_data(msg_data: Dict[str, Any], user_id: int) -> Optional[Dict[str, Any]]:
    """Parse Gmail message data into Email model format"""
    
    try:
        # Extract headers
        headers_map = {}
        payload = msg_data.get("payload", {})
        for h in payload.get("headers", []):
            name = h.get("name")
            value = h.get("value")
            if name and value is not None:
                headers_map[name] = value

        # Parse received date
        internal_date = msg_data.get("internalDate")
        if internal_date:
            received_at = datetime.fromtimestamp(int(internal_date) / 1000, tz=timezone.utc)
        else:
            received_at = datetime.now(timezone.utc)

        # Extract sender info
        from_header = headers_map.get("From", "")
        sender_email = ""
        sender_name = from_header
        
        if "<" in from_header and ">" in from_header:
            sender_name = from_header.split("<")[0].strip().strip('"')
            sender_email = from_header.split("<")[1].split(">")[0].strip()
        elif "@" in from_header:
            sender_email = from_header.strip()
            sender_name = sender_email

        return {
            "user_id": user_id,
            "gmail_id": msg_data.get("id"),
            "thread_id": msg_data.get("threadId", ""),
            "subject": headers_map.get("Subject", ""),
            "sender": sender_name,
            "sender_email": sender_email,
            "recipient": headers_map.get("To", ""),
            "body_preview": msg_data.get("snippet", ""),
            "received_at": received_at,
            "labels": msg_data.get("labelIds", []),
            "is_read": "UNREAD" not in msg_data.get("labelIds", []),
            "is_important": "IMPORTANT" in msg_data.get("labelIds", []),
        }

    except Exception as e:
        logger.error("Error parsing email data: %s", str(e))
        return None

def create_default_categories(user: User, db: Session) -> List[Category]:
    """Create default email categories for new user"""
    
    default_categories = [
        {"name": "Work", "description": "Work-related emails and projects"},
        {"name": "Personal", "description": "Personal emails from friends and family"},
        {"name": "Newsletters", "description": "Newsletters and subscription emails"},
        {"name": "Promotions", "description": "Marketing and promotional emails"},
        {"name": "Social", "description": "Social media notifications"},
    ]
    
    categories = []
    for cat_data in default_categories:
        category = Category(
            user_id=user.id,
            name=cat_data["name"],
            description=cat_data["description"]
        )
        db.add(category)
        categories.append(category)
    
    db.commit()
    logger.info("Created %d default categories for user %s", len(categories), user.id)
    return categories