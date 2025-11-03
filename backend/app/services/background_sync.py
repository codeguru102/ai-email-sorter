# app/services/background_sync.py
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User, GoogleAccount
from .email_service import fetch_and_store_emails

logger = logging.getLogger("background_sync")

async def periodic_email_sync():
    """Periodically sync emails for all users (fallback if webhooks fail)"""
    while True:
        try:
            with next(get_db()) as db:
                # Get all users with Google accounts
                users = db.query(User).join(GoogleAccount).all()
                
                for user in users:
                    try:
                        new_emails = await fetch_and_store_emails(user, db, max_emails=5)
                        if new_emails > 0:
                            logger.info("Background sync: %d new emails for user %s", new_emails, user.id)
                    except Exception as e:
                        logger.error("Background sync failed for user %s: %s", user.id, str(e))
                
            # Wait 5 minutes before next sync
            await asyncio.sleep(300)
            
        except Exception as e:
            logger.error("Background sync error: %s", str(e))
            await asyncio.sleep(60)  # Wait 1 minute on error