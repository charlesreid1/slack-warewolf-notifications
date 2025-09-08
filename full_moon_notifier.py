# full_moon_notifier.py
import os
import requests
import ephem
from datetime import datetime

def is_full_moon_today():
    """Check if today is a full moon day (within 12 hours)"""
    now = datetime.utcnow()
    
    # Get next full moon
    next_full = ephem.next_full_moon(now)
    current_date = ephem.Date(now)
    
    # Check if full moon is within 12 hours (0.5 days)
    days_diff = abs(float(next_full) - float(current_date))
    
    return days_diff <= 0.5

def send_slack_message(webhook_url):
    """Send full moon message to Slack"""
    payload = {
            "text": "🌕 Full Moon Today! 🌕",
        "attachments": [
            {
                "color": "#f1c40f",
                "fields": [
                    {
                        "title": "Full Moon Alert",
                        "value": "The moon is full tonight! Watch out for werewolves. And/or get out and howl at the moon. 🐺",
                        "short": False
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Full moon Slack notification sent!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Slack notification: {e}")
        return False

def main():
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL environment variable not set")
        return
    
    print("🔍 Checking if today is a full moon...")
    
    if is_full_moon_today():
        print("🌕 It's a full moon today!")
        send_slack_message(webhook_url)
    else:
        print("🌙 Not a full moon today - no notification sent")

if __name__ == "__main__":
    main()
