"""FastAPI application entry point for Box Smart Inbox."""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.shared.config import Config
from backend.shared.logging import setup_logging
from backend.shared.types import IngestedDocument, ProcessingResult
from backend.shared.database import db
from backend.domain_1_email import routes as domain1_routes
from backend.domain_2_classifier import routes as domain2_routes
from backend.domain_3_box_integration import routes as domain3_routes

# Setup logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Box Smart Inbox",
    description="AI-powered document orchestration with signature tracking",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database startup and shutdown
@app.on_event("startup")
async def startup():
    """Initialize database connection on startup."""
    logger.info("Starting Box Smart Inbox application")
    try:
        await db.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown."""
    logger.info("Shutting down Box Smart Inbox application")
    await db.disconnect()
    logger.info("Database disconnected")


# Include domain routers
app.include_router(domain1_routes.router, tags=["domain-1"])
app.include_router(domain2_routes.router, tags=["domain-2"])
app.include_router(domain3_routes.router, tags=["domain-3"])


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "box-smart-inbox",
        "environment": Config.ENVIRONMENT,
    }


@app.get("/status")
async def get_status() -> dict:
    """
    Get system status and database statistics.

    Returns:
        dict: Status including documents in pipeline, success rate, etc.
    """
    try:
        total_docs = await db.fetch_val("SELECT COUNT(*) FROM documents")
        completed_docs = await db.fetch_val(
            "SELECT COUNT(*) FROM documents WHERE status = 'complete'"
        )
        success_rate = (completed_docs / total_docs * 100) if total_docs > 0 else 0

        return {
            "status": "operational",
            "documents_total": total_docs,
            "documents_completed": completed_docs,
            "success_rate": f"{success_rate:.1f}%",
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "status": "operational",
            "documents_total": 0,
            "documents_completed": 0,
            "success_rate": "0.0%",
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level=Config.LOG_LEVEL.lower(),
    )
