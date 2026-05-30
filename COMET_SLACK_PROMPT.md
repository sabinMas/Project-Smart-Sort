# Comet Agent Prompt — Slack Webhook Setup

Copy everything in the block below and paste it into Comet. It will drive the
browser parts (Slack + Render). Replace the two ALL-CAPS placeholders first if
you can; if not, Comet will pause and ask.

---

```
You are helping me set up a Slack incoming webhook and add it to my Render
backend service. Do the browser steps and pause for me when you need a login,
a 2FA code, or a decision. Do not skip the verification steps.

CONTEXT
- Slack channel for notifications: #documents
- Render service name: project-smart-sort
- My Slack workspace: WORKSPACE_NAME
- My Render account email: RENDER_EMAIL

TASK 1 — Create the Slack incoming webhook
1. Open https://api.slack.com/apps
2. Click "Create New App" then "From scratch".
3. App name: "Box Smart Inbox". Select my workspace. Create the app.
4. Open "Incoming Webhooks" in the left sidebar.
5. Turn "Activate Incoming Webhooks" ON.
6. Click "Add New Webhook to Workspace".
7. Select the "#documents" channel and click Allow.
8. Copy the generated webhook URL (format: https://hooks.slack.com/services/.../.../...).
9. Show me the URL and confirm you captured it. Treat it as a secret — do not
   share it anywhere except the Render step below.

TASK 2 — Add it to Render and redeploy
1. Open https://dashboard.render.com
2. Open the service named "project-smart-sort".
3. Go to the "Environment" tab.
4. Set environment variable SLACK_WEBHOOK_URL to the webhook URL from Task 1.
5. Set environment variable DEMO_MODE to false (add it if missing).
6. Save changes. Confirm Render starts a redeploy.
7. Watch the deploy until it shows "Live".

TASK 3 — Verify production is up
1. In a browser tab, open https://project-smart-sort.onrender.com/health
2. Confirm the response is JSON with "status":"ok". Report what you see.

RULES
- Pause and ask me whenever a login, 2FA, or confirmation is required.
- Never post the webhook URL into any field other than the Render
  SLACK_WEBHOOK_URL variable.
- After each task, give me a one-line status before moving on.
```

---

After Comet finishes Task 1 and gives you the URL, you can also locally confirm
the URL actually posts to the channel (uses your real backend code):

```bash
python backend/scripts/test_slack_webhook.py "PASTE_WEBHOOK_URL_HERE"
```
