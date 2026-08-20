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

CREATE INDEX IF NOT EXISTS scan_jobs_repository_pr_idx
    ON scan_jobs (github_repository_id, pull_request_number, created_at DESC);
