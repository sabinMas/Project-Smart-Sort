"""Pytest configuration and global fixtures."""

import os
import pytest
from dotenv import load_dotenv

# Load .env file before running tests
load_dotenv(override=True)


@pytest.fixture(scope="session")
def test_environment():
    """Configure test environment variables."""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["USE_ASYNC_QUEUE"] = "false"
    os.environ["DEMO_MODE"] = "true"

    # Set default values for missing env vars
    os.environ.setdefault("LLM_PROVIDER", "cerebras")
    os.environ.setdefault("BOX_CLIENT_ID", "test_box_client_id")
    os.environ.setdefault("BOX_CLIENT_SECRET", "test_box_client_secret")
    os.environ.setdefault("BOX_ENTERPRISE_ID", "test_enterprise_id")
    os.environ.setdefault("SENDGRID_API_KEY", "test_sendgrid_key")

    return os.environ


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio backend for async tests."""
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset module imports between tests to avoid state pollution."""
    yield
    # Cleanup happens after each test


# Markers for organizing tests
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (deselect with '-m \"not unit\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
