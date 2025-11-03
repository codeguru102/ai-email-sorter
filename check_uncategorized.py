#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir('backend')

from app.db import get_db
from app.models import Email, User

def check_uncategorized():
    db = next(get_db())
    
    try:
        # Check user 6 (raymondli378@gmail.com)
        user = db.query(User).filter(User.id == 6).first()
        if not user:
            print("User 6 not found")
            return
            
        print(f"Checking emails for user: {user.email}")
        
        # Get all emails for this user
        all_emails = db.query(Email).filter(Email.user_id == user.id).all()
        print(f"Total emails: {len(all_emails)}")
        
        # Get uncategorized emails (category_id is None)
        uncategorized = db.query(Email).filter(
            Email.user_id == user.id,
            Email.category_id.is_(None)
        ).all()
        
        print(f"Uncategorized emails: {len(uncategorized)}")
        
        # Show categorization status
        categorized = db.query(Email).filter(
            Email.user_id == user.id,
            Email.category_id.isnot(None)
        ).all()
        
        print(f"Categorized emails: {len(categorized)}")
        
        # Show first few uncategorized
        if uncategorized:
            print("\nFirst 5 uncategorized emails:")
            for email in uncategorized[:5]:
                print(f"  - {email.subject or '(No Subject)'} from {email.sender_email}")
        else:
            print("\nNo uncategorized emails found")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_uncategorized()