#!/usr/bin/env python3
"""
Find the correct backend port
"""
import requests

def find_backend_port():
    """Try common ports to find where the backend is running"""
    
    common_ports = [8000, 8080, 3001, 5000, 8001]
    
    for port in common_ports:
        try:
            url = f"http://localhost:{port}/api/auth/me"
            response = requests.get(url, timeout=2)
            print(f"✅ Backend found on port {port}")
            return port
        except:
            continue
    
    print("❌ Backend not found on common ports")
    return None

if __name__ == "__main__":
    port = find_backend_port()
    if port:
        print(f"Use this URL: http://localhost:{port}/api/gmail/webhook")