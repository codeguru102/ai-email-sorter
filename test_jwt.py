#!/usr/bin/env python3
"""
Test JWT token creation and verification
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.security import make_session_jwt, verify_session_jwt

def test_jwt():
    print("Testing JWT creation and verification...")
    
    # Create a test JWT
    jwt_token = make_session_jwt(
        sub="104113443837218250223",
        email="romanfedko60@gmail.com", 
        name="Roman Engineering",
        picture="https://lh3.googleusercontent.com/a/ACg8ocIeaSDJ00Pvw7ZQ3fBpyo9OI3QlNL5B_YjdCKYZ5VHJW8vqvFjV=s96-c"
    )
    
    print(f"Created JWT: {jwt_token[:50]}...")
    
    # Verify the JWT
    decoded = verify_session_jwt(jwt_token)
    
    if decoded:
        print("JWT verification successful!")
        print(f"Decoded data: {decoded}")
    else:
        print("JWT verification failed!")
    
    return jwt_token

if __name__ == "__main__":
    test_jwt()