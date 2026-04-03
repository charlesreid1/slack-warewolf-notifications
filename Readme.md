# Astronomy Slack Notifier

Daily Slack notifications for notable astronomical events, powered by GitHub Actions and [PyEphem](https://rhodesmill.org/pyephem/).

## What It Tracks

- **Full Moon** -- werewolf warning included
- **New Moon** -- heads-up for prime stargazing conditions
- **Greatest Elongation** -- Mercury and Venus at peak visibility (morning or evening)
- **Opposition** -- Mars, Jupiter, and Saturn at their brightest (visible all night)
- **Planetary Conjunctions** -- any two planets within 2 degrees of each other

All calculations use [ephem](https://rhodesmill.org/pyephem/) (PyEphem), a Python library that computes positions of the Sun, Moon, and planets with high precision. Observer location is set to Los Angeles. The workflow runs daily at 9 AM Pacific and only sends a Slack message when there's something worth looking at.

## Setup

### 1. Create a Slack Webhook

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and create a new app from scratch.
2. Enable **Incoming Webhooks** and add one to your desired channel.
3. Copy the webhook URL.

### 2. Add the GitHub Secret

1. Repository **Settings** > **Secrets and variables** > **Actions**
2. Create a new secret named `SLACK_WEBHOOK_URL` with your webhook URL.

### 3. Done

The workflow handles the rest. You can also trigger it manually from the **Actions** tab.

## Files

```
.github/workflows/lunar-phases.yml   # Daily cron workflow
full_moon_notifier.py                 # Event detection + Slack messaging
```
