#!/usr/bin/env python3
"""
Test email categorization functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from backend.app.db import get_db
from backend.app.models import User, Email, Category
from backend.app.services.email_categorizer import email_categorizer

async def test_categorization():
    print("Testing email categorization...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Find a user with emails
        user = db.query(User).join(Email).first()
        
        if not user:
            print("No user with emails found. Please sync emails first.")
            return
        
        print(f"Testing with user: {user.email}")
        
        # Check categories
        categories = db.query(Category).filter(Category.user_id == user.id).all()
        print(f"Available categories: {[cat.name for cat in categories]}")
        
        # Check uncategorized emails
        uncategorized = db.query(Email).filter(
            Email.user_id == user.id,
            Email.category_id.is_(None)
        ).count()
        
        print(f"Uncategorized emails: {uncategorized}")
        
        if uncategorized > 0:
            # Test categorization
            print("Running AI categorization...")
            categorized_count = await email_categorizer.categorize_emails(db, user, limit=5)
            print(f"Successfully categorized {categorized_count} emails")
            
            # Show results
            categorized_emails = db.query(Email).filter(
                Email.user_id == user.id,
                Email.category_id.isnot(None)
            ).limit(5).all()
            
            for email in categorized_emails:
                category = db.query(Category).filter(Category.id == email.category_id).first()
                print(f"- '{email.subject}' -> {category.name if category else 'Unknown'}")
        else:
            print("No uncategorized emails to test with")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_categorization())