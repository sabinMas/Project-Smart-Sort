# Slack Webhook Setup (Production)

Goal: get a Slack incoming webhook live and wired into the **deployed** backend on Render so document notifications post to `#documents`.

> The local `.env` does NOT reach the deployed app. Production config lives in the Render dashboard.

---

## Part 1 — Create the Slack webhook

1. Go to https://api.slack.com/apps
2. Click **Create New App** → **From scratch**.
3. Name it `Box Smart Inbox`, pick your workspace, click **Create App**.
4. In the left sidebar, open **Incoming Webhooks**.
5. Toggle **Activate Incoming Webhooks** to **On**.
6. Click **Add New Webhook to Workspace**.
7. Choose the **#documents** channel, click **Allow**.
8. Copy the webhook URL. It looks like `https://hooks.slack.com/services/XXX/YYY/ZZZ`.

Keep this URL private — anyone who has it can post to your channel.

---

## Part 2 — Verify the URL works (before trusting it)

From the repo root, run:

```bash
python backend/scripts/test_slack_webhook.py "https://hooks.slack.com/services/XXX/YYY/ZZZ"
```

- **Success:** prints `SUCCESS` and a test invoice message appears in `#documents`.
- **Failure:** prints the HTTP status and a hint. Re-copy the URL and retry.

---

## Part 3 — Set it on Render (production)

1. Go to https://dashboard.render.com
2. Open the backend service (**project-smart-sort**).
3. Open the **Environment** tab.
4. Add / edit these variables:
   - `SLACK_WEBHOOK_URL` = the URL from Part 1
   - `DEMO_MODE` = `false`
5. **Save Changes**. Render redeploys automatically.

---

## Part 4 — Confirm production is back up

After the redeploy finishes (watch the **Events**/**Logs** tab), check health:

```bash
curl https://project-smart-sort.onrender.com/health
```

Expect `{"status":"ok",...}`.

---

## Notes / caveats

- Parts 2 and 4 prove the **webhook plumbing** works. They do NOT prove the full
  email → classify → Box flow fires Slack — that pipeline wiring is a separate task
  (teammate). Do one end-to-end dry run together before judging.
- Do not paste the webhook URL into the local `.env` or commit it. Render's
  Environment tab is the source of truth for production.
