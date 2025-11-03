#!/usr/bin/env python3
"""
Quick test to verify auth endpoints work
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_auth():
    print("Testing auth endpoints...")
    
    # 1. Clear cookies first
    print("\n1. Clearing cookies...")
    try:
        response = requests.get(f"{BASE_URL}/auth/debug/clear-cookies")
        print(f"Clear cookies: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error clearing cookies: {e}")
    
    # 2. Test /auth/me (should be not authenticated)
    print("\n2. Testing /auth/me (should be not authenticated)...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        print(f"Auth check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Create test session
    print("\n3. Creating test session...")
    try:
        response = requests.get(f"{BASE_URL}/auth/debug/create-test-session")
        print(f"Test session: {response.status_code} - {response.json()}")
        cookies = response.cookies
        print(f"Cookies received: {dict(cookies)}")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # 4. Test /auth/me with session cookie
    print("\n4. Testing /auth/me with session cookie...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", cookies=cookies)
        print(f"Auth check with cookie: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth()