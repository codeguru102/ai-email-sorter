#!/usr/bin/env python3
"""
Test script to verify Gmail notification logging functionality
"""
import requests
import json
import base64
from datetime import datetime

def find_backend_port():
    """Find the correct backend port"""
    common_ports = [8000, 8080, 3001, 5000, 8001]
    
    for port in common_ports:
        try:
            url = f"http://localhost:{port}/api/auth/me"
            response = requests.get(url, timeout=2)
            return port
        except:
            continue
    return None

def test_gmail_webhook():
    """Test the Gmail webhook endpoint with a sample notification"""
    
    # Find backend port
    port = find_backend_port()
    if not port:
        print("Could not find backend. Make sure it's running.")
        return
    
    # Sample Gmail notification data (simulated)
    sample_notification = {
        "message": {
            "data": base64.b64encode(json.dumps({
                "emailAddress": "raymondli378@gmail.com",
                "historyId": "12345678"
            }).encode()).decode(),
            "messageId": "test-message-id",
            "publishTime": datetime.now().isoformat()
        }
    }
    
    webhook_url = f"http://localhost:{port}/api/gmail/webhook"
    
    try:
        print("Testing Gmail webhook notification...")
        print(f"Sending test notification to: {webhook_url}")
        
        response = requests.post(
            webhook_url,
            json=sample_notification,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.json()}")
        
        if response.status_code == 200:
            print("Gmail webhook test successful!")
            print("Check your backend logs for email titles")
        else:
            print("Gmail webhook test failed")
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to backend. Make sure it's running")
    except Exception as e:
        print(f"Test failed: {str(e)}")

def test_webhook_reachability():
    """Test if the webhook endpoint is reachable"""
    
    port = find_backend_port()
    if not port:
        print("Backend not found on common ports")
        return False
        
    test_url = f"http://localhost:{port}/api/gmail/webhook-test"
    
    try:
        print("Testing webhook reachability...")
        response = requests.get(test_url, timeout=5)
        
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("Webhook endpoint is reachable!")
            return True
        else:
            print("Webhook endpoint returned error")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Backend not running. Start it with: cd backend && python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Gmail Notification Logging Test")
    print("=" * 40)
    
    # First test reachability
    if test_webhook_reachability():
        print()
        # Then test the actual webhook
        test_gmail_webhook()
    
    print("\nInstructions:")
    print("1. Make sure your backend is running")
    print("2. Replace 'your-email@gmail.com' with your actual Gmail address")
    print("3. Check backend logs for email title output")
    print("4. For real Gmail notifications, ensure Gmail push notifications are set up")