#!/usr/bin/env python3
"""
Quick test script to verify backend auth endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_auth_endpoints():
    print("Testing authentication endpoints...")
    
    # Test /auth/me endpoint
    print("\n1. Testing /auth/me (should return not authenticated)")
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test debug cookies endpoint
    print("\n2. Testing /auth/debug/cookies")
    try:
        response = requests.get(f"{BASE_URL}/auth/debug/cookies")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test create test session
    print("\n3. Testing /auth/debug/create-test-session")
    try:
        response = requests.get(f"{BASE_URL}/auth/debug/create-test-session")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print(f"Cookies set: {response.cookies}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth_endpoints()