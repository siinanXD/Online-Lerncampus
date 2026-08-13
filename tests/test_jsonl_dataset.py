"""Tests for the BZE MAF JSONL dataset importer."""

from __future__ import annotations

import json
from pathlib import Path

from app.data.jsonl_dataset import load_jsonl_dataset
from app.services.content_seeder import ContentSeeder
from app.services.database import Database


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_jsonl_dataset_maps_into_content_tables(tmp_path: Path) -> None:
    """A minimal JSONL dataset must import as units, quiz and open questions."""
    _write_jsonl(
        tmp_path / "sources.jsonl",
        [
            {
                "id": "SRC-TEST",
                "title": "Testquelle",
                "publisher": "BZE",
                "url": "https://example.test",
                "type": "official_regulation",
                "usage_note": "Testdaten",
                "scope": "Sicherheit, Pruefung",
            }
        ],
    )
    _write_jsonl(
        tmp_path / "modules.jsonl",
        [
            {
                "id": "MAF-MOD-0001",
                "month": 1,
                "sequence": 1,
                "title": "Willkommen",
                "focus": "Arbeitsplatz",
                "exam_orientation": "production_planning",
                "source_ids": ["SRC-TEST"],
            }
        ],
    )
    _write_jsonl(
        tmp_path / "chapters.jsonl",
        [
            {
                "id": "MAF-CH-0001",
                "module_id": "MAF-MOD-0001",
                "month": 1,
                "week": 1,
                "sequence": 1,
                "title": "Informationsquellen",
                "exam_area": "production_planning",
            }
        ],
    )
    _write_jsonl(
        tmp_path / "lessons.jsonl",
        [
            {
                "id": "MAF-LESSON-0001",
                "chapter_id": "MAF-CH-0001",
                "module_id": "MAF-MOD-0001",
                "sequence": 1,
                "title": "Informationsquellen",
                "summary": "Unterlagen vor der Arbeit pruefen.",
                "estimated_minutes": 20,
                "learning_objective_ids": ["MAF-LO-0001"],
                "source_ids": ["SRC-TEST"],
            }
        ],
    )
    _write_jsonl(
        tmp_path / "learning_objectives.jsonl",
        [
            {
                "id": "MAF-LO-0001",
                "title": "Unterlagen sicher anwenden",
                "description": "Arbeitsauftrag und Zeichnung nutzen.",
            }
        ],
    )
    _write_jsonl(
        tmp_path / "content_blocks.jsonl",
        [
            {
                "id": "MAF-CB-0001-1",
                "lesson_id": "MAF-LESSON-0001",
                "title": "Fachkunde",
                "type": "fachkunde",
                "body": "Zuerst Unterlagen und Sollwerte pruefen.",
            }
        ],
    )
    _write_jsonl(
        tmp_path / "flashcards.jsonl",
        [
            {
                "id": "MAF-FC-0001-1",
                "lesson_id": "MAF-LESSON-0001",
                "front": "Was zuerst pruefen?",
                "back": "Unterlagen und Freigaben.",
            }
        ],
    )
    _write_jsonl(
        tmp_path / "questions.jsonl",
        [
            {
                "id": "MAF-Q-0001-1",
                "lesson_id": "MAF-LESSON-0001",
                "type": "single_choice",
                "prompt": "Was kommt zuerst?",
                "options": [
                    {"id": "OPT-1", "text": "Unterlagen pruefen"},
                    {"id": "OPT-2", "text": "Ohne Plan starten"},
                ],
                "correct_answer": "OPT-1",
                "explanation": "Information vor Ausfuehrung.",
                "difficulty": 5,
                "source_ids": ["SRC-TEST"],
            },
            {
                "id": "MAF-Q-0001-2",
                "lesson_id": "MAF-LESSON-0001",
                "type": "calculation",
                "prompt": "Welche Drehzahl ergibt sich?",
                "correct_answer": {"value": 318, "unit": "1/min", "tolerance": 2},
                "explanation": "n = 1000 * vc / (pi * d)",
                "difficulty": 4,
                "source_ids": ["SRC-TEST"],
            },
        ],
    )
    _write_jsonl(
        tmp_path / "assessments.jsonl",
        [
            {
                "id": "MAF-ASSESS-DIAG-START",
                "title": "Eingangsdiagnose",
                "type": "diagnostic",
                "duration_minutes": 45,
                "question_ids": ["MAF-Q-0001-1", "MAF-Q-0001-2"],
                "grading": {"pass_threshold_percent": 67},
            }
        ],
    )
    for name in (
        "competencies",
        "worlds",
        "interactive_tasks",
        "practical_scenarios",
        "spaced_repetition",
        "mappings",
    ):
        (tmp_path / f"{name}.jsonl").write_text("", encoding="utf-8")

    bundle = load_jsonl_dataset(tmp_path)
    assert len(bundle.units) == 1
    assert len(bundle.questions) == 1
    assert len(bundle.open_questions) == 1
    assert bundle.questions[0].difficulty == 3
    assert bundle.open_questions[0].sample_solution.startswith("318 1/min")
    assert bundle.exams[0].question_ids == ["MAF-Q-0001-1"]
    assert bundle.exams[0].open_question_ids == ["MAF-Q-0001-2"]

    database = Database(f"sqlite:///{tmp_path / 'jsonl.db'}")
    counts = ContentSeeder(database, bundle=bundle).seed_all()
    assert counts["learning_units"] == 1
    assert counts["quiz_questions"] == 1
    assert counts["open_questions"] == 1
    assert counts["practice_exams"] == 1
