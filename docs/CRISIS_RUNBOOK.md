# Crisis Runbook

Quick troubleshooting guide for common hackathon issues.

## LLM API Issues

### Problem: Cerebras API timeout
**Symptoms:** Requests timeout after 30 seconds, classification fails

**Solution:**
1. Check Cerebras API status
2. Switch to fallback provider in `.env`:
   ```bash
   LLM_PROVIDER=groq  # Try Groq instead
   ```
3. Restart the server
4. Re-test classification

**Fallback Order:**
1. Cerebras (primary)
2. Groq (fast, reliable)
3. Gemini (last resort)

### Problem: Invalid LLM response
**Symptoms:** "Failed to parse JSON response from LLM"

**Solution:**
1. Check that LLM response is valid JSON
2. Verify prompt is not too long (truncates at 10k chars)
3. Add logging to `domain_2_classifier/service.py`:
   ```python
   logger.error(f"LLM response: {response}")
   ```
4. Check LLM API logs for errors

### Problem: Confidence score validation fails
**Symptoms:** "Confidence must be between 0.0 and 1.0"

**Solution:**
1. LLM is returning invalid confidence (>1.0 or <0.0)
2. Add validation in prompt:
   ```
   "confidence": 0.95  # Must be decimal between 0 and 1
   ```
3. Add post-processing in `_parse_llm_response()`:
   ```python
   confidence = min(1.0, max(0.0, confidence))
   ```

---

## Box Integration Issues

### Problem: Box authentication fails
**Symptoms:** "BoxAuthenticationError" during startup

**Solution:**
1. Verify Box credentials in `.env`:
   ```bash
   BOX_CLIENT_ID=your_actual_client_id
   BOX_CLIENT_SECRET=your_actual_secret
   BOX_ENTERPRISE_ID=your_enterprise_id
   ```
2. Check Box app is enabled in admin console
3. Regenerate OAuth token if needed
4. Test connection:
   ```python
   from backend.domain_3_box_integration.box_client import BoxClient
   client = BoxClient()  # Should not raise error
   ```

### Problem: File upload fails
**Symptoms:** "BoxUploadError" when moving file to Box

**Solution:**
1. Check folder ID exists:
   ```bash
   # Verify BOX_DEMO_FOLDER_ID in .env
   ```
2. Verify file permissions:
   - User must have write access to folder
   - Check enterprise settings
3. Check file size not exceeding Box limit
4. Enable logging to see full error:
   ```python
   logger.error(f"Box API error: {e}", exc_info=True)
   ```

### Problem: Metadata application fails
**Symptoms:** "MetadataApplicationError" after file upload

**Solution:**
1. Check metadata template exists in Box:
   ```
   box_smart_inbox_metadata
   ```
2. Verify metadata fields match template schema
3. Skip metadata if template missing (for hackathon):
   ```python
   try:
       await metadata_manager.apply_metadata(...)
   except MetadataApplicationError:
       logger.warning("Metadata application failed, continuing...")
   ```

---

## Email Webhook Issues

### Problem: SendGrid webhook not receiving events
**Symptoms:** No emails being processed, POST to /webhooks/email never called

**Solution:**
1. Check ngrok tunnel is running:
   ```bash
   ngrok http 8000
   # Should show: Forwarding https://xxx.ngrok.app -> http://localhost:8000
   ```
2. Update ngrok URL in SendGrid dashboard:
   ```
   Webhook URL: https://xxx.ngrok.app/webhooks/email
   ```
3. Verify callback URL in `.env`:
   ```bash
   SENDGRID_INBOUND_URL=https://xxx.ngrok.app/webhooks/email
   ```
4. Test webhook manually:
   ```bash
   curl -X POST http://localhost:8000/webhooks/email \
     -H "Content-Type: application/json" \
     -d '{"from":"test@example.com","subject":"Test"}'
   ```

### Problem: Signature validation fails
**Symptoms:** "Invalid SendGrid signature" errors

**Solution:**
1. Verify SENDGRID_VERIFY_TOKEN in `.env`:
   ```bash
   SENDGRID_VERIFY_TOKEN=your_actual_token
   ```
2. For testing, disable signature validation temporarily:
   ```python
   # In domain_1_email/routes.py
   # TODO: Remove before production!
   # if Config.DEMO_MODE:
   #     return process_email(...)  # Skip validation
   ```
3. Check SendGrid event documentation for correct algorithm

---

## Git & Merge Conflicts

### Problem: Merge conflict in main.py
**Symptoms:** "Conflict: both branches added imports"

**Solution:**
1. Just add both domain imports:
   ```python
   # Keep all three:
   from backend.domain_1_email import router as email_router
   from backend.domain_2_classifier.service import ClassificationService
   from backend.domain_3_box_integration.service import BoxIntegrationService
   ```
2. Run tests to verify:
   ```bash
   pytest tests/test_integration.py -v
   ```
3. Commit the merge:
   ```bash
   git add main.py
   git commit -m "Merge: resolve main.py domain imports"
   ```

### Problem: Accidentally committed to main branch
**Symptoms:** Code merged without going through feature branch

**Solution:**
1. Revert the commit (if safe):
   ```bash
   git revert <commit-hash>
   git push origin main
   ```
2. Or create proper PR after the fact:
   ```bash
   git log main --oneline  # Find the commit
   git checkout -b hotfix/email-domain
   # Make proper changes and PR
   ```

---

## Testing & Debugging

### Problem: Tests are failing but unclear why
**Symptoms:** "FAILED test_classify_invoice - AssertionError"

**Solution:**
1. Run with verbose output:
   ```bash
   pytest domain_2_classifier/tests/ -vv -s
   ```
2. Use print debugging:
   ```python
   def test_something():
       result = service.classify(doc)
       print(f"Result: {result}")  # -s flag shows print
       assert result.doc_type == "invoice"
   ```
3. Check fixtures are correct:
   ```bash
   pytest domain_2_classifier/tests/test_service.py::TestClassificationService::test_classify_invoice -vv
   ```

### Problem: Service initialization fails
**Symptoms:** "RuntimeError: Box client not initialized"

**Solution:**
1. Check all required env vars are set:
   ```bash
   echo $BOX_CLIENT_ID
   echo $CEREBRAS_API_KEY
   # Should print values, not empty
   ```
2. Verify .env is loaded:
   ```python
   from backend.shared.config import Config
   print(Config.BOX_CLIENT_ID)  # Should print, not raise
   ```
3. Load .env before running:
   ```bash
   export $(cat .env | xargs)
   python -m pytest
   ```

---

## Docker Issues

### Problem: Docker build fails
**Symptoms:** "ERROR: failed to build image" or "pip install failed"

**Solution:**
1. Clear Docker cache:
   ```bash
   docker-compose down
   docker system prune -a
   docker-compose build --no-cache
   ```
2. Check requirements.txt has valid packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Use Python 3.11 or 3.12:
   ```dockerfile
   FROM python:3.11-slim  # Ensure this line in Dockerfile
   ```

### Problem: Container exits immediately
**Symptoms:** `docker-compose logs fastapi` shows error and exits

**Solution:**
1. Check logs:
   ```bash
   docker-compose logs fastapi -n 50
   ```
2. Run container interactively:
   ```bash
   docker-compose run fastapi bash
   python -m backend.main
   ```
3. Verify all env vars are set in .env file

---

## Performance Issues

### Problem: Document processing is slow
**Symptoms:** Requests taking >5 seconds

**Solution:**
1. Profile which domain is slow:
   - Add logging with timestamps:
   ```python
   import time
   start = time.time()
   result = await classification_service.classify(doc)
   logger.info(f"Classification took {time.time() - start:.2f}s")
   ```
2. If Domain 1 slow: Email extraction is slow (OCR?)
3. If Domain 2 slow: LLM API is slow, switch provider
4. If Domain 3 slow: Box API is slow, check network

### Problem: Memory usage growing
**Symptoms:** Server running out of memory

**Solution:**
1. Check for memory leaks in services:
   ```python
   # Don't store all documents in memory
   documents_processed = []  # This grows unbounded!
   # Solution: Use database or Redis
   ```
2. Clear old fixtures:
   ```python
   import gc
   gc.collect()  # Force garbage collection
   ```
3. Use async/await properly:
   ```python
   async def process():  # Not def
       await expensive_operation()  # Yield control
   ```

---

## Quick Fixes Checklist

When in crisis, try these in order:

- [ ] Restart the server: `docker-compose restart fastapi`
- [ ] Check logs: `docker-compose logs -f`
- [ ] Switch LLM provider: `LLM_PROVIDER=groq` in .env
- [ ] Clear cache: `docker-compose down && docker-compose up --build`
- [ ] Check env vars: `cat .env | grep -E "API_KEY|SECRET"`
- [ ] Run tests: `pytest -v`
- [ ] Check Git status: `git status` (unstaged changes?)
- [ ] Ask for help in Discord/Slack with error message

---

## Getting Help

1. **Check this runbook first** for your specific error
2. **Review TEAM_GUIDELINES.md** for architecture
3. **Look at AGENT_DOMAIN_*.md** for domain-specific help
4. **Search error message** in repo issues
5. **Ask team members** who worked on that domain
6. **Check git log** for similar fixes

---

Good luck! You've got this. 🚀
