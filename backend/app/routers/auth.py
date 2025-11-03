# app/routers/auth.py
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from authlib.integrations.base_client.errors import MismatchingStateError
import logging, json
from urllib.parse import urlparse, parse_qs, urlencode
from typing import Optional

from ..db import get_db
from ..oauth import get_oauth
from ..models import User, GoogleAccount, Category
from ..security import make_session_jwt, verify_session_jwt
from ..db import get_settings as get_app_settings

router = APIRouter(prefix="/auth", tags=["auth"])
SESSION_COOKIE = "jwt_session"  # Use different name to avoid conflict with SessionMiddleware

# ---------- logger ----------
logger = logging.getLogger("auth")
if not logger.handlers:
    h = logging.StreamHandler()
    f = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    h.setFormatter(f)
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# ---------- WORKING SOLUTION: Pass token via URL parameter ----------
@router.get("/google/login")
async def google_login(request: Request):
    oauth = get_oauth()
    redirect_uri = build_callback_url(request)
    
    logger.info("GOOGLE_LOGIN_START: redirect_uri=%s", redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri, access_type="offline", prompt="consent", include_granted_scopes="true")

def build_callback_url(request: Request) -> str:
    url = request.url_for("google_callback")
    if url.scheme not in ("http", "https"):
        url = url.replace(scheme="http")
    return str(url)

@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Google OAuth callback - WORKING VERSION that passes token to frontend
    """
    oauth = get_oauth()
    
    logger.info("=== GOOGLE CALLBACK STARTED ===")

    try:
        token = await oauth.google.authorize_access_token(request)
        print("Token: ", token)
        if not token:
            raise HTTPException(status_code=400, detail="No token received")
            
    except Exception as e:
        logger.error("GOOGLE_AUTH_FAILED: %s", str(e))
        raise HTTPException(status_code=400, detail="Authentication failed")

    # Get user info
    userinfo = token.get("userinfo")
    if not userinfo:
        try:
            resp = await oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo", token=token)
            userinfo = resp.json()
        except Exception as e:
            logger.error("USERINFO_FAILED: %s", str(e))
            raise HTTPException(status_code=400, detail="Failed to get user info")

    sub = userinfo.get("sub")
    email = userinfo.get("email", "")
    name = userinfo.get("name", "")
    picture = userinfo.get("picture", "")

    if not sub:
        raise HTTPException(status_code=400, detail="Invalid user info")

    # Create/update user in database
    try:
        user = db.query(User).filter(User.sub == sub).one_or_none()
        if not user:
            user = User(sub=sub, email=email, name=name, picture=picture)
            db.add(user)
            db.flush()
            logger.info("USER_CREATED: id=%s, email=%s", user.id, email)
        else:
            user.email = email
            user.name = name
            user.picture = picture
            logger.info("USER_UPDATED: id=%s, email=%s", user.id, email)

        # Update Google account
        ga = db.query(GoogleAccount).filter(GoogleAccount.user_id == user.id).one_or_none()
        if not ga:
            ga = GoogleAccount(
                user_id=user.id,
                access_token=token["access_token"],
                refresh_token=token.get("refresh_token", ""),
                token_type=token.get("token_type", "Bearer"),
                expires_at=token.get("expires_at"),
                scope=token.get("scope", ""),
                raw_token=json.dumps(token) if isinstance(token, dict) else str(token),
            )
            db.add(ga)
        else:
            ga.access_token = token["access_token"]
            if token.get("refresh_token"):
                ga.refresh_token = token["refresh_token"]

        print("!!!!!!!!!!!!!!!!!!=> refresh token: ", ga.refresh_token)
        db.commit()
        logger.info("DATABASE_SAVED: user_id=%s", user.id)
        
        # Auto-fetch emails and create categories for new users
        try:
            from ..services.email_service import fetch_and_store_emails, create_default_categories
            
            # Create default categories if user is new
            existing_categories = db.query(Category).filter(Category.user_id == user.id).count()
            if existing_categories == 0:
                create_default_categories(user, db)
            
            # Fetch and store recent emails
            email_count = await fetch_and_store_emails(user, db, max_emails=50)
            logger.info("AUTO_FETCH: Stored %d emails for user %s", email_count, user.id)
            
        except Exception as e:
            logger.error("AUTO_FETCH_ERROR: %s", str(e))

    except Exception as e:
        db.rollback()
        logger.error("DATABASE_ERROR: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to save user data")

    # === WORKING SOLUTION: Pass JWT token to frontend via URL parameter ===
    frontend = get_app_settings().CORS_ORIGINS.split(",")[0].strip()
    jwt_token = make_session_jwt(sub=user.sub, email=user.email, name=user.name, picture=user.picture)
    
    # URL encode the token
    import urllib.parse
    encoded_token = urllib.parse.quote(jwt_token)
    
    # Redirect to frontend with token as URL parameter
    redirect_url = f"{frontend}/auth-callback?token={encoded_token}&user_id={user.id}"
    
    logger.info("REDIRECTING_WITH_TOKEN: frontend=%s, token_length=%s", frontend, len(jwt_token))
    logger.info("JWT_TOKEN_PREVIEW: %s", jwt_token[:50] + "...")
    
    resp = RedirectResponse(url=redirect_url, status_code=302)
    
    # Clear any existing session cookie and set the new JWT token
    resp.delete_cookie(SESSION_COOKIE, path="/")
    resp.set_cookie(
        key=SESSION_COOKIE,
        value=jwt_token,  # Set the actual JWT token, not OAuth state
        httponly=False,
        samesite="lax",
        secure=False,
        path="/",
        max_age=60 * 60 * 24 * 30,
    )
    
    logger.info("JWT_COOKIE_SET: token_preview=%s", jwt_token[:50] + "...")
    
    return resp

def _set_session_cookie(resp: RedirectResponse, value: str, frontend_origin: str, request: Request):
    """Set session cookie with proper cross-domain settings"""
    frontend_parsed = urlparse(frontend_origin)
    is_production = frontend_parsed.hostname not in ["localhost", "127.0.0.1"]
    
    cookie_options = {
        "key": SESSION_COOKIE,
        "value": value,
        "httponly": False,  # Allow frontend to read cookie
        "samesite": "lax",  # Use lax for localhost development
        "secure": False,  # False for localhost development
        "path": "/",
        "max_age": 60 * 60 * 24 * 30,
    }
    
    resp.set_cookie(**cookie_options)

@router.post("/session")
async def create_session(request: Request, db: Session = Depends(get_db)):
    """
    Create session from JWT token and return user details
    """
    try:
        data = await request.json()
        token = data.get('token')
        
        if not token:
            raise HTTPException(status_code=400, detail="No token provided")
        
        # Verify the token
        user_data = verify_session_jwt(token)
        if not user_data:
            raise HTTPException(status_code=400, detail="Invalid token")
        
        # Get user from database to ensure they exist and get latest data
        user = db.query(User).filter(User.sub == user_data["sub"]).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Check if user has Google account connected
        has_google = db.query(GoogleAccount).filter(GoogleAccount.user_id == user.id).first() is not None
        
        # Prepare user response data
        user_response = {
            "authenticated": True,
            "user": {
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "sub": user.sub
            },
            "google_connected": has_google
        }
        
        # Set session cookie
        resp = JSONResponse({
            "status": "success",
            "user": user_response
        })
        
        # Detect if production based on request origin
        origin = request.headers.get("origin", "")
        is_production = "localhost" not in origin and "127.0.0.1" not in origin
        
        resp.set_cookie(
            key=SESSION_COOKIE,
            value=token,
            httponly=False,  # Allow frontend to read cookie
            samesite="lax",  # Use lax for localhost
            secure=False,  # False for localhost development
            path="/",
            max_age=60 * 60 * 24 * 30,
        )
        
        logger.info("SESSION_CREATED_FROM_TOKEN: user_id=%s, email=%s", user.id, user.email)
        return resp
        
    except Exception as e:
        logger.error("SESSION_CREATION_FAILED: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to create session")
        
@router.get("/me")
def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    """
    Check if user is authenticated
    """
    token = request.cookies.get(SESSION_COOKIE)
    all_cookies = dict(request.cookies)
    
    logger.info("/ME_CALLED: has_session_cookie=%s, all_cookies=%s", bool(token), all_cookies)
    logger.info("/ME_CALLED: token_preview=%s", token[:50] + "..." if token else "None")
    
    if not token:
        logger.info("/ME_RESULT: No session cookie found")
        return JSONResponse(
            {"authenticated": False, "reason": "no_session_cookie"}, 
            status_code=200
        )

    data = verify_session_jwt(token)
    if not data:
        logger.info("/ME_RESULT: Invalid JWT token")
        return JSONResponse(
            {"authenticated": False, "reason": "invalid_jwt"}, 
            status_code=200
        )

    logger.info("/ME_JWT_DATA: %s", {k: v for k, v in data.items() if k != 'exp'})

    user = db.query(User).filter(User.sub == data["sub"]).one_or_none()
    if not user:
        logger.info("/ME_RESULT: User not found in database for sub=%s", data["sub"])
        return JSONResponse(
            {"authenticated": False, "reason": "user_not_found"}, 
            status_code=200
        )

    has_google = db.query(GoogleAccount).filter(GoogleAccount.user_id == user.id).first() is not None

    logger.info("/ME_RESULT: Authentication successful for user_id=%s, email=%s", user.id, user.email)
    
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "email": user.email, 
            "name": user.name, 
            "picture": user.picture, 
            "sub": user.sub,
        },
        "google_connected": has_google,
    }

@router.post("/logout")
def logout():
    """
    Logout user
    """
    frontend = get_app_settings().CORS_ORIGINS.split(",")[0].strip()
    resp = JSONResponse({"status": "logged_out"})
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp

# Debug endpoints
@router.get("/debug/cookies")
def debug_cookies(request: Request):
    return {
        "cookies": dict(request.cookies),
        "session_cookie": request.cookies.get(SESSION_COOKIE),
        "headers": dict(request.headers)
    }

@router.get("/debug/create-test-session")
def create_test_session(request: Request):
    """Manually create a test session"""
    test_jwt = make_session_jwt(
        sub="test-sub-123",
        email="test@example.com", 
        name="Test User", 
        picture=""
    )
    
    resp = JSONResponse({"status": "test_session_created", "token_preview": test_jwt[:50] + "..."})
    resp.set_cookie(
        key=SESSION_COOKIE,
        value=test_jwt,
        httponly=False,
        samesite="lax",
        secure=False,
        path="/",
        max_age=60 * 60 * 24 * 30,
    )
    return resp

@router.get("/debug/clear-cookies")
def clear_cookies():
    """Clear all session cookies"""
    resp = JSONResponse({"status": "cookies_cleared"})
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp

@router.get("/debug/verify-jwt/{token}")
def verify_jwt_debug(token: str):
    """Debug JWT verification"""
    try:
        decoded = verify_session_jwt(token)
        return {"valid": True, "decoded": decoded}
    except Exception as e:
        return {"valid": False, "error": str(e)}