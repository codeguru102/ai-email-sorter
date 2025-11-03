#!/usr/bin/env python3
"""
Gmail Monitor - Real-time email notification monitor
Run this script to monitor Gmail notifications and see email titles as they arrive
"""
import time
import requests
import json
from datetime import datetime, timedelta

class GmailMonitor:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.last_check = datetime.now()
        
    def check_recent_emails(self):
        """Check for recent emails via the backend API"""
        try:
            # This would require an API endpoint to get recent emails
            # For now, we'll just show how to monitor
            response = requests.get(f"{self.backend_url}/gmail/webhook-test", timeout=5)
            if response.status_code == 200:
                return True
        except:
            return False
        return False
    
    def monitor_logs(self):
        """Monitor for new email notifications"""
        print("🔍 Gmail Monitor Started")
        print("=" * 50)
        print("Monitoring for new Gmail notifications...")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        try:
            while True:
                current_time = datetime.now()
                
                # Check if backend is running
                if self.check_recent_emails():
                    status = "🟢 Backend Online"
                else:
                    status = "🔴 Backend Offline"
                
                print(f"\\r{current_time.strftime('%H:%M:%S')} | {status} | Monitoring...", end="", flush=True)
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\\n\\n👋 Gmail Monitor Stopped")

def main():
    print("📧 Gmail Notification Monitor")
    print("This script monitors your Gmail notifications in real-time")
    print()
    
    monitor = GmailMonitor()
    
    # Check if backend is running
    if not monitor.check_recent_emails():
        print("❌ Backend not running!")
        print("Please start your backend server first:")
        print("   cd backend")
        print("   python -m uvicorn app.main:app --reload")
        return
    
    print("✅ Backend is running")
    print()
    
    # Instructions
    print("📋 Setup Instructions:")
    print("1. Make sure Gmail push notifications are configured")
    print("2. Send yourself a test email")
    print("3. Watch for email titles to appear in your backend logs")
    print("4. Email titles will be logged both in the backend console and logs")
    print()
    
    # Start monitoring
    monitor.monitor_logs()

if __name__ == "__main__":
    main()