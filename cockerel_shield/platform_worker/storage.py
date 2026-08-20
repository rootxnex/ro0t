from __future__ import annotations

import uuid

from psycopg import connect

from github_gate.diff_rules import DiffFinding
from github_gate.verdicts import VerdictResult


class PostgresScanStore:
    def __init__(self, database_url: str):
        self._database_url = database_url

    def start(self, *, scan_key: str, delivery_id: str, repository_id: int, pr_number: int, head_sha: str) -> str:
        scan_id = str(uuid.uuid4())
        with connect(self._database_url) as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO scan_jobs
                    (id, scan_key, delivery_id, github_repository_id, pull_request_number, head_sha, status, started_at)
                VALUES (%s, %s, %s, %s, %s, %s, 'scanning', now())
                ON CONFLICT (scan_key) DO UPDATE SET status = 'scanning', started_at = now()
                RETURNING id
                """,
                (scan_id, scan_key, delivery_id, repository_id, pr_number, head_sha),
            )
            return str(cursor.fetchone()[0])

    def complete(self, *, scan_id: str, result: VerdictResult, findings: list[DiffFinding], check_run_id: int) -> None:
        with connect(self._database_url) as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE scan_jobs SET status='completed', verdict=%s, check_run_id=%s, completed_at=now() WHERE id=%s",
                (result.verdict.value, check_run_id, scan_id),
            )
            cursor.executemany(
                """
                INSERT INTO scan_findings
                    (id, scan_id, fingerprint, rule_id, severity, confidence, path, line_number, evidence, description, remediation, verdict_impact)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (scan_id, fingerprint) DO NOTHING
                """,
                [(
                    str(uuid.uuid4()), scan_id, item.fingerprint, item.rule_id, item.severity,
                    item.confidence, item.path, item.line, item.evidence, item.description,
                    item.remediation,
                    "BLOCK" if item.fingerprint in result.blocking_fingerprints else "REVIEW",
                ) for item in findings],
            )
