import json
import unittest

from github_gate.checks import completed_check_payload
from github_gate.delivery import MemoryDeliveryStore
from github_gate.diffs import added_lines
from github_gate.diff_rules import scan_changed_lines
from github_gate.service import GitHubWebhookService
from github_gate.verdicts import Disposition, FindingInput, Policy, RulePolicy, Verdict, evaluate_verdict
from github_gate.webhooks import WebhookError, parse_github_webhook, sign_payload


class WebhookTests(unittest.TestCase):
    secret = "test-secret"

    def request(self, *, action="opened", draft=False, signature=True):
        body = json.dumps({
            "action": action,
            "number": 7,
            "repository": {"id": 42},
            "pull_request": {"draft": draft, "head": {"sha": "a" * 40}},
            "installation": {"id": 99},
        }).encode()
        headers = {
            "Content-Type": "application/json",
            "X-GitHub-Delivery": "delivery-1",
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": sign_payload(self.secret, body) if signature else "sha256=bad",
        }
        return body, headers

    def test_verifies_and_classifies_scan_event(self):
        body, headers = self.request()
        event = parse_github_webhook(secret=self.secret, headers=headers, body=body)
        self.assertTrue(event.should_scan)
        self.assertEqual(event.scan_key, f"github:42:pr:7:sha:{'a' * 40}")
        self.assertEqual(event.installation_id, 99)

    def test_rejects_invalid_signature(self):
        body, headers = self.request(signature=False)
        with self.assertRaises(WebhookError):
            parse_github_webhook(secret=self.secret, headers=headers, body=body)

    def test_skips_draft_until_ready(self):
        body, headers = self.request(draft=True)
        self.assertFalse(parse_github_webhook(secret=self.secret, headers=headers, body=body).should_scan)
        body, headers = self.request(action="ready_for_review", draft=True)
        self.assertTrue(parse_github_webhook(secret=self.secret, headers=headers, body=body).should_scan)

    def test_delivery_store_accepts_once(self):
        store = MemoryDeliveryStore()
        self.assertTrue(store.accept_once("delivery-1"))
        self.assertFalse(store.accept_once("delivery-1"))


class VerdictTests(unittest.TestCase):
    def setUp(self):
        self.policy = Policy("Balanced", 1, {
            "private-key": RulePolicy(Disposition.BLOCK, "HIGH"),
            "shell": RulePolicy(Disposition.REVIEW, "MEDIUM"),
        })

    def finding(self, fingerprint, rule, confidence="HIGH"):
        return FindingInput(fingerprint, rule, "HIGH", confidence)

    def test_block_takes_priority_and_maps_to_failed_check(self):
        result = evaluate_verdict([self.finding("a", "shell"), self.finding("b", "private-key")], self.policy)
        self.assertEqual(result.verdict, Verdict.BLOCK)
        payload = completed_check_payload(result, details_url="https://example.test/scans/1", head_sha="a" * 40)
        self.assertEqual(payload["conclusion"], "failure")
        self.assertEqual(payload["output"]["title"], "Block")

    def test_review_and_safe_outcomes_are_transparent(self):
        review = evaluate_verdict([self.finding("a", "shell")], self.policy)
        self.assertEqual(review.verdict, Verdict.REVIEW_REQUIRED)
        self.assertEqual(review.github_conclusion, "neutral")
        safe = evaluate_verdict([self.finding("a", "shell", "LOW")], self.policy)
        self.assertEqual(safe.verdict, Verdict.SAFE)

    def test_exception_removes_finding_from_verdict(self):
        result = evaluate_verdict([self.finding("b", "private-key")], self.policy, excepted_fingerprints={"b"})
        self.assertEqual(result.verdict, Verdict.SAFE)
        self.assertEqual(result.ignored_fingerprints, ("b",))


class DiffTests(unittest.TestCase):
    def test_maps_added_lines_to_destination_numbers(self):
        patch = """@@ -8,3 +8,4 @@ def run():
 context()
-old_value = 1
+new_value = eval(user_input)
+audit(new_value)
 return new_value
"""
        lines = added_lines("app.py", patch)
        self.assertEqual([(line.line, line.text) for line in lines], [
            (9, "new_value = eval(user_input)"),
            (10, "audit(new_value)"),
        ])

    def test_enforces_changed_line_limit(self):
        patch = "@@ -0,0 +1,3 @@\n+a\n+b\n+c"
        with self.assertRaises(ValueError):
            added_lines("app.py", patch, max_lines=2)

    def test_scans_only_added_lines_and_preserves_github_line(self):
        patch = "@@ -1,2 +1,2 @@\n-safe = 1\n+value = eval(user_input)"
        findings = scan_changed_lines(added_lines("app.py", patch))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "python-eval")
        self.assertEqual(findings[0].line, 1)


class WebhookServiceTests(WebhookTests):
    class Queue:
        def __init__(self):
            self.events = []

        def enqueue(self, event):
            self.events.append(event)
            return event.scan_key

    def test_accepts_once_and_queues_eligible_event(self):
        body, headers = self.request()
        queue = self.Queue()
        service = GitHubWebhookService(secret=self.secret, deliveries=MemoryDeliveryStore(), queue=queue)
        first = service.accept(headers, body)
        second = service.accept(headers, body)
        self.assertTrue(first.scan_queued)
        self.assertFalse(first.duplicate)
        self.assertTrue(second.duplicate)
        self.assertFalse(second.scan_queued)
        self.assertEqual(len(queue.events), 1)


if __name__ == "__main__":
    unittest.main()
