#!/usr/bin/env python3
import requests

def check_categories():
    try:
        # Get categories to see what exists
        response = requests.get("http://localhost:8000/api/emails/categories", timeout=5)
        print(f"GET categories status: {response.status_code}")
        
        if response.status_code == 200:
            categories = response.json()
            print(f"Found {len(categories)} categories:")
            for cat in categories:
                print(f"  ID: {cat['id']}, Name: {cat['name']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_categories()