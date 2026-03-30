# Full Moon Slack Notifier 🌕

Automatically sends a Slack message at 9 AM Pacific Time on full moon days using GitHub Actions.

## Setup

### 1. Create Slack Webhook

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** (select "From scratch").
2. Name your app (e.g., "Full Moon Notifier") and select your workspace.
3. In the sidebar, click **Incoming Webhooks**.
4. Toggle **Activate Incoming Webhooks** to "On".
5. Click **Add New Webhook to Workspace** at the bottom and select a channel.
6. Copy the **Webhook URL** (it looks like `https://hooks.slack.com/services/T.../B.../...`). This is the secret URL you need.

### 2. Add GitHub Secret

1. Repository **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**: `SLACK_WEBHOOK_URL`
3. Paste your webhook URL

### 3. Done!

The workflow runs daily at 9 AM Pacific Time and only sends notifications on full moon days.

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
