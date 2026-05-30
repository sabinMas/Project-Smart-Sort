"""Database connection and migration utilities."""

import asyncpg
import logging
from pathlib import Path
from typing import Optional

from .config import Config

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL database connection manager."""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """Initialize database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                Config.DATABASE_URL,
                min_size=1,
                max_size=Config.DATABASE_POOL_SIZE,
                command_timeout=Config.DATABASE_TIMEOUT_SEC,
            )
            logger.info("Database connection pool created")
            await self.run_migrations()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self) -> None:
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def run_migrations(self) -> None:
        """Run all pending migrations."""
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            migrations_dir = Path(__file__).parent.parent / "migrations"
            migration_files = sorted(migrations_dir.glob("*.sql"))

            for migration_file in migration_files:
                migration_name = migration_file.name

                existing = await conn.fetchval(
                    "SELECT id FROM migrations WHERE name = $1",
                    migration_name
                )

                if existing:
                    continue

                logger.info(f"Running migration: {migration_name}")
                sql = migration_file.read_text()

                try:
                    await conn.execute(sql)
                    await conn.execute(
                        "INSERT INTO migrations (name) VALUES ($1)",
                        migration_name
                    )
                    logger.info(f"Completed migration: {migration_name}")
                except Exception as e:
                    logger.error(f"Migration failed: {migration_name} - {e}")
                    raise

    async def execute(self, query: str, *args) -> None:
        """Execute a query without returning results."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetch_one(self, query: str, *args) -> Optional[dict]:
        """Execute a query and return one result as a dict."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetch_all(self, query: str, *args) -> list[dict]:
        """Execute a query and return all results as dicts."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetch_val(self, query: str, *args) -> Optional:
        """Execute a query and return a single scalar value."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def transaction(self):
        """Get a transaction context manager."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        conn = await self.pool.acquire()
        return conn.transaction()


# Global database instance
db = Database()
