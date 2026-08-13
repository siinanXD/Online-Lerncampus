"""Database schema definitions and migration helpers."""

from app.db.content_schema import CONTENT_SCHEMA_SQL, initialize_content_schema
from app.db.platform_schema import PLATFORM_SCHEMA_SQL, initialize_platform_schema

__all__ = [
    "CONTENT_SCHEMA_SQL",
    "PLATFORM_SCHEMA_SQL",
    "initialize_content_schema",
    "initialize_platform_schema",
]
