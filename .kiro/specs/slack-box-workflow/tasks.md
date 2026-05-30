# Implementation Plan: slack-box-workflow

## Overview

Three Domain-3-scoped changes, ordered by demo value so the highest-impact work lands and verifies first:

1. **Slack enrichment** (`notifications.py`) — thread an optional `metadata` dict through the existing `httpx`-based Slack path and render an urgent variant for high-value invoices. Gets the webhook visibly producing rich messages.
2. **POST /tasks/create** (`models.py` + `routes.py`) — wire the endpoint the sidebar already calls to the existing `TaskManager.create_review_task()`.
3. **WorkflowStatus UI** (`App.tsx` + new `WorkflowStatus.tsx`/`.css`) — derive six pipeline stages from `processingResult` and swap the inline block.

All backend changes are additive (new optional params / new models / new route) so Domain 1 and Domain 2 files are untouched and merge conflicts stay minimal. Tests are kept practical: property tests cover the pure functions (P1–P6) and are marked optional so core wiring can ship under the time budget.

## Tasks

- [x] 1. Slack message enrichment (highest demo value — webhook online)
  - [x] 1.1 Add formatting helpers and enrich `_build_slack_message()`
    - In `backend/domain_3_box_integration/notifications.py`, add static helpers `_format_percent(confidence)` (0.0–1.0 float → integer `%`) and `_format_currency(amount)` (`$` prefix, thousands separators, 2 decimals)
    - Add an optional `metadata: Optional[dict] = None` parameter to `_build_slack_message()` (keep existing positional params)
    - Append body lines for `confidence`, `vendor`, and `amount` only when each key is present in `metadata`
    - Resolve the "Review in Box" button URL to `https://app.box.com/file/{box_file_id}` when `box_file_id` is present, falling back to `document_id` otherwise
    - Render the urgent variant (🚨 text + `danger` button style) iff `doc_type == "invoice"` and `amount` is present and `> 10000`; otherwise the standard variant (📄, no danger style)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_

  - [x] 1.2 Thread `metadata` through `_send_slack_notification()` and `send_notifications()`, and wire the live call site
    - Add `metadata: Optional[dict] = None` to `_send_slack_notification()` and pass it into `_build_slack_message()`
    - Add `metadata: Optional[dict] = None` to `send_notifications()` and forward it to `_send_slack_notification()`
    - In `backend/domain_3_box_integration/service.py`, build a `metadata` dict in `process()` from `classification_result.extracted_fields` (`vendor`, `amount`), `classification_result.confidence`, and the `box_file_id` (the moved `file_id`), and pass it to `send_notifications(...)` so the enrichment actually reaches Slack in the live pipeline
    - Preserve the existing demo gate: when `Config.DEMO_MODE` or no `SLACK_WEBHOOK_URL`, log the enriched payload at INFO and return `True` with no HTTP call
    - Preserve the existing live path: `httpx` POST of the enriched payload to `SLACK_WEBHOOK_URL`
    - _Requirements: 1.9, 1.10, 1.11, 1.12_

  - [ ]* 1.3 Write property test for enrichment field rendering
    - **Property 1: Enrichment fields are rendered when present**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.6**
    - Add `hypothesis` to `requirements.txt`; create `backend/domain_3_box_integration/tests/test_notifications.py`
    - Generate `metadata` with arbitrary subsets of `confidence` ∈ [0.0, 1.0], `vendor` (str), `amount` (number); assert each present field appears (confidence as `%`, amount as currency, vendor verbatim) and absent keys produce no line; ≥100 iterations

  - [ ]* 1.4 Write property test for the urgency variant
    - **Property 2: Urgency variant is determined by doc_type and amount**
    - **Validates: Requirements 1.7, 1.8**
    - In `test_notifications.py`, generate `doc_type` from the classification literal set and `amount` spanning the 10000 boundary (≤0, exactly 10000, large); assert 🚨 + `danger` iff `doc_type == "invoice"` and `amount > 10000`, else 📄 and no danger style; ≥100 iterations

  - [ ]* 1.5 Write property test for button URL resolution
    - **Property 3: Button URL resolution**
    - **Validates: Requirements 1.5, 1.6**
    - In `test_notifications.py`, assert the action button URL is `https://app.box.com/file/{box_file_id}` when `metadata` has `box_file_id`, and falls back to `https://app.box.com/file/{document_id}` when `metadata` is `None` or omits the key; ≥100 iterations

  - [ ]* 1.6 Write example and integration tests for the Slack path
    - In `test_notifications.py`: demo mode returns `True` with no HTTP call (1.11); live mode POSTs the enriched payload via a mocked `httpx.AsyncClient` (1.12); `send_notifications()`/`_send_slack_notification()` forward `metadata` to the builder (verify via mock)
    - _Requirements: 1.9, 1.10, 1.11, 1.12_

- [x] 2. POST /tasks/create endpoint (highest demo value — sidebar task creation)
  - [x] 2.1 Add `CreateTaskRequest` and `CreateTaskResponse` models
    - Append to `backend/domain_3_box_integration/models.py` (no edits to existing models)
    - `CreateTaskRequest`: `file_id: str`, `assigned_to: EmailStr`, `due_date: Optional[str] = None`, `message: Optional[str] = None`
    - `CreateTaskResponse`: `task_id: str`, `status: str`
    - _Requirements: 2.1, 2.2_

  - [x] 2.2 Add the `POST /tasks/create` route delegating to `TaskManager`
    - In `backend/domain_3_box_integration/routes.py`, instantiate `_task_manager = TaskManager(BoxClient())` at module scope and import the new models
    - Implement `create_task` with `response_model=CreateTaskResponse` and `tags=["tasks"]`; delegate to `TaskManager.create_review_task(file_id, doc_type="document", assigned_to_email=str(request.assigned_to), due_date=request.due_date)`
    - Return HTTP 200 with `{task_id, status: "created"}` on success; catch exceptions and raise `HTTPException(status_code=500, detail=str(e))`
    - _Requirements: 2.3, 2.4, 2.5, 2.6, 2.8_

  - [ ]* 2.3 Write route tests for `/tasks/create`
    - Create `backend/domain_3_box_integration/tests/test_tasks_route.py` using FastAPI `TestClient`
    - Cover: 200 happy path with mocked `create_review_task` (2.5); 422 on missing `file_id`/`assigned_to` or invalid email (2.7); 500 when `create_review_task` raises (2.6); route registered with method/path and `["tasks"]` tag (2.3, 2.8)
    - _Requirements: 2.3, 2.5, 2.6, 2.7, 2.8_

- [x] 3. Checkpoint — backend demo-ready
  - Ensure all backend tests pass, ask the user if questions arise.

- [x] 4. WorkflowStatus UI component (third priority)
  - [x] 4.1 Create `WorkflowStatus.tsx` with the `deriveStages` pure function
    - Create `box-extension/src/components/WorkflowStatus.tsx`
    - Define `STAGE_LABELS` (exactly six, fixed order: Received, Classified, Routed, Task Created, Notified, Complete), `StageState`, and `Stage`; mirror the local `ProcessingResult` interface
    - Export `deriveStages(pr)`: success → all `completed`; failure → mark the failure-point stage `error` (earlier `completed`, later `pending`); otherwise derive per field with `enforceMonotonic` (after the first non-`completed` stage, all later stages are non-`completed`) using `task_id` and `notification_sent_to`
    - Render the `<ol>` of stages with per-state classes/icons and the `error_message` paragraph on failure
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 4.2 Create `WorkflowStatus.css` with state styles
    - Create `box-extension/src/styles/WorkflowStatus.css` with distinct `.stage-completed`, `.stage-pending`, `.stage-error` classes (color + icon) plus `.workflow-status`, `.workflow-stages`, and `.workflow-error`
    - _Requirements: 3.7_

  - [x] 4.3 Swap the inline block in `App.tsx` for `<WorkflowStatus />`
    - Import `WorkflowStatus` and replace the inline `<div className="processing-result">…</div>` with `{processingResult && <WorkflowStatus processingResult={processingResult} />}`, preserving the null-guard; no other lines change
    - _Requirements: 3.8, 3.9_

  - [ ]* 4.4 Set up frontend test tooling (vitest + fast-check)
    - Add `vitest` and `fast-check` devDependencies and a `test` script to `box-extension/package.json`; add minimal `vitest.config.ts`
    - (Optional prerequisite for the frontend property tests below)

  - [ ]* 4.5 Write property test for the six ordered stages
    - **Property 4: Exactly six ordered pipeline stages**
    - **Validates: Requirements 3.2**
    - Create `box-extension/src/components/WorkflowStatus.test.tsx`; with `fast-check`, generate arbitrary `ProcessingResult` and assert `deriveStages()` returns six stages whose labels match the fixed order; ≥100 runs

  - [ ]* 4.6 Write property test for stage derivation and monotonicity
    - **Property 5: Stage derivation is correct and monotonic**
    - **Validates: Requirements 3.3, 3.4, 3.5**
    - In `WorkflowStatus.test.tsx`, generate `status`, nullable `task_id`, and empty/non-empty `notification_sent_to`; assert success → all `completed`; null `task_id` → `Task Created` and later stages `pending`; empty notifications → `Notified` pending; and no `completed` stage follows a non-`completed` stage; ≥100 runs

  - [ ]* 4.7 Write property test for failure handling
    - **Property 6: Failure marks an error stage and surfaces the message**
    - **Validates: Requirements 3.6**
    - In `WorkflowStatus.test.tsx`, for `status === "failure"` assert exactly one stage has state `error` and the rendered output contains a non-empty `error_message`; ≥100 runs

- [x] 5. Final checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional (test sub-tasks) and can be skipped for a faster demo path; the core wiring tasks (1.1, 1.2, 2.1, 2.2, 4.1, 4.2, 4.3) are sufficient to demo Slack notifications, task creation, and the pipeline UI.
- Ordering reflects demo value: Slack enrichment (1) and `/tasks/create` (2) land and verify first; WorkflowStatus UI (4) is third.
- Scope is confined to Domain 3 backend files (`notifications.py`, `routes.py`, `models.py`) and frontend (`App.tsx` + new `WorkflowStatus.tsx`/`.css`) plus their test files, to minimize merge conflicts with Domain 1/2 teammates.
- Backend property tests use `hypothesis` (added in 1.3); frontend property tests use `fast-check` (tooling added in 4.4). Each property test runs ≥100 iterations and is annotated with its property number and the requirements it validates.
- Each property is its own sub-task placed next to the implementation it checks, so regressions surface early.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1", "4.1", "4.2", "4.4"] },
    { "id": 1, "tasks": ["1.2", "2.2", "4.3"] },
    { "id": 2, "tasks": ["1.3", "2.3", "4.5"] },
    { "id": 3, "tasks": ["1.4", "4.6"] },
    { "id": 4, "tasks": ["1.5", "4.7"] },
    { "id": 5, "tasks": ["1.6"] }
  ]
}
```
