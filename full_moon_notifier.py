# full_moon_notifier.py
import os
import math
import requests
import ephem
from datetime import datetime, timedelta
import pytz

PLANETS = {
    'Mercury': ephem.Mercury,
    'Venus': ephem.Venus,
    'Mars': ephem.Mars,
    'Jupiter': ephem.Jupiter,
    'Saturn': ephem.Saturn,
}

INNER_PLANETS = {'Mercury', 'Venus'}
OUTER_PLANETS = {'Mars', 'Jupiter', 'Saturn'}

# Los Angeles
LA_LAT = '34.05'
LA_LON = '-118.25'


def _noon_utc(dt):
    """Pin to noon UTC so results are consistent regardless of cron timing."""
    return dt.replace(hour=12, minute=0, second=0, microsecond=0)


def _get_observer(dt):
    obs = ephem.Observer()
    obs.lat = LA_LAT
    obs.lon = LA_LON
    obs.date = dt
    return obs


# --- Moon events ---

def _moon_event_tonight(next_fn, prev_fn):
    """Check if a moon event (full/new) is happening tonight.

    The cron runs at 9 AM Pacific (17:00 UTC). "Tonight" means the upcoming
    evening through early next morning.

    We look forward 24 hours to catch tonight's event, AND backward 4 hours
    to handle GitHub Actions cron delays (if the exact peak just passed,
    next_full_moon/next_new_moon jumps to next month — the original bug).

    A 4-hour backward window won't cause duplicates: by the next day's cron
    the peak will be ~28 hours in the past, well outside the window.
    """
    now = datetime.utcnow()
    current = ephem.Date(now)

    next_event = next_fn(now)
    hours_to_next = (float(next_event) - float(current)) * 24

    prev_event = prev_fn(now)
    hours_from_prev = (float(current) - float(prev_event)) * 24

    return hours_to_next <= 24 or hours_from_prev <= 4


def is_full_moon_tonight():
    return _moon_event_tonight(ephem.next_full_moon, ephem.previous_full_moon)


def is_new_moon_tonight():
    return _moon_event_tonight(ephem.next_new_moon, ephem.previous_new_moon)


# --- Planet events ---

def _get_elongation(planet_class, dt):
    """Get elongation in degrees for a planet on a given date."""
    obs = _get_observer(dt)
    planet = planet_class(obs)
    return math.degrees(abs(float(planet.elong)))


def _get_signed_elongation(planet_class, dt):
    """Get signed elongation (positive=evening, negative=morning)."""
    obs = _get_observer(dt)
    planet = planet_class(obs)
    return float(planet.elong)


def check_greatest_elongation(name, planet_class):
    """Check if an inner planet is at greatest elongation today (local max)."""
    now = _noon_utc(datetime.utcnow())
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    elong_yesterday = _get_elongation(planet_class, yesterday)
    elong_today = _get_elongation(planet_class, now)
    elong_tomorrow = _get_elongation(planet_class, tomorrow)

    # Must be a local maximum
    if elong_today < elong_yesterday or elong_today < elong_tomorrow:
        return None

    # Must be a significant elongation (not just a minor wobble)
    # Mercury rarely exceeds 28°, so 18° is a good threshold
    # Venus can reach 47°, so 40° is a good threshold
    threshold = 18 if name == 'Mercury' else 40
    if elong_today < threshold:
        return None

    signed = _get_signed_elongation(planet_class, now)
    apparition = "evening" if signed > 0 else "morning"

    return {
        'event': 'greatest_elongation',
        'planet': name,
        'elongation_deg': elong_today,
        'apparition': apparition,
    }


def check_opposition(name, planet_class):
    """Check if an outer planet is at opposition today (elongation peaks near 180°)."""
    now = _noon_utc(datetime.utcnow())
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    elong_yesterday = _get_elongation(planet_class, yesterday)
    elong_today = _get_elongation(planet_class, now)
    elong_tomorrow = _get_elongation(planet_class, tomorrow)

    # Must be a local maximum and reasonably close to 180°
    if elong_today < elong_yesterday or elong_today < elong_tomorrow:
        return None
    if elong_today < 150:
        return None

    return {
        'event': 'opposition',
        'planet': name,
        'elongation_deg': elong_today,
    }


def check_conjunctions():
    """Check for close conjunctions between any two planets (< 2°)."""
    now = _noon_utc(datetime.utcnow())
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    def _positions(dt):
        obs = _get_observer(dt)
        return {name: cls(obs) for name, cls in PLANETS.items()}

    pos_yesterday = _positions(yesterday)
    pos_today = _positions(now)
    pos_tomorrow = _positions(tomorrow)

    events = []
    names = list(PLANETS.keys())

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1, n2 = names[i], names[j]

            sep_today = float(ephem.separation(
                (pos_today[n1].ra, pos_today[n1].dec),
                (pos_today[n2].ra, pos_today[n2].dec),
            ))
            sep_yesterday = float(ephem.separation(
                (pos_yesterday[n1].ra, pos_yesterday[n1].dec),
                (pos_yesterday[n2].ra, pos_yesterday[n2].dec),
            ))
            sep_tomorrow = float(ephem.separation(
                (pos_tomorrow[n1].ra, pos_tomorrow[n1].dec),
                (pos_tomorrow[n2].ra, pos_tomorrow[n2].dec),
            ))

            sep_today_deg = math.degrees(sep_today)

            # Must be close AND at closest approach (local minimum)
            if sep_today_deg < 2.0 and sep_today <= sep_yesterday and sep_today <= sep_tomorrow:
                events.append({
                    'event': 'conjunction',
                    'planets': (n1, n2),
                    'separation_deg': sep_today_deg,
                })

    return events


# --- Event collection and formatting ---

def get_all_events():
    """Collect all astronomical events for today."""
    events = []

    if is_full_moon_tonight():
        events.append({'event': 'full_moon'})

    if is_new_moon_tonight():
        events.append({'event': 'new_moon'})

    for name, cls in PLANETS.items():
        if name in INNER_PLANETS:
            result = check_greatest_elongation(name, cls)
        else:
            result = check_opposition(name, cls)
        if result:
            events.append(result)

    events.extend(check_conjunctions())

    return events


def format_event(event):
    """Format an event into a Slack attachment payload."""
    if event['event'] == 'full_moon':
        return {
            'text': '\U0001f315 Full Moon Tonight!',
            'detail': 'The moon is full tonight! Watch out for werewolves. And/or get out and howl at the moon. \U0001f43a',
            'color': '#f1c40f',
        }
    elif event['event'] == 'new_moon':
        return {
            'text': '\U0001f311 New Moon Tonight!',
            'detail': 'Great night for stargazing \u2014 the sky will be extra dark. \U0001f52d',
            'color': '#2c3e50',
        }
    elif event['event'] == 'greatest_elongation':
        if event['apparition'] == 'evening':
            when = 'Look west after sunset tonight!'
        else:
            when = 'Set your alarm \u2014 look east before sunrise tomorrow morning!'
        return {
            'text': f'\u2728 {event["planet"]} at Greatest Elongation!',
            'detail': (
                f'{event["planet"]} is {event["elongation_deg"]:.1f}\u00b0 from the Sun \u2014 '
                f'best visibility this week. {when} \U0001f52d'
            ),
            'color': '#e67e22',
        }
    elif event['event'] == 'opposition':
        return {
            'text': f'\U0001f534 {event["planet"]} at Opposition!',
            'detail': (
                f'{event["planet"]} is opposite the Sun \u2014 at its brightest and visible all night. '
                f'Rises at sunset, sets at sunrise. \U0001f52d'
            ),
            'color': '#e74c3c',
        }
    elif event['event'] == 'conjunction':
        p1, p2 = event['planets']
        return {
            'text': f'\U0001f31f {p1}\u2013{p2} Conjunction!',
            'detail': f'{p1} and {p2} are just {event["separation_deg"]:.1f}\u00b0 apart \u2014 look up tonight! \U0001f52d',
            'color': '#9b59b6',
        }


def send_slack_message(webhook_url, event):
    """Send a single event notification to Slack."""
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
        print(f"\u2705 Sent: {fmt['text']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"\u274c Failed to send notification: {e}")
        return False


def check_and_notify():
    """The main job function that checks for events and notifies Slack."""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    if not webhook_url:
        print("\u274c SLACK_WEBHOOK_URL environment variable not set. Skipping check.")
        return

    pacific_tz = pytz.timezone('America/Los_Angeles')
    current_pacific_time = datetime.now(pacific_tz).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_pacific_time} PT] \U0001f50d Running check...")

    events = get_all_events()

    if events:
        for event in events:
            send_slack_message(webhook_url, event)
    else:
        print("\U0001f4ab Nothing notable today \u2014 no notifications sent")


if __name__ == "__main__":
    check_and_notify()
