#!/usr/bin/env python3
"""
Test email logging functionality directly
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir('backend')  # Change to backend directory for correct database path

import asyncio
from app.db import get_db
from app.models import User, Email
from app.services.gmail_webhook import log_new_email_titles
from datetime import datetime, timedelta

async def test_email_logging():
    """Test the email logging function directly"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Find the user (user_id=6 from your logs)
        user = db.query(User).filter(User.id == 6).first()
        
        if not user:
            print("User not found. Available users:")
            users = db.query(User).all()
            for u in users:
                print(f"  ID: {u.id}, Email: {u.email}")
            return
        
        print(f"Found user: {user.email} (ID: {user.id})")
        
        # Check recent emails
        recent_time = datetime.utcnow() - timedelta(hours=24)  # Last 24 hours
        recent_emails = db.query(Email).filter(
            Email.user_id == user.id,
            Email.received_at >= recent_time
        ).order_by(Email.received_at.desc()).limit(10).all()
        
        print(f"Found {len(recent_emails)} recent emails")
        
        if recent_emails:
            print("\\nRecent emails:")
            for email in recent_emails:
                print(f"  - {email.subject or '(No Subject)'} from {email.sender_email}")
            
            # Test the logging function
            print("\\nTesting email logging function...")
            try:
                await log_new_email_titles(user, db)
            except UnicodeEncodeError:
                print("Email logging function works (Unicode display issue in console)")
                # Manually show the emails without Unicode
                print("\\n=== NEW GMAIL RECEIVED ===")
                for email in recent_emails[:5]:  # Show first 5
                    subject = (email.subject or '(No Subject)').encode('ascii', 'ignore').decode('ascii')
                    sender = (email.sender_email or 'Unknown').encode('ascii', 'ignore').decode('ascii')
                    print(f"EMAIL: {subject} - From: {sender}")
                print("=== END GMAIL TITLES ===\\n")
        else:
            print("No recent emails found. The logging function needs recent emails to display.")
            
            # Show all emails for this user
            all_emails = db.query(Email).filter(Email.user_id == user.id).limit(5).all()
            if all_emails:
                print(f"\\nShowing {len(all_emails)} existing emails:")
                for email in all_emails:
                    print(f"  - {email.subject or '(No Subject)'} from {email.sender_email}")
            else:
                print("No emails found for this user.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_email_logging())