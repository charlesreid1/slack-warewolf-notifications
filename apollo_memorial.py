# apollo_memorial.py
import os
import requests
from datetime import datetime
import pytz

APOLLO11_LAUNCH_YEAR = 1969

# (month, day, key, title, detail_template)
# detail_template supports {years} for the anniversary count.
APOLLO11_EVENTS = [
    (
        7, 16, 'launch',
        '\U0001f680 Apollo 11 Launched!',
        '{years} years ago today, Apollo 11 lifted off from Kennedy Space Center '
        'atop a Saturn V — Armstrong, Aldrin, and Collins on their way to the Moon.',
    ),
    (
        7, 20, 'landing',
        '\U0001f315 Apollo 11 Landed on the Moon!',
        '{years} years ago today, the Eagle touched down in the Sea of Tranquility at '
        '1:17 PM PT — "The Eagle has landed." Armstrong took his first step onto the '
        'lunar surface at 7:56 PM PT tonight. One small step.',
    ),
    (
        7, 21, 'lunar_liftoff',
        '\U0001f315 Apollo 11 Departed the Moon!',
        '{years} years ago today, the Eagle’s ascent stage lifted off from the lunar surface '
        'to rendezvous with Columbia in orbit.',
    ),
    (
        7, 24, 'splashdown',
        '\U0001f30a Apollo 11 Returned to Earth!',
        '{years} years ago today, Apollo 11 splashed down in the Pacific Ocean, '
        'safely returning the crew home after their journey to the Moon.',
    ),
]

APOLLO_COLOR = '#1a237e'


def _pacific_now():
    return datetime.now(pytz.timezone('America/Los_Angeles'))


def get_apollo_events(now=None):
    """Return any Apollo 11 anniversary events matching today's Pacific date."""
    if now is None:
        now = _pacific_now()
    years = now.year - APOLLO11_LAUNCH_YEAR
    events = []
    for month, day, key, title, detail_template in APOLLO11_EVENTS:
        if now.month == month and now.day == day:
            events.append({
                'event': f'apollo11_{key}',
                'title': title,
                'detail': detail_template.format(years=years),
            })
    return events


def format_event(event):
    return {
        'text': event['title'],
        'detail': event['detail'],
        'color': APOLLO_COLOR,
    }


def send_slack_message(webhook_url, event):
    fmt = format_event(event)
    payload = {
        "text": fmt['text'],
        "attachments": [{
            "color": fmt['color'],
            "fields": [{
                "title": fmt['text'],
                "value": fmt['detail'],
                "short": False,
            }]
        }]
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Sent: {fmt['text']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send notification: {e}")
        return False


def check_and_notify():
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL environment variable not set. Skipping check.")
        return

    now = _pacific_now()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')} PT] \U0001f680 Running Apollo memorial check...")

    events = get_apollo_events(now)

    if events:
        for event in events:
            send_slack_message(webhook_url, event)
    else:
        print("\U0001f4ab No Apollo 11 anniversaries today")


if __name__ == "__main__":
    check_and_notify()
