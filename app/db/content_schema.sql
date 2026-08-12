-- Online Lerncampus: content + extended learner schema (SQLite / PostgreSQL compatible)
-- Phase 1: tables only. Seed import and repository switch follow in later phases.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- A. Stammdaten: Beruf, Schwerpunkt, Curriculum
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS occupations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    duration_months INTEGER NOT NULL CHECK (duration_months > 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS specializations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occupation_id INTEGER NOT NULL,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (occupation_id) REFERENCES occupations (id) ON DELETE CASCADE,
    UNIQUE (occupation_id, slug)
);

CREATE TABLE IF NOT EXISTS curriculum_months (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occupation_id INTEGER NOT NULL,
    specialization_id INTEGER,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 48),
    year INTEGER NOT NULL CHECK (year IN (1, 2, 3, 4)),
    title TEXT NOT NULL,
    focus_area TEXT NOT NULL,
    learning_goals_json TEXT NOT NULL DEFAULT '[]',
    is_exam_preparation INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (occupation_id) REFERENCES occupations (id) ON DELETE CASCADE,
    FOREIGN KEY (specialization_id) REFERENCES specializations (id) ON DELETE SET NULL,
    UNIQUE (occupation_id, specialization_id, month)
);

CREATE TABLE IF NOT EXISTS learning_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curriculum_month_id INTEGER NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    mission_type TEXT NOT NULL,
    lesson_goal TEXT NOT NULL,
    quiz_focus TEXT NOT NULL,
    required_review INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (curriculum_month_id) REFERENCES curriculum_months (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_curriculum_months_occ_month
    ON curriculum_months (occupation_id, month);

-- ---------------------------------------------------------------------------
-- B. Quellen & Review
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS source_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    publisher TEXT NOT NULL,
    url TEXT NOT NULL,
    trust_tier INTEGER NOT NULL CHECK (trust_tier BETWEEN 1 AND 3),
    allowed_usage TEXT NOT NULL,
    topics_json TEXT NOT NULL DEFAULT '[]',
    archived_sha256 TEXT,
    last_verified_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS content_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL CHECK (
        entity_type IN ('learning_unit', 'quiz_question', 'open_question')
    ),
    entity_id INTEGER NOT NULL,
    from_status TEXT,
    to_status TEXT NOT NULL,
    reviewer_learner_id TEXT,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (reviewer_learner_id) REFERENCES learners (learner_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_content_reviews_entity
    ON content_reviews (entity_type, entity_id);

-- ---------------------------------------------------------------------------
-- C. Lerncontent
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS question_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    curriculum_month_id INTEGER NOT NULL,
    subchapter_number INTEGER NOT NULL CHECK (subchapter_number BETWEEN 1 AND 20),
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (curriculum_month_id) REFERENCES curriculum_months (id) ON DELETE CASCADE,
    UNIQUE (curriculum_month_id, subchapter_number)
);

CREATE TABLE IF NOT EXISTS learning_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    curriculum_month_id INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    title TEXT NOT NULL,
    subtitle TEXT NOT NULL DEFAULT '',
    learning_goals_json TEXT NOT NULL DEFAULT '[]',
    practice_task TEXT NOT NULL DEFAULT '',
    estimated_minutes INTEGER NOT NULL DEFAULT 12,
    review_status TEXT NOT NULL DEFAULT 'draft' CHECK (
        review_status IN ('draft', 'source_checked', 'needs_revision', 'approved')
    ),
    version INTEGER NOT NULL DEFAULT 1,
    published_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (curriculum_month_id) REFERENCES curriculum_months (id) ON DELETE CASCADE,
    UNIQUE (curriculum_month_id, position)
);

CREATE TABLE IF NOT EXISTS theory_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learning_unit_id INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    heading TEXT NOT NULL,
    body TEXT NOT NULL,
    key_points_json TEXT NOT NULL DEFAULT '[]',
    norm_references_json TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (learning_unit_id) REFERENCES learning_units (id) ON DELETE CASCADE,
    UNIQUE (learning_unit_id, position)
);

CREATE TABLE IF NOT EXISTS glossary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learning_unit_id INTEGER NOT NULL,
    term TEXT NOT NULL,
    definition TEXT NOT NULL,
    FOREIGN KEY (learning_unit_id) REFERENCES learning_units (id) ON DELETE CASCADE,
    UNIQUE (learning_unit_id, term)
);

CREATE TABLE IF NOT EXISTS learning_unit_categories (
    learning_unit_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (learning_unit_id, category_id),
    FOREIGN KEY (learning_unit_id) REFERENCES learning_units (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES question_categories (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quiz_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL UNIQUE,
    category_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    options_json TEXT NOT NULL,
    correct_option_index INTEGER NOT NULL CHECK (correct_option_index >= 0),
    explanation TEXT NOT NULL DEFAULT '',
    difficulty INTEGER NOT NULL DEFAULT 2 CHECK (difficulty BETWEEN 1 AND 3),
    exam_style TEXT NOT NULL DEFAULT 'single_choice',
    review_status TEXT NOT NULL DEFAULT 'draft' CHECK (
        review_status IN ('draft', 'source_checked', 'needs_revision', 'approved')
    ),
    version INTEGER NOT NULL DEFAULT 1,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES question_categories (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_quiz_questions_category
    ON quiz_questions (category_id, is_active);

CREATE TABLE IF NOT EXISTS open_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL UNIQUE,
    category_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    answer_format TEXT NOT NULL CHECK (
        answer_format IN ('short_text', 'calculation', 'sketch')
    ),
    sample_solution TEXT NOT NULL DEFAULT '',
    review_status TEXT NOT NULL DEFAULT 'draft' CHECK (
        review_status IN ('draft', 'source_checked', 'needs_revision', 'approved')
    ),
    version INTEGER NOT NULL DEFAULT 1,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES question_categories (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS open_question_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    open_question_id INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    description TEXT NOT NULL,
    points INTEGER NOT NULL CHECK (points > 0),
    FOREIGN KEY (open_question_id) REFERENCES open_questions (id) ON DELETE CASCADE,
    UNIQUE (open_question_id, position)
);

CREATE TABLE IF NOT EXISTS content_source_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL CHECK (
        entity_type IN ('learning_unit', 'quiz_question', 'open_question')
    ),
    entity_id INTEGER NOT NULL,
    FOREIGN KEY (source_id) REFERENCES source_documents (id) ON DELETE CASCADE,
    UNIQUE (source_id, entity_type, entity_id)
);

-- ---------------------------------------------------------------------------
-- D. Pruefungen
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS practice_exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    passing_score_percent INTEGER NOT NULL DEFAULT 80,
    time_limit_minutes INTEGER NOT NULL DEFAULT 0,
    is_checkpoint INTEGER NOT NULL DEFAULT 0,
    curriculum_month_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (curriculum_month_id) REFERENCES curriculum_months (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS exam_quiz_questions (
    exam_id INTEGER NOT NULL,
    quiz_question_id INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    PRIMARY KEY (exam_id, position),
    FOREIGN KEY (exam_id) REFERENCES practice_exams (id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_question_id) REFERENCES quiz_questions (id) ON DELETE CASCADE,
    UNIQUE (exam_id, quiz_question_id)
);

CREATE TABLE IF NOT EXISTS exam_open_questions (
    exam_id INTEGER NOT NULL,
    open_question_id INTEGER NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    PRIMARY KEY (exam_id, position),
    FOREIGN KEY (exam_id) REFERENCES practice_exams (id) ON DELETE CASCADE,
    FOREIGN KEY (open_question_id) REFERENCES open_questions (id) ON DELETE CASCADE,
    UNIQUE (exam_id, open_question_id)
);

-- ---------------------------------------------------------------------------
-- E. Erweiterter Lernfortschritt (Phase 5+)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS category_progress (
    learner_id TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    questions_mastered INTEGER NOT NULL DEFAULT 0,
    questions_total INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (learner_id, category_id),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES question_categories (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS unit_progress (
    learner_id TEXT NOT NULL,
    learning_unit_id INTEGER NOT NULL,
    completed_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (learner_id, learning_unit_id),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE,
    FOREIGN KEY (learning_unit_id) REFERENCES learning_units (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exam_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id TEXT NOT NULL,
    exam_id INTEGER NOT NULL,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT,
    submitted_at TEXT,
    score_percent REAL,
    passed INTEGER,
    status TEXT NOT NULL DEFAULT 'in_progress' CHECK (
        status IN ('in_progress', 'submitted', 'expired')
    ),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES practice_exams (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exam_sessions_learner
    ON exam_sessions (learner_id, status);

CREATE TABLE IF NOT EXISTS exam_session_answers (
    session_id INTEGER NOT NULL,
    quiz_question_id INTEGER NOT NULL,
    selected_option_index INTEGER,
    is_correct INTEGER,
    answered_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (session_id, quiz_question_id),
    FOREIGN KEY (session_id) REFERENCES exam_sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_question_id) REFERENCES quiz_questions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exam_session_open_answers (
    session_id INTEGER NOT NULL,
    open_question_id INTEGER NOT NULL,
    learner_answer TEXT,
    self_score INTEGER,
    reviewer_score INTEGER,
    answered_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (session_id, open_question_id),
    FOREIGN KEY (session_id) REFERENCES exam_sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (open_question_id) REFERENCES open_questions (id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------------
-- Schema-Metadaten
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO schema_migrations (version)
VALUES ('001_content_schema');
