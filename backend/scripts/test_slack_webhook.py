"""Standalone Slack webhook verification.

Posts a real, enriched Slack message (built by the production
NotificationManager) directly to a webhook URL so you can confirm the URL is
live and lands in your channel BEFORE relying on it in the demo.

This bypasses Config.DEMO_MODE on purpose: it always performs a real POST.

Usage (PowerShell / bash), pass the webhook URL as an argument:

    python backend/scripts/test_slack_webhook.py "https://hooks.slack.com/services/XXX/YYY/ZZZ"

...or set it as an env var and omit the argument:

    SLACK_WEBHOOK_URL=... python backend/scripts/test_slack_webhook.py

Exit code 0 means Slack accepted the message (HTTP 200, body "ok").
Any other exit code means it did not — read the printed status/body.
"""

import os
import sys
from pathlib import Path

import httpx

# Ensure the repo root is importable when this script is run directly
# (e.g. `python backend/scripts/test_slack_webhook.py`).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.domain_3_box_integration.notifications import NotificationManager


def main() -> int:
    webhook_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("SLACK_WEBHOOK_URL", "")

    if not webhook_url or "YOUR/WEBHOOK/URL" in webhook_url:
        print(
            "ERROR: no real webhook URL provided.\n"
            "Pass it as the first argument or set SLACK_WEBHOOK_URL.\n"
            'Example: python backend/scripts/test_slack_webhook.py '
            '"https://hooks.slack.com/services/XXX/YYY/ZZZ"'
        )
        return 2

    # Build the message via the SAME code the live pipeline uses, including the
    # high-value-invoice urgent variant, so the channel shows the real format.
    manager = NotificationManager()
    message = manager._build_slack_message(
        document_id="webhook-test-001",
        doc_type="invoice",
        assigned_to_email="finance@company.com",
        metadata={
            "confidence": 0.96,
            "vendor": "ACME Corporation",
            "amount": 25000,
            "box_file_id": "file_demo_0001",
        },
    )

    print("Posting test message to Slack webhook...")
    try:
        response = httpx.post(webhook_url, json=message, timeout=10.0)
    except Exception as e:  # noqa: BLE001 - surface any connection error plainly
        print(f"FAILED: could not reach the webhook URL: {e}")
        return 1

    print(f"HTTP {response.status_code}: {response.text!r}")

    if response.status_code == 200 and response.text.strip() == "ok":
        print("SUCCESS: check your #documents channel for the test message.")
        return 0

    print(
        "NOT OK: Slack did not accept the message. Common causes:\n"
        "  - URL copied incompletely or revoked\n"
        "  - webhook's app was removed from the workspace\n"
        "  - channel was archived/deleted"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
