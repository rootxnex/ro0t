import unittest
from unittest.mock import patch

from cshield.linkscan import LinkScanError, _github_parts, _public_url


class LinkScanValidationTests(unittest.TestCase):
    def test_parses_supported_github_links(self):
        self.assertEqual(_github_parts("https://github.com/acme/widget"), ("acme", "widget", "main"))
        self.assertEqual(_github_parts("https://github.com/acme/widget/tree/dev"), ("acme", "widget", "dev"))

    def test_rejects_non_github_source_link(self):
        with self.assertRaises(LinkScanError):
            _github_parts("https://example.com/acme/widget")

    @patch("cshield.linkscan.socket.getaddrinfo")
    def test_blocks_private_network_targets(self, getaddrinfo):
        getaddrinfo.return_value = [(2, 1, 6, "", ("127.0.0.1", 443))]
        with self.assertRaises(LinkScanError):
            _public_url("https://localhost/admin")

    @patch("cshield.linkscan.socket.getaddrinfo")
    def test_accepts_public_web_target(self, getaddrinfo):
        getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 443))]
        self.assertEqual(_public_url("https://example.com/path"), "https://example.com/path")


if __name__ == "__main__":
    unittest.main()
