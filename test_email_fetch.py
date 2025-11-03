#!/usr/bin/env python3
"""
Test email fetching functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from backend.app.db import get_db
from backend.app.models import User, GoogleAccount
from backend.app.services.email_service import fetch_and_store_emails, create_default_categories

async def test_email_fetch():
    print("Testing email fetch functionality...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Find a user with Google account
        user = db.query(User).join(GoogleAccount).first()
        
        if not user:
            print("No user with Google account found. Please login first.")
            return
        
        print(f"Testing with user: {user.email}")
        
        # Create categories if none exist
        existing_categories = db.query(Category).filter(Category.user_id == user.id).count()
        if existing_categories == 0:
            print("Creating default categories...")
            create_default_categories(user, db)
        
        # Fetch emails
        print("Fetching emails from Gmail...")
        email_count = await fetch_and_store_emails(user, db, max_emails=10)
        
        print(f"Successfully stored {email_count} emails")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Import Category here to avoid circular import
    from backend.app.models import Category
    asyncio.run(test_email_fetch())