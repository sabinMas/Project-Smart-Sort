# Design Document

## Overview

This feature delivers three changes, all scoped to **Domain 3** to keep the merge-conflict surface minimal while teammates work concurrently on Domain 1 (email) and Domain 2 (classifier):

1. **Slack enrichment** — enrich the *existing* `NotificationManager._build_slack_message()` / `_send_slack_notification()` / `send_notifications()` path (which already uses `httpx`) so an optional `metadata` dict flows through and produces a richer payload, with an urgent variant for high-value invoices.
2. **POST /tasks/create** — add a new FastAPI endpoint to `domain_3_box_integration/routes.py` that delegates to the existing `TaskManager.create_review_task()`. The frontend `TaskAssignment` component already calls this endpoint, so this closes an existing gap.
3. **WorkflowStatus UI** — add a new `WorkflowStatus.tsx` component (+ CSS) that derives six pipeline stages from `processingResult`, and surgically swap the inline "Processing Status" block in `App.tsx` for `<WorkflowStatus />`.

### Design Principles (merge-conflict minimization)

- **No new top-level functions where an existing one can be enriched.** We do **not** add a `notify_slack()` helper (the stale `TEAM_TASKS.md` suggestion using `aiohttp` is rejected). We extend the existing `httpx`-based methods in place.
- **Additive, optional parameters only.** Every new parameter on existing methods defaults to `None`, so existing call sites (including `service.py`) compile and behave identically without modification.
- **Touch only Domain 3 files.** Backend: `notifications.py`, `routes.py`, `models.py`. Frontend: `App.tsx` (one surgical swap) plus two brand-new files `components/WorkflowStatus.tsx` and `styles/WorkflowStatus.css`.
- **Reuse working paths.** `TaskManager.create_review_task()`, `BoxClient`, and the demo/live mode gating already work; we build on them rather than re-implementing.

### Languages

- Backend: Python 3 (FastAPI, Pydantic, `httpx`).
- Frontend: TypeScript + React (Vite).

---

## Architecture

```
┌─────────────────────── Frontend (box-extension) ───────────────────────┐
│  App.tsx                                                                │
│   └─ <WorkflowStatus processingResult={processingResult} />  (NEW swap) │
│        └─ deriveStages(processingResult) -> Stage[6]  (pure fn)         │
│        └─ styles/WorkflowStatus.css                   (NEW)             │
│  TaskAssignment.tsx  ──POST /tasks/create──┐  (already calls endpoint)  │
└────────────────────────────────────────────┼──────────────────────────┘
                                              │
┌──────────────────────── Backend (Domain 3) ─┼──────────────────────────┐
│  routes.py                                   ▼                          │
│   └─ POST /tasks/create  (NEW)                                          │
│        └─ TaskManager.create_review_task(file_id, doc_type, ...)        │
│                                                                         │
│  notifications.py  (ENRICHED, not rewritten)                           │
│   send_notifications(..., metadata?)                                    │
│     └─ _send_slack_notification(..., metadata?)                         │
│          └─ _build_slack_message(..., metadata?)  -> enriched payload   │
│               └─ httpx POST (live) | log + return True (demo)           │
└─────────────────────────────────────────────────────────────────────── ┘
```

---

## Components and Interfaces

### 1. Slack Enrichment (`notifications.py`)

The optional `metadata` dict threads through three existing methods. All new parameters default to `None`, preserving current callers.

```python
async def send_notifications(
    self,
    document_id: str,
    doc_type: str,
    assigned_to_email: str,
    channels: Optional[List[str]] = None,
    metadata: Optional[dict] = None,        # NEW (Req 1.10)
) -> List[str]:
    ...
    success = await self._send_slack_notification(
        document_id, doc_type, assigned_to_email, metadata=metadata   # forward
    )
```

```python
async def _send_slack_notification(
    self,
    document_id: str,
    doc_type: str,
    assigned_to_email: str,
    metadata: Optional[dict] = None,        # NEW (Req 1.9)
) -> bool:
    webhook_url = Config.SLACK_WEBHOOK_URL
    message = self._build_slack_message(document_id, doc_type, assigned_to_email, metadata)

    # Demo gate UNCHANGED: log enriched payload, return True, no HTTP (Req 1.11)
    if Config.DEMO_MODE or not webhook_url:
        logger.info(f"[DEMO] Slack payload for {document_id}: {message}")
        return True

    # Live path UNCHANGED: httpx POST of the enriched payload (Req 1.12)
    ...
```

#### `_build_slack_message()` enrichment logic

This is the pure core. It is a deterministic function of `(document_id, doc_type, assigned_to_email, metadata)`.

```python
def _build_slack_message(
    self,
    document_id: str,
    doc_type: str,
    assigned_to_email: str,
    metadata: Optional[dict] = None,        # NEW (Req 1.1)
) -> dict:
    meta = metadata or {}

    # Button URL: prefer box_file_id, fall back to document_id (Req 1.5, 1.6)
    box_file_id = meta.get("box_file_id") or document_id
    button_url = f"https://app.box.com/file/{box_file_id}"

    # Urgency decision (Req 1.7, 1.8)
    amount = meta.get("amount")
    is_urgent = doc_type == "invoice" and amount is not None and amount > 10000
    emoji = "🚨" if is_urgent else "📄"
    button_style = "danger" if is_urgent else "primary"

    # Body lines: only include enrichment fields that are present (Req 1.2-1.4, 1.6)
    lines = [
        f"*New {doc_type.replace('_', ' ').title()} for Review*",
        f"Document ID: `{document_id}`",
        f"Assigned to: {assigned_to_email}",
    ]
    if "confidence" in meta:
        lines.append(f"Confidence: {self._format_percent(meta['confidence'])}")
    if "vendor" in meta:
        lines.append(f"Vendor: {meta['vendor']}")
    if "amount" in meta:
        lines.append(f"Amount: {self._format_currency(meta['amount'])}")

    button = {
        "type": "button",
        "text": {"type": "plain_text", "text": "Review in Box"},
        "url": button_url,
    }
    if is_urgent:
        button["style"] = button_style   # Slack only honors primary/danger

    return {
        "text": f"{emoji} New {doc_type} document for review",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": "\n".join(lines)}},
            {"type": "actions", "elements": [button]},
        ],
    }
```

#### Formatting helpers (private, pure)

```python
@staticmethod
def _format_percent(confidence) -> str:
    # confidence is a 0.0-1.0 float -> "96%"
    return f"{round(float(confidence) * 100)}%"

@staticmethod
def _format_currency(amount) -> str:
    # numeric -> "$15,500.00"
    return f"${float(amount):,.2f}"
```

**Formatting rules**
- *Confidence*: stored as a `0.0–1.0` float (per `ClassificationResult.confidence`); multiply by 100 and render as an integer percentage with a `%` suffix.
- *Amount*: render with a `$` prefix, thousands separators, and two decimals.
- Helpers coerce via `float()` so ints or numeric strings are tolerated; non-numeric values are guarded at the call site by the `in meta` checks and try/except is unnecessary because metadata originates from `extracted_fields`.

**Variant decision table (Req 1.7 / 1.8)**

| doc_type   | amount        | Variant  | Emoji | Button style |
|------------|---------------|----------|-------|--------------|
| invoice    | > 10000       | urgent   | 🚨    | danger       |
| invoice    | ≤ 10000       | standard | 📄    | primary      |
| invoice    | missing       | standard | 📄    | primary      |
| non-invoice| any           | standard | 📄    | primary      |

### 2. POST /tasks/create (`routes.py` + `models.py`)

**New Pydantic models** appended to `models.py` (no edits to existing models):

```python
class CreateTaskRequest(BaseModel):
    """Request body for POST /tasks/create."""
    file_id: str
    assigned_to: EmailStr
    due_date: Optional[str] = None
    message: Optional[str] = None


class CreateTaskResponse(BaseModel):
    """Response for POST /tasks/create."""
    task_id: str
    status: str
```

**New route** appended to `routes.py`, reusing the module-level pattern. It needs a `TaskManager`, which requires a `BoxClient`:

```python
from .models import CreateTaskRequest, CreateTaskResponse
from .tasks import TaskManager
from .box_client import BoxClient

_task_manager = TaskManager(BoxClient())

@router.post("/tasks/create", response_model=CreateTaskResponse, tags=["tasks"])
async def create_task(request: CreateTaskRequest) -> CreateTaskResponse:
    """Create and assign a Box review task from the extension sidebar."""
    try:
        task_id = await _task_manager.create_review_task(
            file_id=request.file_id,
            doc_type="document",            # generic; sidebar tasks are ad-hoc
            assigned_to_email=str(request.assigned_to),
            due_date=request.due_date,
        )
        return CreateTaskResponse(task_id=task_id, status="created")
    except Exception as e:
        logger.error(f"Error creating task for file {request.file_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Error handling**
- Missing/invalid `file_id` or `assigned_to` (e.g. malformed email) → FastAPI returns **422** automatically from Pydantic validation (Req 2.7). No custom handling needed.
- `create_review_task()` raising (e.g. `TaskCreationError`) → caught and re-raised as **500** with the exception message in `detail` (Req 2.6).
- Happy path → **200** with `{task_id, status: "created"}` (Req 2.5).

The endpoint path (`/tasks/create`) and request shape (`file_id`, `assigned_to`, `due_date`, `message`) exactly match the existing `TaskAssignment.tsx` fetch call, so no frontend change is required for Domain 2's endpoint to work.

### 3. WorkflowStatus Component (frontend)

**New file:** `box-extension/src/components/WorkflowStatus.tsx`
**New file:** `box-extension/src/styles/WorkflowStatus.css`

#### Stage model

```typescript
type StageState = 'completed' | 'pending' | 'error';

interface Stage {
  label: string;
  state: StageState;
}

const STAGE_LABELS = [
  'Received',
  'Classified',
  'Routed',
  'Task Created',
  'Notified',
  'Complete',
] as const;   // exactly six, fixed order (Req 3.2)
```

`ProcessingResult` is co-located by re-declaring the same interface already present in `App.tsx` (kept local to avoid touching shared type files; the shape matches `ProcessingResult` in `App.tsx`).

#### Derivation logic (pure function)

```typescript
export function deriveStages(pr: ProcessingResult): Stage[] {
  // success => every stage completed (Req 3.3)
  if (pr.status === 'success') {
    return STAGE_LABELS.map((label) => ({ label, state: 'completed' as StageState }));
  }

  // failure => mark the failure point as error, earlier stages completed,
  // later stages pending (Req 3.6)
  if (pr.status === 'failure') {
    const failIndex = failurePointIndex(pr);
    return STAGE_LABELS.map((label, i) => ({
      label,
      state: i < failIndex ? 'completed' : i === failIndex ? 'error' : 'pending',
    }));
  }

  // in-progress / escalated => derive per-stage from available fields,
  // enforcing monotonicity (once pending, all later stages pending)
  // Received + Classified + Routed are implied complete once we have a result.
  const taskDone = pr.task_id != null;                       // Req 3.4
  const notifiedDone = pr.notification_sent_to.length > 0;    // Req 3.5
  const states = [
    'completed',                                  // Received
    'completed',                                  // Classified
    pr.destination_folder ? 'completed' : 'pending', // Routed
    taskDone ? 'completed' : 'pending',           // Task Created
    taskDone && notifiedDone ? 'completed' : 'pending', // Notified
    'pending',                                    // Complete (only success completes it)
  ] as StageState[];
  return enforceMonotonic(STAGE_LABELS, states);
}
```

`enforceMonotonic` walks left-to-right; after the first non-`completed` stage, every later stage is forced to `pending` (Req 3.4 "all subsequent stages pending"). `failurePointIndex` chooses the first stage whose precondition is unmet (no destination → Routed; no task_id → Task Created; empty notifications → Notified; otherwise Complete).

#### Rendering

```tsx
export const WorkflowStatus: React.FC<{ processingResult: ProcessingResult }> = ({ processingResult }) => {
  const stages = deriveStages(processingResult);
  return (
    <div className="workflow-status">
      <h3>Processing Status</h3>
      <ol className="workflow-stages">
        {stages.map((s) => (
          <li key={s.label} className={`stage stage-${s.state}`}>
            <span className="stage-icon" aria-hidden="true">
              {s.state === 'completed' ? '✓' : s.state === 'error' ? '✕' : '○'}
            </span>
            <span className="stage-label">{s.label}</span>
          </li>
        ))}
      </ol>
      {processingResult.status === 'failure' && processingResult.error_message && (
        <p className="workflow-error">{processingResult.error_message}</p>
      )}
    </div>
  );
};
```

CSS classes (Req 3.7): `.stage-completed`, `.stage-pending`, `.stage-error` provide the distinct visual states (color + icon), with `.workflow-error` styling the failure message. Accessibility: each stage carries its state via class and a visible icon; the icon is `aria-hidden` and the label text conveys meaning.

#### App.tsx integration (surgical swap)

The only change to the shared-ish `App.tsx` is replacing the inline `<div className="processing-result">…</div>` block with the component, preserving the existing `{processingResult && (...)}` null-guard (Req 3.8, 3.9):

```tsx
import { WorkflowStatus } from './components/WorkflowStatus';
// ...
{processingResult && <WorkflowStatus processingResult={processingResult} />}
```

No other lines in `App.tsx` change. The local `ProcessingResult` interface stays in `App.tsx` and is mirrored in the component file.

---

## Data Models

| Model | Location | Fields |
|-------|----------|--------|
| `CreateTaskRequest` | `models.py` (new) | `file_id: str`, `assigned_to: EmailStr`, `due_date: Optional[str]=None`, `message: Optional[str]=None` |
| `CreateTaskResponse` | `models.py` (new) | `task_id: str`, `status: str` |
| `metadata` dict | runtime arg | keys (all optional): `confidence: float`, `vendor: str`, `amount: number`, `box_file_id: str` |
| `Stage` | `WorkflowStatus.tsx` (new) | `label: string`, `state: 'completed' \| 'pending' \| 'error'` |

The `metadata` dict is sourced from `ClassificationResult.extracted_fields` plus `box_file_id`; callers may pass it, but every consumer treats it as fully optional.

---

## Error Handling

| Surface | Condition | Behavior |
|---------|-----------|----------|
| `_build_slack_message` | missing enrichment keys | Omit those lines; never raise (Req 1.6) |
| `_send_slack_notification` | demo mode / no webhook | Log payload, return `True`, no HTTP (Req 1.11) |
| `_send_slack_notification` | live HTTP non-200 / timeout / exception | Log error, return `False` (unchanged existing behavior) |
| `send_notifications` | one channel fails | Logged per-channel; other channels still attempted (unchanged) |
| `POST /tasks/create` | invalid body | 422 via Pydantic (Req 2.7) |
| `POST /tasks/create` | task creation raises | 500 with detail message (Req 2.6) |
| `WorkflowStatus` | `processingResult` null | Not rendered (guarded in `App.tsx`, Req 3.9) |
| `WorkflowStatus` | `status === 'failure'` | Failure stage shown as error + `error_message` rendered (Req 3.6) |

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Enrichment fields are rendered when present

For any `metadata` dict containing any subset of `confidence`, `vendor`, and `amount`, the body text of the message produced by `_build_slack_message()` includes each present field — confidence formatted as a percentage, amount formatted as currency, vendor verbatim — and omits the line for any key that is absent.

**Validates: Requirements 1.2, 1.3, 1.4, 1.6**

### Property 2: Urgency variant is determined by doc_type and amount

For any `doc_type` and any `amount`, `_build_slack_message()` renders the urgent variant (🚨 text emoji and `danger` button style) if and only if `doc_type == "invoice"` and `amount` is present and greater than 10000; otherwise it renders the standard variant (📄 emoji, no danger style).

**Validates: Requirements 1.7, 1.8**

### Property 3: Button URL resolution

For any `document_id` and any `metadata`, the action button URL equals `https://app.box.com/file/{box_file_id}` when `metadata` contains a `box_file_id`, and falls back to `https://app.box.com/file/{document_id}` when `metadata` is `None` or omits `box_file_id`.

**Validates: Requirements 1.5, 1.6**

### Property 4: Exactly six ordered pipeline stages

For any `ProcessingResult`, `deriveStages()` returns exactly six stages whose labels are, in order, `Received`, `Classified`, `Routed`, `Task Created`, `Notified`, `Complete`.

**Validates: Requirements 3.2**

### Property 5: Stage derivation is correct and monotonic

For any `ProcessingResult`: if `status == "success"` every stage state is `completed`; otherwise (a) when `task_id` is null the `Task Created` stage and all subsequent stages are `pending`, and (b) when `notification_sent_to` is empty the `Notified` stage is `pending`; and in all non-success cases, once a stage is not `completed`, every later stage is also not `completed` (no completed stage follows a pending/error stage).

**Validates: Requirements 3.3, 3.4, 3.5**

### Property 6: Failure marks an error stage and surfaces the message

For any `ProcessingResult` with `status == "failure"`, exactly one stage has state `error`, and when `error_message` is non-empty the rendered output contains that message.

**Validates: Requirements 3.6**

---

## Testing Strategy

### Dual approach
- **Property tests** (≥100 iterations each) cover the universal properties above — the pure functions `_build_slack_message()` (P1–P3) and `deriveStages()` (P4–P6). Backend uses `hypothesis`; frontend uses `fast-check`.
- **Example / edge / integration / smoke tests** cover the wiring and config-gated behavior that does not vary with input:
  - *Examples*: model field definitions (Req 2.1, 2.2), metadata pass-through via mocks (Req 1.9, 1.10, 2.4), 200 happy path (Req 2.5), App integration swap (Req 3.8), null-guard (Req 3.9), CSS class application (Req 3.7).
  - *Edge cases*: 422 on missing/invalid fields (Req 2.7), 500 on raised exception (Req 2.6).
  - *Integration*: live-mode `httpx` POST of enriched payload with a mocked client (Req 1.12).
  - *Smoke*: route registered with method/path and `["tasks"]` tag (Req 2.3, 2.8), demo-mode returns `True` with no HTTP (Req 1.11).

### Property test configuration
- Minimum 100 iterations per property test.
- Each property test is tagged: **Feature: slack-box-workflow, Property {number}: {property_text}** and references the design property it validates.
- Generators: confidence ∈ [0.0, 1.0]; amounts spanning across the 10000 boundary (including ≤0, exactly 10000, and large values); doc_type drawn from the `ClassificationResult` literal set; `ProcessingResult` generated with random `status`, nullable `task_id`, and empty/non-empty `notification_sent_to` to exercise the derivation branches.
