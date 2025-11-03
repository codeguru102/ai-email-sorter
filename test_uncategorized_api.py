#!/usr/bin/env python3
import requests

def test_uncategorized_api():
    try:
        # Test the uncategorized emails endpoint
        response = requests.get("http://localhost:8000/api/emails/uncategorized", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("Authentication required - this is expected for direct API call")
        elif response.status_code == 200:
            emails = response.json()
            print(f"Found {len(emails)} uncategorized emails")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_uncategorized_api()