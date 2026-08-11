"""Repository for trusted source metadata."""

from app.data.sources import TRUSTED_SOURCES
from app.models.domain import SourceDocument


class SourceRepository:
    """Read-only repository for source metadata."""

    def list_sources(self) -> list[SourceDocument]:
        """Return all trusted source documents."""
        return TRUSTED_SOURCES

    def get_sources_by_keys(self, keys: list[str]) -> list[SourceDocument]:
        """Return source documents matching the given source keys."""
        source_map = {source.key: source for source in TRUSTED_SOURCES}
        missing_keys = [key for key in keys if key not in source_map]
        if missing_keys:
            raise ValueError(f"Unknown source keys: {', '.join(missing_keys)}")
        return [source_map[key] for key in keys]

