-- Multi-tenant organisations (Bildungsbetriebe) and class cohorts.

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cohorts (
    cohort_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cohorts_tenant ON cohorts (tenant_id);
