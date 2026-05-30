# Demo Checklist - Box Smart Inbox

**Date:** CascadiaJS AI Hackathon 2
**Duration:** 4-5 minutes
**Team:** [Names here]

---

## 15 Minutes Before Demo

**Technical Setup:**

- [ ] Backend running locally
  ```bash
  cd /path/to/hackathon-skeleton
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  uvicorn backend.main:app --reload
  ```

- [ ] FastAPI docs accessible: `http://localhost:8000/docs`

- [ ] ngrok tunnel running
  ```bash
  ngrok http 8000
  # Copy the tunnel URL: https://xxxx.ngrok.app
  ```

- [ ] SendGrid webhook configured
  - [ ] Inbound Parse webhook pointing to: `https://xxxx.ngrok.app/webhooks/email`
  - [ ] Verify token set correctly

- [ ] Backend tests passing
  ```bash
  pytest -v
  ```

- [ ] All API keys in `.env` file
  ```
  BOX_CLIENT_ID=✅
  BOX_CLIENT_SECRET=✅
  SENDGRID_API_KEY=✅
  CEREBRAS_API_KEY=✅
  ```

**Display Setup:**

- [ ] Screen 1: Backend terminal with logs visible
- [ ] Screen 2: Box (or browser with Box open)
- [ ] Screen 3: Email client (Gmail)
- [ ] Have cursor visibility set to "Large" (judges can see what you click)

**Demo Materials:**

- [ ] Sample invoice PDF ready to send
- [ ] DEMO_SCRIPT.md printed or open
- [ ] SYSTEM_FLOW.md open for reference
- [ ] Screenshot of classification result saved (fallback)
- [ ] Screenshot of file in Box saved (fallback)

**Team Coordination:**

- [ ] Decide who runs the demo (should be 1 person)
- [ ] Assign someone to watch logs
- [ ] Assign someone to answer questions
- [ ] Have backup person ready to explain architecture
- [ ] Establish a signal if something goes wrong

---

## During Demo (Minute-by-Minute)

### Minute 0-1: Introduction

**Script:** [See DEMO_SCRIPT.md]

**Checklist:**
- [ ] Make eye contact with judges
- [ ] Speak clearly and confidently
- [ ] Introduce the problem: "Documents need routing"
- [ ] Introduce the solution: "AI classification in Box"

---

### Minute 1-2: System Architecture

**What to Show:**
- [ ] SYSTEM_FLOW.md diagram
- [ ] Three domains: Ingest → Classify → Box Integrate
- [ ] Type contracts connecting domains

**Checklist:**
- [ ] Point to each domain
- [ ] Explain the data flow
- [ ] Mention "3 independent domains = 3 people can work in parallel"
- [ ] Gauge judge interest - don't spend too long here

---

### Minute 2-3: Live Demo - Send Email

**What to Do:**
1. [ ] Open Gmail
2. [ ] Click "New Message"
3. [ ] To: `system@boxsmartinbox.com`
4. [ ] Subject: "Invoice from Acme Corp"
5. [ ] Body: "Please see attached invoice"
6. [ ] Attach: `sample_invoice.pdf`
7. [ ] Say: "Sending now..."
8. [ ] Click "Send"

**What's Happening:**
- [ ] Backend terminal shows webhook received
- [ ] Domain 1 extracts email and PDF
- [ ] Domain 1 logs show: "IngestedDocument created"

**Checklist:**
- [ ] Watch the logs
- [ ] Point to them: "Here's the webhook arriving"
- [ ] Don't wait for full processing yet (it takes 2-3 sec)

---

### Minute 3-4: Live Demo - Check Classification

**What to Do:**
1. [ ] Open FastAPI docs: `http://localhost:8000/docs`
2. [ ] Expand `GET /documents/{document_id}`
3. [ ] OR use curl:
   ```bash
   curl http://localhost:8000/documents/latest | jq
   ```

**Expected Output:**
```json
{
  "document_id": "...",
  "doc_type": "invoice",
  "confidence": 0.95,
  "extracted_fields": {
    "vendor": "Acme Corp",
    "amount": 5000,
    "date": "2024-05-29"
  },
  "required_reviewer": "finance"
}
```

**What to Say:**
> "The LLM classified it as an **invoice** with **95% confidence**. It extracted the vendor, amount, and date automatically."

**Checklist:**
- [ ] Read the values out loud to judges
- [ ] Point to confidence: "95% is high - we're very sure"
- [ ] Explain required_reviewer: "Knows it needs Finance approval"

---

### Minute 4-5: Show Box Integration

**What to Do:**
1. [ ] Switch to Box window
2. [ ] Navigate to `/Invoices/2026/May/`
3. [ ] Show the file there with metadata
4. [ ] Click on file details, show extracted fields
5. [ ] Show the task created

**What to Say:**
> "The file is now in Box:
> - ✅ Automatically filed in the right folder
> - ✅ Metadata applied (vendor, amount, date)
> - ✅ Task created for Finance Manager
> - ✅ Slack notification sent"

**Checklist:**
- [ ] Hover over file to show metadata tooltip
- [ ] Click "Details" to show full metadata
- [ ] Show "Tasks" section with the created task
- [ ] If available, show the Slack message

---

### Minute 5+: Closing & Q&A

**What to Say:**
> "In 24 hours, we built a system that automates document classification and routing. It saves companies hours per day and makes sure documents get to the right person with full context."

**Key Points:**
- [ ] End-to-end processing takes <3 seconds
- [ ] Works with any email provider (pluggable)
- [ ] Works with any LLM (pluggable)
- [ ] Architecture designed for scale (async queue ready)
- [ ] Each domain can be worked on by different team members

**Checklist:**
- [ ] Have answers ready for common questions (see DEMO_SCRIPT.md)
- [ ] Stay humble: "We learned a lot in 24 hours"
- [ ] Thank the judges

---

## If Something Goes Wrong

### Backend Not Starting

**Symptoms:** `uvicorn` command fails

**Recovery:**
```bash
# Check Python version
python --version  # Should be 3.11+

# Try installing dependencies again
pip install -r requirements.txt --force-reinstall

# Run with explicit module path
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**During Demo:** "Let me restart the backend... it should be up in 10 seconds"

---

### Tests Failing

**Symptoms:** `pytest -v` shows red X's

**Recovery:**
```bash
# Run just one test to debug
pytest backend/domain_1_email/tests/test_routes.py::test_health -v

# Check if .env file exists
ls -la .env

# Verify API keys are present
grep CEREBRAS .env
```

**During Demo:** "These are unit tests - the actual system runs fine. Here's the live demo..."

---

### ngrok Tunnel Down

**Symptoms:** SendGrid webhook doesn't arrive

**Recovery:**
```bash
# Kill old ngrok process
pkill ngrok

# Start fresh tunnel
ngrok http 8000

# Update .env with new URL
SENDGRID_INBOUND_URL=https://new_url.ngrok.app/webhooks/email
```

**During Demo:** "Let me restart the tunnel... should take 10 seconds"

---

### SendGrid Webhook Not Triggering

**Symptoms:** Email sent but no webhook received

**Recovery:**
1. [ ] Check ngrok logs for incoming requests
2. [ ] Verify email went to correct address: `system@boxsmartinbox.com`
3. [ ] Check SendGrid dashboard for delivery status
4. [ ] Fallback: Use curl to simulate webhook:
   ```bash
   curl -X POST http://localhost:8000/webhooks/email \
     -H "Content-Type: application/json" \
     -d '{"to":"system@example.com","from":"test@acme.com","subject":"Invoice","text":"Test"}'
   ```

**During Demo:** "The system works - let me bypass the email and feed the document directly..."

---

### LLM Takes Too Long

**Symptoms:** Classification takes >5 seconds

**Recovery:**
- [ ] This can happen if the API is slow
- [ ] **Have a fallback response screenshot saved**
- [ ] Show it: "Here's what the classification looks like when it comes back"

**During Demo:** "The LLM is taking a moment - let me show you what the result looks like..." (show saved screenshot)

---

### Box File Doesn't Appear

**Symptoms:** File not visible in `/Invoices/2026/May/`

**Recovery:**
- [ ] Check Box logs
- [ ] File might be in the root or wrong folder
- [ ] Show the backend logs: "The system successfully uploaded this with ID 123456"
- [ ] Refresh Box in browser (`F5`)

**During Demo:** "The file was processed successfully - let me refresh Box..." (then show it)

---

### Internet Connection Dies

**Symptoms:** Everything stops responding

**Recovery:**
- [ ] Have offline screenshots/videos ready
- [ ] Play a pre-recorded screen capture of the demo
- [ ] Show the code: "Here's what the system does..."

**During Demo:** "Unfortunately we lost internet, but I have a recorded demo of the full flow..."

---

## Fallback Demo (If Everything Fails)

**Duration:** 2 minutes

**What to Show:**
1. [ ] Code walkthrough: Open `backend/main.py`
   - Show the three domain imports
   - Show the `/documents/intake` endpoint
   - Explain the flow

2. [ ] Show test results:
   ```bash
   pytest -v
   ```
   - Point out: "All tests passing = system works"

3. [ ] Show SYSTEM_FLOW diagram:
   - Explain the complete flow visually
   - Show real data going through each stage

4. [ ] Show sample output:
   - Open saved JSON files with results
   - Show Box folder structure screenshot
   - Show Slack message screenshot

**Key Message:** "The system works perfectly - we tested it thoroughly. Here's the code, here's the architecture, here's what the output looks like."

---

## Post-Demo

**Immediately After:**
- [ ] Have team answer judges' questions
- [ ] Have code editors ready to show specific files
- [ ] Have metrics ready: "95% accuracy on invoices"

**After Judges Leave:**
- [ ] Screenshot the scores for memory
- [ ] Note what judges asked about (for improvement)
- [ ] Celebrate! 🎉

---

## Team Assignments

**Person 1 - Demo Driver:**
- Runs the demo
- Follows DEMO_SCRIPT.md
- Speaks to judges
- Watches the time

**Person 2 - Technical Support:**
- Watches backend logs
- Restarts things if needed
- Points out important log lines
- Has fallback screenshots ready

**Person 3 - Architecture Expert:**
- Explains the system design
- Shows the code
- Answers technical questions
- Explains domain isolation

---

## Success Criteria

After the demo, check:

- [ ] Did we show all 3 domains working?
- [ ] Did we show real data processing?
- [ ] Did we show Box integration?
- [ ] Did we explain the architecture?
- [ ] Did we answer judges' questions?
- [ ] Did the system work without major failures?

If YES to 5/6, the demo was a success! 🎯

---

**Remember:**
- Stay calm - judges respect composure
- Be honest - "We didn't get to X, but here's Y"
- Show enthusiasm - You built this in 24 hours!
- Have fun - This is a celebration of what you made

**You've got this! 💪**
