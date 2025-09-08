# Full Moon Slack Notifier 🌕

Automatically sends a Slack message at 9 AM UTC on full moon days using GitHub Actions.

## Setup

### 1. Create Slack Webhook

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App**
2. Enable **Incoming Webhooks** → **Add New Webhook to Workspace**
3. Copy the webhook URL

### 2. Add GitHub Secret

1. Repository **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**: `SLACK_WEBHOOK_URL`
3. Paste your webhook URL

### 3. Done!

The workflow runs daily at 9 AM UTC and only sends notifications on full moon days.

## Files Structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── lunar-phases.yml
├── full_moon_notifier.py
└── README.md
```

## Manual Test

**Actions** tab → **Full Moon Notifications** → **Run workflow**
