#!/usr/bin/env python3
import requests
import json
import base64

# Test the actual webhook endpoint
webhook_url = "http://localhost:8000/api/gmail/webhook"

# Sample notification
sample_notification = {
    "message": {
        "data": base64.b64encode(json.dumps({
            "emailAddress": "raymondli378@gmail.com",
            "historyId": "12345678"
        }).encode()).decode(),
        "messageId": "test-message-id"
    }
}

try:
    print("Testing Gmail webhook...")
    response = requests.post(webhook_url, json=sample_notification, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")