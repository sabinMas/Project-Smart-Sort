# Requirements Document

## Introduction

This feature completes three interconnected workflow enhancements for the Box Smart Inbox system:

1. **Slack enrichment** — extends `_build_slack_message()` in `NotificationManager` to accept optional classification metadata (confidence, vendor, amount, box_file_id), render an urgent 🚨 variant for high-value invoices (amount > $10,000), and link the "Review in Box" button directly to the specific Box file.

2. **POST /tasks/create route** — wires up a new FastAPI endpoint in `domain_3_box_integration/routes.py` that delegates to the existing `TaskManager.create_review_task()`, accepts a typed Pydantic request body, and returns a structured response.

3. **WorkflowStatus UI component** — introduces a new `WorkflowStatus.tsx` React component (with companion CSS) that derives six pipeline stages from `processingResult` and replaces the inline "Processing Status" block in `App.tsx`.

## Glossary

- **NotificationManager**: Python class in `backend/domain_3_box_integration/notifications.py` responsible for sending Slack and email notifications.
- **_build_slack_message()**: Method on `NotificationManager` that constructs the Slack Block Kit payload.
- **_send_slack_notification()**: Method on `NotificationManager` that resolves the webhook URL and dispatches the Slack payload built by `_build_slack_message()`.
- **send_notifications()**: Public method on `NotificationManager` that orchestrates all notification channels for a processed document.
- **TaskManager**: Python class in `backend/domain_3_box_integration/tasks.py` that creates and assigns Box review tasks.
- **CreateTaskRequest**: Pydantic model to be added to `backend/domain_3_box_integration/models.py` representing the `/tasks/create` request body.
- **CreateTaskResponse**: Pydantic model representing the `/tasks/create` response body.
- **WorkflowStatus**: New React component in `box-extension/src/components/WorkflowStatus.tsx` that visualises the six pipeline stages.
- **processingResult**: The `ProcessingResult` object already available in `App.tsx` state, containing `status`, `destination_folder`, `task_id`, `assigned_to`, `notification_sent_to`, and `error_message`.
- **High-value invoice**: An invoice document where the extracted `amount` field exceeds $10,000.
- **Pipeline stage**: One of six discrete steps in the document processing workflow displayed by `WorkflowStatus`.
- **Box file URL**: A URL of the form `https://app.box.com/file/{box_file_id}` that opens a specific file in the Box web application.
- **SLACK_WEBHOOK_URL**: Environment variable that holds the Slack incoming webhook URL used by `NotificationManager` in live mode.
- **Demo mode**: Operating mode (controlled by `Config.DEMO_MODE`) in which external HTTP calls are skipped and outcomes are logged instead.

---

## Requirements

### Requirement 1: Slack Message Metadata Enrichment

**User Story:** As a finance team member, I want Slack notifications to include document confidence, vendor name, amount, and a direct link to the Box file, so that I can assess and act on a document without leaving Slack.

#### Acceptance Criteria

1. THE `NotificationManager` SHALL accept an optional `metadata` parameter of type `dict` on `_build_slack_message()`, alongside the existing `document_id`, `doc_type`, and `assigned_to_email` parameters.

2. WHEN `metadata` is provided and contains a `confidence` key, THE `NotificationManager` SHALL include the confidence value formatted as a percentage in the Slack message body.

3. WHEN `metadata` is provided and contains a `vendor` key, THE `NotificationManager` SHALL include the vendor name in the Slack message body.

4. WHEN `metadata` is provided and contains an `amount` key, THE `NotificationManager` SHALL include the amount formatted as a currency value in the Slack message body.

5. WHEN `metadata` is provided and contains a `box_file_id` key, THE `NotificationManager` SHALL set the "Review in Box" button URL to `https://app.box.com/file/{box_file_id}`.

6. IF `metadata` is not provided or is `None`, THEN THE `NotificationManager` SHALL fall back to the existing button URL `https://app.box.com/file/{document_id}` and omit the enrichment fields from the message body.

7. WHEN `doc_type` is `"invoice"` and `metadata` contains an `amount` value greater than 10000, THE `NotificationManager` SHALL render the urgent variant of the Slack message, using the 🚨 emoji in the message text and a `danger` style on the action button.

8. WHEN `doc_type` is not `"invoice"` or `amount` is 10000 or less, THE `NotificationManager` SHALL render the standard (non-urgent) Slack message variant using the 📄 emoji.

9. THE `_send_slack_notification()` method SHALL accept an optional `metadata` parameter and pass it to `_build_slack_message()`, so that enrichment data flows from the call site through to the payload builder.

10. THE `send_notifications()` method SHALL accept an optional `metadata` parameter of type `dict` and forward it to `_send_slack_notification()`, so that callers can supply classification metadata in a single call.

11. WHILE `Config.DEMO_MODE` is `True` or `SLACK_WEBHOOK_URL` is not set, THE `NotificationManager` SHALL log the enriched Slack payload at INFO level and return `True` without making an outbound HTTP request.

12. WHEN `Config.DEMO_MODE` is `False` and `SLACK_WEBHOOK_URL` is set, THE `NotificationManager` SHALL POST the enriched Slack payload to the URL specified by `SLACK_WEBHOOK_URL`.

---

### Requirement 2: POST /tasks/create Endpoint

**User Story:** As a Box extension user, I want to assign a review task to a colleague directly from the sidebar, so that the task is tracked in Box without manual steps.

#### Acceptance Criteria

1. THE `CreateTaskRequest` Pydantic model SHALL be defined in `backend/domain_3_box_integration/models.py` with the fields: `file_id` (str, required), `assigned_to` (EmailStr, required), `due_date` (Optional[str], default None), and `message` (Optional[str], default None).

2. THE `CreateTaskResponse` Pydantic model SHALL be defined in `backend/domain_3_box_integration/models.py` with the fields: `task_id` (str) and `status` (str).

3. THE `routes.py` router SHALL expose a `POST /tasks/create` endpoint that accepts a `CreateTaskRequest` body and returns a `CreateTaskResponse`.

4. WHEN a valid `POST /tasks/create` request is received, THE router SHALL delegate task creation to `TaskManager.create_review_task()` using `file_id`, `assigned_to`, and `due_date` from the request body.

5. WHEN `TaskManager.create_review_task()` returns a task ID, THE router SHALL respond with HTTP 200 and a `CreateTaskResponse` containing the task ID and `status` set to `"created"`.

6. IF `TaskManager.create_review_task()` raises an exception, THEN THE router SHALL respond with HTTP 500 and a JSON detail message describing the failure.

7. WHEN the request body is missing `file_id` or `assigned_to`, THE router SHALL respond with HTTP 422 (Unprocessable Entity) via FastAPI's default validation.

8. THE `POST /tasks/create` endpoint SHALL be tagged `["tasks"]` in the OpenAPI schema.

---

### Requirement 3: WorkflowStatus React Component

**User Story:** As a Box extension user, I want to see a clear visual pipeline of the six processing stages for a document, so that I can understand exactly where the document is in the workflow at a glance.

#### Acceptance Criteria

1. THE `WorkflowStatus` component SHALL be defined in `box-extension/src/components/WorkflowStatus.tsx` and accept a single `processingResult` prop of type `ProcessingResult` (imported from or co-located with `App.tsx`).

2. THE `WorkflowStatus` component SHALL derive and display exactly six pipeline stages in order: `Received`, `Classified`, `Routed`, `Task Created`, `Notified`, and `Complete`.

3. WHEN `processingResult.status` is `"success"`, THE `WorkflowStatus` component SHALL mark all six stages as completed.

4. WHEN `processingResult.task_id` is `null`, THE `WorkflowStatus` component SHALL mark the `Task Created` stage as pending and all subsequent stages as pending.

5. WHEN `processingResult.notification_sent_to` is an empty array, THE `WorkflowStatus` component SHALL mark the `Notified` stage as pending.

6. WHEN `processingResult.status` is `"failure"`, THE `WorkflowStatus` component SHALL mark the stage corresponding to the failure point as errored and display `processingResult.error_message` beneath the pipeline.

7. THE `WorkflowStatus` component SHALL apply styles from `box-extension/src/styles/WorkflowStatus.css`, using distinct CSS classes for `completed`, `pending`, and `error` stage states.

8. THE `App.tsx` file SHALL import `WorkflowStatus` and render it in place of the existing inline `<div className="processing-result">` block, passing `processingResult` as the prop.

9. WHEN `processingResult` is `null`, THE `App.tsx` file SHALL not render the `WorkflowStatus` component (existing null-guard behaviour is preserved).
