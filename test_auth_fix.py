#!/usr/bin/env python3
"""
Test script to verify authentication and cookie handling
"""
import requests
import json

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("🧪 Testing Authentication Endpoints")
    print("=" * 50)
    
    # Test 1: Check /auth/me without authentication
    print("\n1. Testing /auth/me without authentication...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/auth/me")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check debug endpoints
    print("\n2. Testing debug endpoints...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/auth/debug/cookies")
        print(f"   Debug cookies status: {response.status_code}")
        print(f"   Debug response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Create test session
    print("\n3. Creating test session...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/auth/debug/create-test-session")
        print(f"   Test session status: {response.status_code}")
        print(f"   Test session response: {response.json()}")
        
        # Extract cookie from response
        cookies = response.cookies
        print(f"   Cookies received: {dict(cookies)}")
        
        # Test 4: Use the test session
        if cookies:
            print("\n4. Testing with session cookie...")
            me_response = requests.get(f"{BACKEND_URL}/api/auth/me", cookies=cookies)
            print(f"   Auth check status: {me_response.status_code}")
            print(f"   Auth check response: {me_response.json()}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Test CORS headers
    print("\n5. Testing CORS configuration...")
    try:
        response = requests.options(
            f"{BACKEND_URL}/api/auth/me",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        print(f"   CORS preflight status: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   Error: {e}")

def test_cookie_settings():
    """Test cookie configuration"""
    print("\n🍪 Testing Cookie Configuration")
    print("=" * 50)
    
    try:
        # Create a test session and examine cookie attributes
        response = requests.get(f"{BACKEND_URL}/api/auth/debug/create-test-session")
        
        if response.cookies:
            for cookie in response.cookies:
                print(f"\nCookie: {cookie.name}")
                print(f"  Value: {cookie.value[:50]}...")
                print(f"  Domain: {cookie.domain}")
                print(f"  Path: {cookie.path}")
                print(f"  Secure: {cookie.secure}")
                print(f"  HttpOnly: {cookie.has_nonstandard_attr('HttpOnly')}")
                print(f"  SameSite: {cookie.get_nonstandard_attr('SameSite')}")
                print(f"  Max-Age: {cookie.get_nonstandard_attr('Max-Age')}")
        else:
            print("No cookies found in response")
            
    except Exception as e:
        print(f"Error testing cookies: {e}")

if __name__ == "__main__":
    print("🔧 Authentication Fix Test Script")
    print("Make sure both backend and frontend are running:")
    print(f"  Backend: {BACKEND_URL}")
    print(f"  Frontend: {FRONTEND_URL}")
    print()
    
    test_auth_endpoints()
    test_cookie_settings()
    
    print("\n✅ Test completed!")
    print("\nNext steps:")
    print("1. Start both backend and frontend servers")
    print("2. Try logging in through the frontend")
    print("3. Check browser developer tools for cookie issues")
    print("4. Look for 'jwt_session' cookie in Application/Storage tab")