import unittest

from github_gate.attestations import attestation_material, canonical_json, verify_report


class AttestationTests(unittest.TestCase):
    def test_canonical_hash_is_stable_across_key_order(self):
        first = {"verdict": "SAFE", "findings": [], "meta": {"b": 2, "a": 1}}
        second = {"meta": {"a": 1, "b": 2}, "findings": [], "verdict": "SAFE"}
        one = attestation_material(repository_id=42, commit_sha="a" * 40, policy={"version": 1}, report=first)
        two = attestation_material(repository_id=42, commit_sha="a" * 40, policy={"version": 1}, report=second)
        self.assertEqual(one, two)
        self.assertEqual(len(one.report_hash), 32)

    def test_verifies_exact_report_and_rejects_mutation(self):
        report = {"scanId": "scan-1", "verdict": "BLOCK"}
        material = attestation_material(repository_id=7, commit_sha="f" * 40, policy={"version": 3}, report=report)
        expected = "0x" + material.report_hash.hex()
        self.assertTrue(verify_report(report, expected))
        self.assertFalse(verify_report({**report, "verdict": "SAFE"}, expected))

    def test_rejects_invalid_identity_material(self):
        with self.assertRaises(ValueError):
            attestation_material(repository_id=0, commit_sha="a" * 40, policy={}, report={})
        with self.assertRaises(ValueError):
            attestation_material(repository_id=1, commit_sha="not-a-sha", policy={}, report={})

    def test_canonical_json_rejects_nan(self):
        with self.assertRaises(ValueError):
            canonical_json({"score": float("nan")})


if __name__ == "__main__":
    unittest.main()
