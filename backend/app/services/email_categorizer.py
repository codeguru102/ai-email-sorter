# app/services/email_categorizer.py
import json
import logging
import openai
import httpx
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models import User, Email, Category
from ..db import get_settings

logger = logging.getLogger("email_categorizer")

class EmailCategorizerService:
    def __init__(self):
        self.client = self._get_openai_client()
    
    def _get_openai_client(self):
        """Get OpenAI client with proxy settings"""
        proxy_url = os.environ.get('HTTPS_PROXY', 'socks5://14ac63464dbca:b9e059af46@64.84.118.137:12324')
        
        return openai.OpenAI(
            api_key=get_settings().OPENAI_API_KEY,
            http_client=httpx.Client(proxy=proxy_url)
        )
    
    async def categorize_emails(self, db: Session, user: User, limit: int = 20) -> int:
        """Categorize uncategorized emails for a user"""
        
        # Get user's categories
        categories = db.query(Category).filter(Category.user_id == user.id).all()
        if not categories:
            logger.warning("No categories found for user %s", user.id)
            return 0
        
        # Get uncategorized emails
        uncategorized_emails = db.query(Email).filter(
            Email.user_id == user.id,
            Email.category_id.is_(None)
        ).limit(min(limit, 4)).all()
        
        if not uncategorized_emails:
            logger.info("No uncategorized emails found for user %s", user.id)
            return 0
        
        categorized_count = 0
        
        for email in uncategorized_emails:
            try:
                category_id = await self._categorize_single_email(email, categories)
                if category_id:
                    email.category_id = category_id
                    categorized_count += 1
            except Exception as e:
                logger.error("Error categorizing email %s: %s", email.id, str(e))
        
        db.commit()
        logger.info("Categorized %d emails for user %s", categorized_count, user.id)
        return categorized_count
    
    async def _categorize_single_email(self, email: Email, categories: List[Category]) -> Optional[int]:
        """Categorize a single email using OpenAI"""
        
        # Prepare categories for AI
        category_options = []
        for cat in categories:
            category_options.append({
                "id": cat.id,
                "name": cat.name,
                "description": cat.description
            })
        
        # Create prompt
        prompt = f"""
Categorize this email into one of the available categories.

Email Details:
- Subject: {email.subject}
- From: {email.sender} ({email.sender_email})
- Preview: {email.body_preview}

Available Categories:
{json.dumps(category_options, indent=2)}

Return only the category ID number that best fits this email. If none fit well, return null.
Consider:
- Work emails should go to Work category
- Personal emails from friends/family to Personal
- Marketing/promotional emails to Promotions
- Newsletter subscriptions to Newsletters
- Social media notifications to Social

Response format: Just the category ID number (e.g., 1) or null
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an email categorization assistant. Return only the category ID number or null."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse result
            if result.lower() == "null":
                return None
            
            try:
                category_id = int(result)
                # Verify category exists
                if any(cat.id == category_id for cat in categories):
                    return category_id
            except ValueError:
                pass
            
            logger.warning("Invalid categorization result: %s", result)
            return None
            
        except Exception as e:
            logger.error("OpenAI categorization failed: %s", str(e))
            return None

email_categorizer = EmailCategorizerService()