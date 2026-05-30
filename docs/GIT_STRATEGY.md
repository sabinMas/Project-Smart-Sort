# Git Strategy & Workflow

## Branch Naming

**Format:** `feature/domain-<number>-<description>`

Examples:
```
feature/domain-1-email-webhook       # Person A
feature/domain-2-llm-router          # Person B
feature/domain-3-box-integration     # Person C
feature/shared-config-updates        # Shared code
bugfix/domain-1-signature-validation # Bug fix
```

## Commit Messages

**Format:** `[domain-X] Commit message`

Examples:
```
[domain-1] Add SendGrid webhook handler
[domain-2] Implement Cerebras LLM router with fallback to Groq
[domain-3] Create review task and assign to finance team
[shared] Add logging configuration
```

## Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/domain-1-email-webhook
# Push immediately to track progress
git push -u origin feature/domain-1-email-webhook
```

### 2. Work on Your Domain Only

```bash
# Only edit your domain files
# Domain 1 person:
backend/domain_1_email/routes.py
backend/domain_1_email/service.py
backend/domain_1_email/models.py
backend/domain_1_email/tests/

# Domain 2 person:
backend/domain_2_classifier/llm_router.py
backend/domain_2_classifier/service.py
backend/domain_2_classifier/tests/

# Domain 3 person:
backend/domain_3_box_integration/box_client.py
backend/domain_3_box_integration/service.py
backend/domain_3_box_integration/tests/
```

### 3. Test Your Domain

```bash
# Run only your domain tests
pytest domain_1_email/ -v      # Domain 1
pytest domain_2_classifier/ -v # Domain 2
pytest domain_3_box_integration/ -v  # Domain 3

# Check you didn't break anything
pytest -v  # All tests
```

### 4. Commit Frequently

```bash
git add domain_1_email/
git commit -m "[domain-1] Add email parsing logic"

git add domain_1_email/tests/
git commit -m "[domain-1] Add unit tests for email service"

# Push regularly
git push origin feature/domain-1-email-webhook
```

### 5. Create Pull Request

```bash
# GitHub CLI (recommended)
gh pr create \
  --title "[domain-1] Email webhook integration" \
  --body "Implements email ingestion via SendGrid webhook"

# Or manually on GitHub
# 1. Go to repo
# 2. Click "New Pull Request"
# 3. Compare feature/domain-1-* to main
# 4. Add description and submit
```

### 6. Review & Merge

**Code Review Checklist:**
- [ ] Only files from one domain modified
- [ ] Tests pass
- [ ] Commit messages follow convention
- [ ] No cross-domain imports
- [ ] Type contracts respected (types.py unchanged)

**Merge Process:**
```bash
# PO (Product Owner) merges
gh pr merge <PR_NUMBER> --squash  # Squash to one commit
# or
git merge feature/domain-1-email-webhook
git push origin main
```

---

## Key Rules

### ❌ DON'T

```bash
# Don't commit shared config changes
git add backend/shared/config.py  # Only PO can do this

# Don't modify types.py
git add backend/shared/types.py  # LOCKED after T+0

# Don't commit changes from other domains
git commit -m "[domain-1] Updated domain 3 service"  # NO!

# Don't merge without tests passing
git push feature/domain-1-*  # Tests must pass first

# Don't rebase onto main (creates conflicts)
git rebase origin/main  # NO! Just merge main → your branch
```

### ✅ DO

```bash
# Do commit your domain changes
git add domain_1_email/
git commit -m "[domain-1] Add email validation"

# Do test before pushing
pytest domain_1_email/ -v

# Do push regularly
git push origin feature/domain-1-*

# Do create PR for code review
gh pr create --title "[domain-1] ..." --body "..."

# Do merge main into your branch if needed
git fetch origin
git merge origin/main  # Safe, doesn't rewrite history
```

---

## Conflict Resolution

### If You Have a Merge Conflict

```bash
# Check which files conflict
git status

# Edit conflicting files
# Most likely: main.py (when integrating domains)

# After editing, mark as resolved
git add main.py

# Complete the merge
git commit -m "Resolve merge conflict: add domain imports"
```

### Typical Conflict: main.py

**Before Merge:**
```python
# Person A's version
from backend.domain_1_email import router as email_router
```

**After Merge (with conflict):**
```python
<<<<<<< HEAD
from backend.domain_1_email import router as email_router
from backend.domain_2_classifier.service import ClassificationService
=======
from backend.domain_1_email import router as email_router
from backend.domain_3_box_integration.service import BoxIntegrationService
>>>>>>> main
```

**Resolution (keep both):**
```python
from backend.domain_1_email import router as email_router
from backend.domain_2_classifier.service import ClassificationService
from backend.domain_3_box_integration.service import BoxIntegrationService
```

Then test:
```bash
pytest tests/test_integration.py -v
```

---

## Timeline

### T+0 (Start)
- [ ] Git repo initialized
- [ ] Main branch has skeleton
- [ ] Each person creates feature branch

### T+4h
- [ ] Domain 1: First PR with routes.py stub → implementation
- [ ] Domain 2: First PR with llm_router.py
- [ ] Domain 3: First PR with box_client.py

### T+8h
- [ ] Domain 1: Service tests passing
- [ ] Domain 2: Classification working
- [ ] Domain 3: Box integration working
- [ ] PO: Starting to integrate domains in main.py

### T+16h
- [ ] All 3 domains complete
- [ ] Integration tests passing
- [ ] PO: main.py orchestration done

### T+20h
- [ ] Demo-ready
- [ ] All tests passing
- [ ] 5 sample documents tested

### T+24h
- [ ] Live demo or video submission
- [ ] Final commit tagged

---

## Common Git Commands

```bash
# Check current branch
git branch

# Switch branch
git checkout feature/domain-1-email

# Pull latest changes
git pull origin main

# Check status
git status

# Stage changes
git add domain_1_email/

# Commit
git commit -m "[domain-1] Add webhook handler"

# Push
git push origin feature/domain-1-email

# View recent commits
git log --oneline -5

# View what changed
git diff

# View what you'll commit
git diff --staged

# Undo unstaged changes
git checkout -- domain_1_email/routes.py

# Undo staged changes
git reset HEAD domain_1_email/routes.py

# View branch details
git show feature/domain-1-email
```

---

## Team Communication

Use Discord/Slack channels for:

```
#domain-1-email       → Person A updates
#domain-2-classifier  → Person B updates
#domain-3-box         → Person C updates
#general              → Blockers, merge requests
#crisis               → Critical issues
```

Example message:
```
@team-pocs My domain tests are all passing! 
Ready to merge feature/domain-1-email-webhook
```

---

For more details, see:
- [Team Guidelines](../TEAM_GUIDELINES.md)
- [Architecture](ARCHITECTURE.md)
- [Crisis Runbook](CRISIS_RUNBOOK.md)
