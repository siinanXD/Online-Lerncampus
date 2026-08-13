-- Online Lerncampus: learner preferences, tools, trainer/admin extras
-- SQLite / PostgreSQL compatible (AUTOINCREMENT rewritten for Postgres)

-- ---------------------------------------------------------------------------
-- Learner preferences, notifications, daily goals
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS learner_preferences (
    learner_id TEXT PRIMARY KEY,
    language TEXT NOT NULL DEFAULT 'de',
    theme TEXT NOT NULL DEFAULT 'dark',
    high_contrast INTEGER NOT NULL DEFAULT 0,
    reduce_motion INTEGER NOT NULL DEFAULT 0,
    daily_goal_lessons INTEGER NOT NULL DEFAULT 5,
    onboarding_completed INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notification_settings (
    learner_id TEXT PRIMARY KEY,
    daily_reminder INTEGER NOT NULL DEFAULT 1,
    streak_risk INTEGER NOT NULL DEFAULT 1,
    daily_goal_missed INTEGER NOT NULL DEFAULT 1,
    level_up INTEGER NOT NULL DEFAULT 1,
    new_badges INTEGER NOT NULL DEFAULT 1,
    exam_ready INTEGER NOT NULL DEFAULT 1,
    missing_reports INTEGER NOT NULL DEFAULT 1,
    report_approved INTEGER NOT NULL DEFAULT 1,
    new_content INTEGER NOT NULL DEFAULT 0,
    maintenance INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    href TEXT,
    read_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notifications_learner
    ON notifications (learner_id, read_at, created_at);

CREATE TABLE IF NOT EXISTS daily_goal_progress (
    learner_id TEXT NOT NULL,
    goal_date TEXT NOT NULL,
    lessons_completed INTEGER NOT NULL DEFAULT 0,
    questions_answered INTEGER NOT NULL DEFAULT 0,
    minutes_studied INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (learner_id, goal_date),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------------
-- Learning tools: formulas, diagnosis, videos, translations
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS formulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    expression TEXT NOT NULL,
    legend_json TEXT NOT NULL DEFAULT '[]',
    example TEXT NOT NULL DEFAULT '',
    difficulty TEXT NOT NULL DEFAULT 'mittel' CHECK (
        difficulty IN ('leicht', 'mittel', 'schwer')
    ),
    source_keys_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS formula_progress (
    learner_id TEXT NOT NULL,
    formula_id INTEGER NOT NULL,
    practiced_count INTEGER NOT NULL DEFAULT 0,
    last_correct INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (learner_id, formula_id),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE,
    FOREIGN KEY (formula_id) REFERENCES formulas (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS diagnosis_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    symptom TEXT NOT NULL,
    options_json TEXT NOT NULL,
    correct_option_index INTEGER NOT NULL CHECK (correct_option_index >= 0),
    explanation TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'mittel',
    estimated_minutes INTEGER NOT NULL DEFAULT 5,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS diagnosis_progress (
    learner_id TEXT NOT NULL,
    case_id INTEGER NOT NULL,
    solved INTEGER NOT NULL DEFAULT 0,
    selected_option_index INTEGER,
    solved_at TEXT,
    PRIMARY KEY (learner_id, case_id),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES diagnosis_cases (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS video_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    instructor TEXT NOT NULL DEFAULT 'Ausbilder',
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    topic TEXT NOT NULL DEFAULT 'allgemein',
    thumbnail_url TEXT NOT NULL DEFAULT '',
    video_url TEXT NOT NULL DEFAULT '',
    chapters_json TEXT NOT NULL DEFAULT '[]',
    next_slug TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS video_progress (
    learner_id TEXT NOT NULL,
    video_id INTEGER NOT NULL,
    watched_seconds INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (learner_id, video_id),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES video_lessons (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL,
    language TEXT NOT NULL,
    translation TEXT NOT NULL,
    definition TEXT NOT NULL DEFAULT '',
    UNIQUE (term, language)
);

CREATE TABLE IF NOT EXISTS content_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    reason TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (learner_id) REFERENCES learners (learner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS media_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    media_type TEXT NOT NULL CHECK (
        media_type IN ('image', 'video', 'pdf', 'audio', 'other')
    ),
    url TEXT NOT NULL,
    uploaded_by TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (uploaded_by) REFERENCES learners (learner_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO schema_migrations (version)
VALUES ('003_platform_features');
