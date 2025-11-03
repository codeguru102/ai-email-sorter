#!/usr/bin/env python3
import requests

# Test if the delete endpoint exists
def test_delete_endpoint():
    # First, let's see what endpoints are available
    try:
        # Test with a non-existent category ID to see if endpoint exists
        response = requests.delete("http://localhost:8000/api/emails/categories/999", timeout=5)
        print(f"DELETE endpoint status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404 and "Not Found" in response.text and "detail" in response.text:
            print("Endpoint exists but category not found (expected)")
        elif response.status_code == 404 and "Not Found" == response.text:
            print("Endpoint does not exist - route not found")
        else:
            print("Endpoint exists and working")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_delete_endpoint()