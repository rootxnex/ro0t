import json
import tempfile
import unittest
from pathlib import Path

from cshield.__main__ import main
from cshield.engine import RepositoryScanner
from cshield.reporting import json_report, markdown_report
from cshield.scanners import fingerprint
from cshield.uploads import UploadError, UploadedSource, scan_uploads


class RepositoryScannerTests(unittest.TestCase):
    def test_detects_code_execution_and_redacts_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.py").write_text('value = eval(user_input)\napi_key = "abcdefghijklmnop1234"\n', encoding="utf-8")
            result = RepositoryScanner().scan(root)

        self.assertEqual({item.rule_id for item in result.findings}, {"python-eval", "generic-api-token"})
        secret = next(item for item in result.findings if item.category == "SECRET")
        self.assertNotIn("abcdefghijklmnop1234", json_report(result))
        self.assertEqual(secret.evidence[0].snippet, 'api_key = "[REDACTED]"')
        self.assertIn("Defensive attack scenario", markdown_report(result))

    def test_skips_symlinks_and_large_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root.parent / "outside-cshield-test.py"
            outside.write_text("eval(untrusted)\n", encoding="utf-8")
            try:
                (root / "linked.py").symlink_to(outside)
                (root / "large.py").write_text("x" * 101, encoding="utf-8")
                result = RepositoryScanner(max_file_bytes=100).scan(root)
            finally:
                outside.unlink(missing_ok=True)

        self.assertEqual(result.files_scanned, 0)
        self.assertEqual(result.files_skipped, 2)
        self.assertEqual(result.findings, [])

    def test_fingerprint_is_stable_and_context_sensitive(self):
        first = fingerprint("rule", "a.py", 1, " eval(x) ")
        self.assertEqual(first, fingerprint("rule", "a.py", 1, "eval(x)"))
        self.assertNotEqual(first, fingerprint("rule", "a.py", 2, "eval(x)"))

    def test_json_schema_and_cli_exit_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.py").write_text("eval(user_input)\n", encoding="utf-8")
            result = RepositoryScanner().scan(root)
            report = json.loads(json_report(result))
            self.assertEqual(report["schemaVersion"], "1.0")
            self.assertEqual(main(["scan", directory, "--format", "json", "--fail-on", "high"]), 1)

    def test_upload_scan_rejects_paths_and_scans_content(self):
        with self.assertRaises(UploadError):
            scan_uploads([UploadedSource("../escape.py", b"eval(value)\n")])
        result = scan_uploads([UploadedSource("app.py", b"eval(value)\n")])
        self.assertEqual(result.findings[0].rule_id, "python-eval")


if __name__ == "__main__":
    unittest.main()
