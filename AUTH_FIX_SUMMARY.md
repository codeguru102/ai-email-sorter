# Authentication Auto-Logout Fix

## Issues Identified

1. **Cookie Settings**: The backend was setting `httponly=True` which prevented the frontend from reading the session cookie
2. **Cross-Origin Cookie Issues**: Incorrect `samesite` and `secure` settings for localhost development
3. **Token Handling**: URL-encoded token in callback wasn't being properly decoded
4. **Error Handling**: Poor error handling in auth flow made debugging difficult

## Changes Made

### Backend Changes (`backend/app/routers/auth.py`)

1. **Fixed Cookie Settings**:
   - Changed `httponly=False` to allow frontend access
   - Set `samesite="lax"` for localhost development
   - Set `secure=False` for localhost development

2. **Enhanced Logging**:
   - Added detailed logging to `/auth/me` endpoint
   - Better error messages and debugging info

### Frontend Changes

1. **`frontend/src/lib/auth.ts`**:
   - Improved error handling in `getMe()` function
   - Added timeout in `createSessionFromToken()` for cookie setting
   - Better error logging

2. **`frontend/src/app/auth-callback/page.tsx`**:
   - Added proper URL decoding for the JWT token
   - Increased wait time for cookie setting
   - Better error handling and redirects

3. **`frontend/src/app/dashboard/page.tsx`**:
   - Improved authentication check flow
   - Better error handling and logging
   - Only load data after successful authentication

## Testing the Fix

### 1. Start Both Services
```bash
# Option 1: Use the batch script
start_dev.bat

# Option 2: Manual start
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 2. Test Authentication Flow
1. Go to http://localhost:3000
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Should redirect to dashboard and stay logged in

### 3. Debug if Issues Persist
```bash
# Test backend endpoints
cd main
python test_auth.py

# Check browser console for errors
# Check backend logs for detailed auth info
```

## Key Points

- **Cookies are now readable by frontend** (`httponly=False`)
- **Proper localhost settings** (`samesite=lax`, `secure=false`)
- **Better error handling** throughout the auth flow
- **Enhanced logging** for debugging

## Next Steps if Still Having Issues

1. Check browser developer tools → Application → Cookies
2. Verify session cookie is being set with correct domain/path
3. Check backend logs for detailed auth flow information
4. Test with different browsers or incognito mode

The main issue was that the session cookie was set as `httponly=true` which prevented the frontend JavaScript from accessing it, causing the authentication state to not persist properly.