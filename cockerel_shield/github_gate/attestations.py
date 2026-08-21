from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Mapping

SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")


@dataclass(frozen=True)
class AttestationMaterial:
    repository_hash: bytes
    commit_hash: bytes
    policy_hash: bytes
    report_hash: bytes

    def as_hex(self) -> dict[str, str]:
        return {
            "repositoryHash": "0x" + self.repository_hash.hex(),
            "commitHash": "0x" + self.commit_hash.hex(),
            "policyHash": "0x" + self.policy_hash.hex(),
            "reportHash": "0x" + self.report_hash.hex(),
        }


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def attestation_material(
    *, repository_id: int, commit_sha: str, policy: Mapping[str, Any], report: Mapping[str, Any]
) -> AttestationMaterial:
    if not isinstance(repository_id, int) or isinstance(repository_id, bool) or repository_id <= 0:
        raise ValueError("repository ID must be a positive integer")
    if not SHA40.fullmatch(commit_sha):
        raise ValueError("commit SHA must contain 40 hexadecimal characters")
    return AttestationMaterial(
        repository_hash=_hash(f"github-repository:{repository_id}".encode()),
        commit_hash=_hash(bytes.fromhex(commit_sha)),
        policy_hash=_hash(canonical_json(policy)),
        report_hash=_hash(canonical_json(report)),
    )


def verify_report(report: Mapping[str, Any], expected_report_hash: str) -> bool:
    expected = expected_report_hash.removeprefix("0x").lower()
    if len(expected) != 64 or any(character not in "0123456789abcdef" for character in expected):
        return False
    return hashlib.sha256(canonical_json(report)).hexdigest() == expected


def _hash(value: bytes) -> bytes:
    # SHA-256 is used for report portability. The Solidity scan key applies keccak256
    # to the resulting fixed-width hashes.
    return hashlib.sha256(value).digest()
