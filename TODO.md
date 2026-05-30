# Project Smart Sort - TODO & Bug Fix List

## 🔴 CRITICAL DOMAIN 3 BUGS - FIX IMMEDIATELY

### Task #3: Fix Missing `await` on Box SDK API Calls
**File:** `backend/domain_3_box_integration/box_client.py`
**Lines:** 93, 130, 214, 233, 262, 306, 331, 365, 380
**Severity:** CRITICAL
**Impact:** Event loop blocks on synchronous API calls; entire system becomes unresponsive under load
**Effort:** 2-3 hours
**Status:** ⏳ TODO

**Problem:**
Box SDK API calls are made synchronously inside async methods, blocking the event loop.

**Solution:**
Use `asyncio.to_thread()` or thread pool executor to run sync calls in background:
```python
# Instead of:
uploaded_file = self.client.uploads.upload_file(...)

# Use:
uploaded_file = await asyncio.to_thread(self.client.uploads.upload_file, ...)
```

**Methods to fix:**
- `upload_file()` - line 93
- `move_file()` - line 130
- `get_folder_items()` - line 214
- `create_folder()` - lines 233, 262
- `apply_metadata()` - line 306
- `delete_file()` - line 331
- `get_file_metadata()` - line 365
- `list_documents()` - line 380

---

### Task #4: Fix SQL Parameter Index Off-by-One in Approval Service
**File:** `backend/domain_3_box_integration/approval_service.py`
**Lines:** 576-583
**Severity:** CRITICAL
**Impact:** Pagination queries fail or return wrong results
**Effort:** 1-2 hours
**Status:** ⏳ TODO

**Problem:**
The `param_idx` counter is not incremented after building WHERE conditions, but then used for LIMIT/OFFSET placeholders. This causes incorrect SQL parameter binding.

**Solution:**
Track parameter count correctly:
```python
# After building WHERE conditions (around line 570)
# Need to update param_idx to reflect number of params

# Then use correct indices for pagination:
param_idx = len(params) + 1
query += f" LIMIT ${param_idx} OFFSET ${param_idx + 1}"
params.extend([limit, offset])
```

---

### Task #5: Fix UUID Validation on Document IDs
**File:** `backend/domain_3_box_integration/approval_service.py`
**Lines:** 97-98, 115, 147, 235
**Severity:** HIGH
**Impact:** Invalid document IDs crash API instead of returning proper 400 error
**Effort:** 1 hour
**Status:** ⏳ TODO

**Problem:**
Document IDs are converted to UUID without validation. Invalid UUIDs raise unhandled ValueError.

**Solution:**
```python
from fastapi import HTTPException

try:
    document_id_uuid = uuid.UUID(document_id)
except ValueError:
    raise HTTPException(
        status_code=400,
        detail=f"Invalid document ID format. Expected UUID, got: {document_id}"
    )
```

**Methods to fix:**
- `review_document()` - line 97
- `get_approval_history()` - line 115
- `approve_document()` - line 147
- `reject_document()` - line 235

---

## 🟠 HIGH SEVERITY DOMAIN 3 BUGS

### Task #6: Fix Metadata Application Not Being Executed
**File:** `backend/domain_3_box_integration/metadata.py`
**Lines:** 18-49
**Severity:** HIGH
**Impact:** Classification metadata never reaches Box files; files never get organized
**Effort:** 1-2 hours
**Status:** ⏳ TODO

**Problem:**
The `apply_metadata()` method only validates but doesn't actually call BoxClient to apply metadata.

**Current Code:**
```python
def apply_metadata(self, document_id: str, classification: dict) -> bool:
    # ... validation code ...
    return True  # Returns success without doing anything!
```

**Solution:**
Actually call the Box API after validation:
```python
def apply_metadata(self, document_id: str, classification: dict) -> bool:
    # ... validation code ...
    
    try:
        self.box_client.apply_metadata(document_id, classification)
        return True
    except Exception as e:
        logger.error(f"Failed to apply metadata: {e}")
        return False
```

---

### Task #7: Fix Silent Exception Swallowing in _find_folder
**File:** `backend/domain_3_box_integration/box_client.py`
**Lines:** 219-220
**Severity:** HIGH
**Impact:** Auth failures hidden; system creates duplicate folders instead of surfacing errors
**Effort:** 1 hour
**Status:** ⏳ TODO

**Problem:**
`_find_folder()` catches all exceptions and returns None, hiding authentication failures and API errors.

**Solution:**
Only catch specific, expected exceptions:
```python
try:
    items = self.client.folders.get_folder_items(...)
    return items
except BoxException as e:
    if "folder not found" in str(e).lower():
        return None
    else:
        logger.error(f"Box API error finding folder: {e}")
        raise
except Exception as e:
    logger.error(f"Unexpected error finding folder: {e}")
    raise
```

---

### Task #8: Fix Race Condition in Concurrent Folder Creation
**File:** `backend/domain_3_box_integration/box_client.py`
**Lines:** 240-246
**Severity:** MEDIUM
**Impact:** Concurrent requests may fail unnecessarily even if folder was created
**Effort:** 2 hours
**Status:** ⏳ TODO

**Problem:**
When two concurrent requests try to create the same folder, if `_find_folder()` fails, the original exception is re-raised instead of handling the race condition properly.

**Solution:**
Add retry logic with exponential backoff:
```python
try:
    folder = await self.client.folders.create_folder(...)
except Exception as e:
    if "already exists" in str(e):
        for attempt in range(3):
            try:
                existing = await self._find_folder(...)
                if existing:
                    return existing
            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(0.1 * (2 ** attempt))
    raise
```

---

## 🟡 MEDIUM SEVERITY DOMAIN 3 BUGS

### Task #9: Remove Double Metadata Application Attempt
**File:** `backend/domain_3_box_integration/service.py`
**Lines:** 177-183
**Severity:** MEDIUM
**Impact:** Redundant API calls; potential data inconsistency
**Effort:** 30 minutes
**Status:** ⏳ TODO

**Problem:**
`_apply_metadata()` calls both `metadata_manager.apply_metadata()` AND `box_client.apply_metadata()`, causing redundant API calls.

**Solution:**
Choose one approach (recommended: use box_client only):
```python
async def _apply_metadata(self, document_id: str, classification: dict) -> bool:
    return await self.box_client.apply_metadata(document_id, classification)
```

---

### Task #10: Fix Dict Type Casting Without Null Check
**File:** `backend/domain_3_box_integration/approval_service.py`
**Line:** 149
**Severity:** LOW
**Impact:** Edge case that breaks if database schema changes
**Effort:** 30 minutes
**Status:** ⏳ TODO

**Problem:**
`[dict(row) for row in rows]` assumes all rows are dict-convertible.

**Solution:**
```python
rows = await self.db_connection.fetch(query, *params)
result = []
for row in rows:
    try:
        result.append(dict(row))
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to convert row to dict: {e}, row type: {type(row)}")
        raise
return result
```

---

## 🟢 LOW SEVERITY DOMAIN 3 BUGS

### Task #11: Fix Unvalidated Box File URL Construction
**File:** `backend/domain_3_box_integration/notifications.py`
**Line:** 201
**Severity:** LOW
**Impact:** Malformed URLs in Slack messages
**Effort:** 30 minutes
**Status:** ⏳ TODO

**Solution:**
```python
from urllib.parse import quote

try:
    uuid.UUID(document_id)
except ValueError:
    document_id = "unknown"

file_url = f"https://app.box.com/file/{quote(document_id, safe='')}"
```

---

### Task #12: Add Error Context to Validation Responses
**File:** `backend/domain_3_box_integration/routes.py`
**Line:** 75
**Severity:** LOW
**Impact:** UX/debugging improvement
**Effort:** 30 minutes
**Status:** ⏳ TODO

**Solution:**
```python
if not request.recipients:
    raise HTTPException(
        status_code=400,
        detail={
            "error": "Recipients cannot be empty",
            "field": "recipients",
            "hint": "Provide at least one recipient email or user ID"
        }
    )
```

---

## 🔐 REAL-WORLD SETUP TASKS (Handled by User)

### ✅ COMPLETED
- [x] Cerebras API key configured
- [x] SendGrid API configured for Domain 1
- [x] Requirements.txt updated with all dependencies

### ⏳ IN PROGRESS (User handling)
- [ ] Box API credentials and enterprise configuration
- [ ] PostgreSQL database setup and migrations
- [ ] Slack webhook configuration

### 🔄 TODO (After core features working)
- [ ] HTTPS/TLS certificates for production
- [ ] Environment variables for staging/production
- [ ] Monitoring, logging, and alerting infrastructure
- [ ] CI/CD pipeline configuration
- [ ] Security audit and penetration testing

---

## 📊 SUMMARY

**Total Bugs Found:** 18
- Critical: 4
- High: 5
- Medium: 6
- Low: 3

**Domain 3 Code Fixes Required:** 10 tasks
**Total Effort:** 10-14 hours

**Real-World Setup Tasks:** 10 tasks
**Total Effort:** 20-40 hours (user handling)

---

## 🎯 RECOMMENDED FIX ORDER

1. **Week 1 (Critical):** Tasks #3, #4, #5, #6 (4-8 hours)
2. **Week 1 (High):** Tasks #7, #8 (3 hours)
3. **Week 2 (Medium/Low):** Tasks #9, #10, #11, #12 (2-3 hours)

---

## ✅ TESTING CHECKLIST

After fixing bugs, verify:
- [ ] All 13 Domain 2 classification tests pass
- [ ] Domain 3 routes return proper error codes
- [ ] Box file uploads and metadata application work end-to-end
- [ ] Email ingestion receives messages and classifies them
- [ ] Slack notifications are sent on document processing
- [ ] Concurrent requests don't cause race conditions
- [ ] SQL pagination queries return correct results
- [ ] Invalid UUID document IDs return 400 (not 500)
- [ ] Folder creation doesn't create duplicates
- [ ] System stays responsive under load (test with concurrent requests)

---

**Last Updated:** 2026-05-29
**Generated by:** Comprehensive Code Review
