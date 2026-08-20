CREATE TABLE IF NOT EXISTS webhook_deliveries (
    delivery_id varchar(100) PRIMARY KEY,
    event varchar(100),
    action varchar(100),
    status varchar(32) NOT NULL,
    received_at timestamptz NOT NULL DEFAULT now(),
    processed_at timestamptz
);

CREATE TABLE IF NOT EXISTS scan_jobs (
    id uuid PRIMARY KEY,
    scan_key text NOT NULL UNIQUE,
    delivery_id varchar(100) NOT NULL REFERENCES webhook_deliveries(delivery_id),
    github_repository_id bigint NOT NULL,
    pull_request_number integer NOT NULL,
    head_sha char(40) NOT NULL,
    status varchar(32) NOT NULL DEFAULT 'queued',
    created_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz,
    completed_at timestamptz,
    error_code varchar(100)
);

ALTER TABLE scan_jobs ADD COLUMN IF NOT EXISTS verdict varchar(32);
ALTER TABLE scan_jobs ADD COLUMN IF NOT EXISTS check_run_id bigint;

CREATE TABLE IF NOT EXISTS scan_findings (
    id uuid PRIMARY KEY,
    scan_id uuid NOT NULL REFERENCES scan_jobs(id) ON DELETE CASCADE,
    fingerprint char(64) NOT NULL,
    rule_id varchar(100) NOT NULL,
    severity varchar(20) NOT NULL,
    confidence varchar(20) NOT NULL,
    path text NOT NULL,
    line_number integer NOT NULL,
    evidence text NOT NULL,
    description text NOT NULL,
    remediation text NOT NULL,
    verdict_impact varchar(20) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (scan_id, fingerprint)
);

CREATE INDEX IF NOT EXISTS scan_jobs_repository_pr_idx
    ON scan_jobs (github_repository_id, pull_request_number, created_at DESC);
