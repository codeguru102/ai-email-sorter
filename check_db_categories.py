#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir('backend')

from app.db import get_db
from app.models import Category, User

def check_categories():
    db = next(get_db())
    
    try:
        # Get all users
        users = db.query(User).all()
        print("Users in database:")
        for user in users:
            print(f"  ID: {user.id}, Email: {user.email}")
        
        print("\nCategories in database:")
        categories = db.query(Category).all()
        for cat in categories:
            print(f"  ID: {cat.id}, Name: {cat.name}, User ID: {cat.user_id}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_categories()