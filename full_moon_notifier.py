# full_moon_notifier.py
import os
import requests
import ephem
import schedule
import time
from datetime import datetime
import pytz

def is_full_moon_today():
    """Check if today is a full moon day (within 12 hours)"""
    now = datetime.utcnow()
    next_full = ephem.next_full_moon(now)
    current_date = ephem.Date(now)
    days_diff = abs(float(next_full) - float(current_date))
    return days_diff <= 0.5

def send_slack_message(webhook_url):
    """Send full moon message to Slack"""
    payload = {
        "text": "🌕 Full Moon Today! 🌕",
        "attachments": [{
            "color": "#f1c40f",
            "fields": [{
                "title": "Full Moon Alert",
                "value": "The moon is full tonight! Watch out for werewolves. And/or get out and howl at the moon. 🐺",
                "short": False
            }]
        }]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Full moon Slack notification sent!") # This is now the only success message
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Slack notification: {e}")
        return False

def check_and_notify():
    """The main job function that checks for a full moon and notifies Slack."""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL environment variable not set. Skipping check.")
        return
    
    pacific_tz = pytz.timezone('America/Los_Angeles')
    current_pacific_time = datetime.now(pacific_tz).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_pacific_time} PT] 🔍 Running check...")
    
    if is_full_moon_today():
        # The redundant print statement was removed from here.
        send_slack_message(webhook_url)
    else:
        print("🌙 Not a full moon today - no notification sent")

if __name__ == "__main__":
    print("Scheduler started. Waiting to run the check at 9 AM Pacific Time...")
    
    schedule.every().day.at("09:00", "America/Los_Angeles").do(check_and_notify)

    while True:
        schedule.run_pending()
        time.sleep(60)
