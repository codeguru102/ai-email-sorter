# app/routers/emails.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..db import get_db
from ..models import User, Email, Category, EmailOut, CategoryOut
from pydantic import BaseModel
from ..security import verify_session_jwt

router = APIRouter(prefix="/emails", tags=["emails"])
logger = logging.getLogger("emails")

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current user from session cookie"""
    token = request.cookies.get("jwt_session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_data = verify_session_jwt(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    user = db.query(User).filter(User.sub == user_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@router.get("/categories", response_model=List[CategoryOut])
async def get_categories(request: Request, db: Session = Depends(get_db)):
    """Get user's email categories"""
    user = await get_current_user(request, db)
    
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    
    result = []
    for category in categories:
        email_count = db.query(Email).filter(Email.category_id == category.id).count()
        result.append(CategoryOut(
            id=category.id,
            name=category.name,
            description=category.description,
            email_count=email_count,
            created_at=category.created_at
        ))
    
    return result

@router.get("/", response_model=List[EmailOut])
async def get_emails(
    request: Request,
    category_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's emails, optionally filtered by category"""
    user = await get_current_user(request, db)
    
    query = db.query(Email).filter(Email.user_id == user.id)
    
    if category_id:
        query = query.filter(Email.category_id == category_id)
    
    emails = query.order_by(Email.received_at.desc()).limit(limit).all()
    
    return [EmailOut(
        id=email.id,
        gmail_id=email.gmail_id,
        subject=email.subject,
        sender=email.sender,
        sender_email=email.sender_email,
        body_preview=email.body_preview,
        received_at=email.received_at,
        is_read=email.is_read,
        category_id=email.category_id
    ) for email in emails]

@router.get("/uncategorized", response_model=List[EmailOut])
async def get_uncategorized_emails(
    request: Request,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get uncategorized emails"""
    user = await get_current_user(request, db)
    
    logger.info("Fetching uncategorized emails for user %d", user.id)
    
    emails = db.query(Email).filter(
        Email.user_id == user.id,
        Email.category_id.is_(None)
    ).order_by(Email.received_at.desc()).limit(limit).all()
    
    logger.info("Found %d uncategorized emails for user %d", len(emails), user.id)
    
    return [EmailOut(
        id=email.id,
        gmail_id=email.gmail_id,
        subject=email.subject,
        sender=email.sender,
        sender_email=email.sender_email,
        body_preview=email.body_preview,
        received_at=email.received_at,
        is_read=email.is_read,
        category_id=email.category_id
    ) for email in emails]

@router.get("/category/{category_id}", response_model=List[EmailOut])
async def get_emails_by_category(
    category_id: int,
    request: Request,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get emails in a specific category"""
    user = await get_current_user(request, db)
    
    # Verify category belongs to user
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user.id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    emails = db.query(Email).filter(
        Email.user_id == user.id,
        Email.category_id == category_id
    ).order_by(Email.received_at.desc()).limit(limit).all()
    
    return [EmailOut(
        id=email.id,
        gmail_id=email.gmail_id,
        subject=email.subject,
        sender=email.sender,
        sender_email=email.sender_email,
        body_preview=email.body_preview,
        received_at=email.received_at,
        is_read=email.is_read,
        category_id=email.category_id
    ) for email in emails]

@router.post("/sync")
async def sync_emails(request: Request, db: Session = Depends(get_db)):
    """Manually sync emails from Gmail"""
    user = await get_current_user(request, db)
    
    try:
        from ..services.email_service import fetch_and_store_emails
        email_count = await fetch_and_store_emails(user, db, max_emails=100)
        
        return {
            "status": "success",
            "emails_synced": email_count,
            "message": f"Synced {email_count} new emails"
        }
    except Exception as e:
        logger.error("Email sync failed for user %s: %s", user.id, str(e))
        raise HTTPException(status_code=500, detail="Email sync failed")

@router.post("/add-account")
async def add_gmail_account(request: Request, db: Session = Depends(get_db)):
    """Add additional Gmail account for email syncing"""
    user = await get_current_user(request, db)
    
    try:
        # For now, just sync more emails from the current account
        # In a full implementation, this would handle multiple OAuth tokens
        from ..services.email_service import fetch_and_store_emails
        email_count = await fetch_and_store_emails(user, db, max_emails=200)
        
        return {
            "status": "success",
            "emails_synced": email_count,
            "message": f"Added account and synced {email_count} emails"
        }
    except Exception as e:
        logger.error("Add account failed for user %s: %s", user.id, str(e))
        raise HTTPException(status_code=500, detail="Failed to add account")

class CategoryCreate(BaseModel):
    name: str
    description: str

@router.post("/categories", response_model=CategoryOut)
async def create_category(category_data: CategoryCreate, request: Request, db: Session = Depends(get_db)):
    """Create a new email category"""
    user = await get_current_user(request, db)
    
    # Create new category
    new_category = Category(
        user_id=user.id,
        name=category_data.name,
        description=category_data.description
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    # Return the created category with email count (0 for new category)
    return CategoryOut(
        id=new_category.id,
        name=new_category.name,
        description=new_category.description,
        email_count=0,
        created_at=new_category.created_at
    )

@router.delete("/categories/{category_id}")
async def delete_category(category_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete an email category"""
    user = await get_current_user(request, db)
    
    logger.info("Delete request: category_id=%d, user_id=%d", category_id, user.id)
    
    # Find the category and verify it belongs to the user
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user.id
    ).first()
    
    if not category:
        # Debug: check if category exists for any user
        any_category = db.query(Category).filter(Category.id == category_id).first()
        if any_category:
            logger.warning("Category %d exists but belongs to user %d, not %d", category_id, any_category.user_id, user.id)
        else:
            logger.warning("Category %d does not exist at all", category_id)
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if there are emails in this category
    email_count = db.query(Email).filter(Email.category_id == category_id).count()
    
    if email_count > 0:
        # Option 1: Move emails to uncategorized (set category_id to None)
        db.query(Email).filter(Email.category_id == category_id).update({"category_id": None})
        logger.info("Moved %d emails to uncategorized before deleting category %s", email_count, category.name)
    
    # Delete the category
    db.delete(category)
    db.commit()
    
    logger.info("Deleted category '%s' (ID: %d) for user %s", category.name, category_id, user.id)
    
    return {
        "status": "success",
        "message": f"Category '{category.name}' deleted successfully",
        "emails_moved": email_count
    }

@router.post("/categorize")
async def categorize_emails(request: Request, db: Session = Depends(get_db)):
    """Manually categorize uncategorized emails using AI"""
    user = await get_current_user(request, db)
    
    try:
        from ..services.email_categorizer import EmailCategorizerService
        email_categorizer = EmailCategorizerService()
        categorized_count = await email_categorizer.categorize_emails(db, user, limit=3)
        
        return {
            "status": "success",
            "emails_categorized": categorized_count,
            "message": f"Categorized {categorized_count} emails using AI"
        }
    except Exception as e:
        logger.error("Email categorization failed for user %s: %s", user.id, str(e))
        raise HTTPException(status_code=500, detail="Email categorization failed")