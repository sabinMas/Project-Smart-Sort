# Manager Tasks - Your Role (Mason)

Welcome! You're the **Project Manager / Scrum Master** for this hackathon. Your job is coordination, credentials, merges, and unblocking the team.

---

## Your Responsibilities

✅ **Credentials & Setup**
- Get API keys from services (SendGrid, Box, Cerebras)
- Create and manage `.env` file
- Distribute credentials securely to team
- Verify all services work before coding starts

✅ **Team Coordination**
- Assign each person to a domain (Person A/B/C)
- Ensure they read their DOMAIN_*_SETUP.md file
- Set up communication (Discord/Slack)
- Unblock people who are stuck

✅ **Git Management**
- Review and merge PRs from each domain
- Resolve merge conflicts
- Ensure commits follow the naming convention
- Manage the master branch

✅ **Testing & Integration**
- Run `pytest -v` after each merge
- Integrate domains together (T+16h)
- Verify end-to-end flow works
- Fix integration issues

✅ **Demo Preparation**
- Prep demo script and checklist
- Assign demo driver and supporting roles
- Do dry runs before judges
- Manage time on stage

---

## Your Timeline

### T-2 hours (Before Event - DO TODAY)

**Credentials Setup (30 minutes):**
- [ ] Create SendGrid account → get API key & verify token
- [ ] Create Box developer app → get Client ID/Secret/Enterprise ID/Dev Token
- [ ] Get Cerebras API key (and Groq as backup)
- [ ] Set up ngrok tunnel: `ngrok http 8000`
- [ ] Fill in `.env` file with all credentials

**Team Setup (15 minutes):**
- [ ] Create Discord or Slack channel for team
- [ ] Send team repo link
- [ ] Assign each person their domain:
  - Person A → DOMAIN_1_SETUP.md (Email Ingestion)
  - Person B → DOMAIN_2_SETUP.md (AI Classification)
  - Person C → DOMAIN_3_SETUP.md (Box Integration)
  - You → MANAGER_TASKS.md (Orchestration)
- [ ] Share `.env` file securely (direct message, NOT in git)

**Verification (15 minutes):**
- [ ] Everyone clones repo
- [ ] Everyone runs `python -m venv venv && pip install -r requirements.txt`
- [ ] Everyone runs `pytest -v` (tests will fail on business logic - that's OK!)
- [ ] Everyone can start `uvicorn backend.main:app --reload`

### T+0 (Event Starts)

- [ ] All team members present
- [ ] Everyone has `.env` file
- [ ] Backend runs locally
- [ ] Team watches 1-hour demo on AI/Box
- [ ] Make note of important info from demo

### T+1h (Coding Begins)

- [ ] Domain 1 starts implementing email webhook
- [ ] Domain 2 starts implementing LLM classification
- [ ] Domain 3 starts implementing Box integration
- [ ] You monitor progress, answer questions

### T+8h (Checkpoint)

- [ ] Check with each person: "How's it going?"
- [ ] Domain 1: Webhook implemented?
- [ ] Domain 2: LLM classification working?
- [ ] Domain 3: Box routing working?
- [ ] Unblock anyone who's stuck
- [ ] Coffee/food break for team

### T+12h (Integration Starts)

- [ ] Review and merge PRs from all three domains
- [ ] Run full test suite: `pytest -v`
- [ ] If tests pass: Time to integrate! 🎉
- [ ] If tests fail: Help debug

### T+14h (Integration Testing)

- [ ] Test end-to-end flow manually:
  1. Send test email to greenriver.hack.squad@gmail.com
  2. Watch it get classified
  3. Verify file appears in Box
  4. Check task was created
  5. Verify Slack notification sent
- [ ] If it works: You're in great shape!
- [ ] If it doesn't: Debug with team

### T+18h (Demo Prep)

- [ ] Prepare materials:
  - [ ] Sample invoice PDF ready to email
  - [ ] DEMO_SCRIPT.md printed
  - [ ] DEMO_CHECKLIST.md open
  - [ ] Screenshots of expected output saved
- [ ] Do a dry run of the demo
- [ ] Assign roles:
  - [ ] Demo Driver (speaks to judges)
  - [ ] Technical Lead (watches logs, explains architecture)
  - [ ] Box Expert (shows Box UI)
- [ ] Practice the flow once
- [ ] Set up demo environment:
  - [ ] Terminal 1: ngrok running
  - [ ] Terminal 2: Backend running
  - [ ] Terminal 3: Logs visible
  - [ ] Browser: Box account logged in
  - [ ] Email: Ready to send test email

### T+22h (Final Review)

- [ ] All tests passing: `pytest -v`
- [ ] Backend running smoothly
- [ ] ngrok tunnel active
- [ ] SendGrid webhook configured
- [ ] All team members ready
- [ ] Demo script memorized
- [ ] Fallback plans reviewed
- [ ] Get some rest!

### T+24h (DEMO TIME!)

- [ ] Follow DEMO_SCRIPT.md exactly
- [ ] Follow DEMO_CHECKLIST.md minute-by-minute
- [ ] Show judges what you built
- [ ] Answer questions with confidence
- [ ] Celebrate! 🎉

---

## Your Daily Checklist

### Morning (Before Event)

- [ ] `.env` file created with all 8 API keys:
  ```
  □ SENDGRID_API_KEY
  □ SENDGRID_VERIFY_TOKEN
  □ BOX_CLIENT_ID
  □ BOX_CLIENT_SECRET
  □ BOX_ENTERPRISE_ID
  □ BOX_DEVELOPER_TOKEN
  □ CEREBRAS_API_KEY
  □ SENDGRID_INBOUND_URL (ngrok)
  ```

- [ ] SendGrid configured:
  - [ ] Inbound parse webhook points to `https://your-ngrok-url.ngrok.app/webhooks/email`
  - [ ] Forwarding to `greenriver.hack.squad@gmail.com`

- [ ] All 3 team members:
  - [ ] Have `.env` file
  - [ ] Can clone and run repo locally
  - [ ] Have read their DOMAIN_*_SETUP.md
  - [ ] Know which domain they're building

### Daily (During Hackathon)

- [ ] Morning standup (10 min):
  - What did Person A accomplish?
  - What did Person B accomplish?
  - What did Person C accomplish?
  - Any blockers?

- [ ] Mid-day check-in (10 min):
  - Progress update
  - Anyone stuck?
  - Tests passing?

- [ ] Late afternoon check-in (10 min):
  - Ready to integrate?
  - Any last issues?

### Before Demo

- [ ] Run pre-demo checklist (from DEMO_CHECKLIST.md):
  - [ ] Backend running
  - [ ] Tests passing
  - [ ] ngrok active
  - [ ] SendGrid configured
  - [ ] Sample PDF ready
  - [ ] Team roles assigned
  - [ ] Demo script reviewed
  - [ ] Fallback screenshots saved

---

## Git Workflow (For You)

### Setting Up Git

```bash
# Initialize git (already done, but for reference)
git init
git config user.name "Mason"
git config user.email "masonsabin@gmail.com"
git remote add origin https://github.com/sabinMas/hackathon-skeleton.git
```

### Merging Domain PRs

**Process:**
1. Person A makes PR from `feature/domain-1-*`
2. You review (check Domain 1 tests pass)
3. Run: `pytest backend/domain_1_email/tests/ -v`
4. Merge into master
5. Repeat for Person B and C

**Commands:**
```bash
# Check for new branches
git branch -r

# Fetch latest
git fetch origin

# Merge branch into master
git checkout master
git merge feature/domain-1-email-ingestion

# If conflicts, resolve them:
# - Open conflicted files
# - Choose which version to keep
# - Run `git add file.py`
# - Run `git commit -m "Resolve merge conflict"`

# Run tests to verify
pytest -v
```

### If Merge Conflicts Happen

Most conflicts will be in `backend/main.py` when integrating domains.

**Solution:**
1. Open `backend/main.py`
2. Look for `<<<<<<<` and `>>>>>>>`
3. Keep both imports from both domains
4. Run `pytest -v` to verify
5. Commit with: `git commit -m "[shared] Resolve merge conflict: add Domain X imports"`

---

## Handling Blockers

### When Someone Is Stuck

**Check:**
1. Did they read their DOMAIN_*_SETUP.md?
2. Are they trying to implement something that's already done?
3. Do they have the right credentials in `.env`?
4. Can they run tests for their domain?

**Common Issues:**

| Issue | Solution |
|-------|----------|
| "My tests won't pass" | Make sure they implemented `async def` functions, not sync ones |
| "I don't know what to implement" | Point them to the TODO comments in their service.py |
| "API keys aren't working" | Check `.env` file is in right location with right values |
| "LLM call timing out" | Try backup provider (Groq if Cerebras down) |
| "Box isn't uploading files" | Check Box credentials and permissions |

### When Someone Finishes Early

**Options:**
1. Help other domains with tests
2. Optimize their code (performance)
3. Add error handling
4. Write better comments
5. Prepare demo materials

---

## Testing & Integration

### After Each Domain PR

```bash
# Pull latest
git pull origin master

# Run ALL tests
pytest -v

# If tests pass
echo "✅ All good!"

# If tests fail
pytest -v --tb=short  # Show what failed
# Fix the issue, ask the domain person for help
```

### Integration Testing (T+14h)

**Manual end-to-end test:**

```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Terminal 2: Start backend
uvicorn backend.main:app --reload

# Terminal 3: Watch logs
tail -f output.log  # or stdout

# Terminal 4: Send test email
# Use Gmail to send to greenriver.hack.squad@gmail.com
# Attach sample_invoice.pdf
# Subject: "Test Invoice"

# Watch logs - should see:
# ✅ Domain 1: IngestedDocument created
# ✅ Domain 2: ClassificationResult - invoice, 0.95 confidence
# ✅ Domain 3: File moved to /Invoices/2024/May/, task created
# ✅ Notifications sent

# Check Box
# File should be in /Invoices/2024/May/ with metadata
# Task should be created and assigned
# Slack should have notification
```

---

## Pre-Demo Walkthrough

### The Day Before (if you had one)

Do a full dry run:
1. Start ngrok
2. Start backend
3. Follow DEMO_SCRIPT.md exactly
4. Send a test email
5. Watch it process
6. Show judges the result
7. Time yourself (should be 4-5 minutes)

### Day Of (1 hour before)

**15-minute technical setup:**
- [ ] ngrok running
- [ ] Backend running and healthy
- [ ] Logs visible in terminal
- [ ] Box logged in
- [ ] Email client ready
- [ ] Sample PDF ready

**15-minute team prep:**
- [ ] Demo driver knows script
- [ ] Tech lead ready to explain
- [ ] Box expert ready to show
- [ ] Everyone knows what happens if things break

**30-minute dry run:**
- [ ] Walk through script once
- [ ] Send test email (practice)
- [ ] Show result
- [ ] Check timing
- [ ] Agree on fallback plan

---

## Demo Script Overview

**Duration:** 4-5 minutes

1. **Intro** (30 sec) - Explain the problem and solution
2. **Architecture** (45 sec) - Show SYSTEM_FLOW.md diagram
3. **Live Demo** (2 min) - Send email, show classification, show Box
4. **Close** (30 sec) - Explain impact, invite questions
5. **Q&A** (unlimited) - Answer judges' questions

See `DEMO_SCRIPT.md` for exact wording!

---

## Success Criteria

You've done your job when:

- [ ] All team members know their role
- [ ] `.env` file has all 8 API keys
- [ ] Backend runs locally without errors
- [ ] All 3 domains implement and test their code
- [ ] End-to-end flow works (email → classify → Box)
- [ ] Demo runs smoothly with no major issues
- [ ] Team is energized and confident
- [ ] Judges are impressed! 🏆

---

## If Things Go Wrong

**Remember:**
- ✅ It's a hackathon - nothing is perfect
- ✅ Judges know about last-minute bugs
- ✅ Having a working MVP and good architecture beats polish
- ✅ Your team working well together matters
- ✅ You've got FALLBACK_PLAN in DEMO_CHECKLIST.md

---

## Support

**Questions?**
1. Check TEAM_GUIDELINES.md (team rules)
2. Check CRISIS_RUNBOOK.md (common issues)
3. Read DEMO_CHECKLIST.md (fallback plans)
4. Ask the community on Slack/Discord

**Feeling overwhelmed?**
1. Take a break
2. Grab coffee
3. Remember: you're already winning (prepped, organized, ready)
4. You've got this! 💪

---

**You're the glue holding this team together. Great job preparing! 🚀**

Now go get those API keys and coordinate your team to build something amazing! 🎉
