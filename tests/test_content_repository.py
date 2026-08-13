"""Tests for the database-backed content repository."""

from pathlib import Path

from app.services.content_repository import ContentRepository
from app.services.content_seeder import ContentSeeder
from app.services.database import Database


def test_content_repository_reads_seeded_questions(tmp_path: Path) -> None:
    """DB repository must return the same volume as the Python seed."""
    database = Database(f"sqlite:///{tmp_path / 'repo.db'}")
    ContentSeeder(database).seed_all()
    repository = ContentRepository(database)

    assert len(repository.list_categories()) == 240
    assert len(repository.list_questions()) == 480
    assert len(repository.list_learning_units()) == 240
    assert len(repository.list_questions(month=1)) == 20

    unit = repository.get_learning_unit("messschieber")
    assert unit.title == "Messschieber"
    assert len(unit.theory_blocks) >= 3

    exam, questions = repository.get_exam("exam-01")
    assert exam is not None
    assert len(questions) == 10
