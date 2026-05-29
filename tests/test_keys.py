"""Key resolution tests.

load_key() precedence: cli → env → file. scrub() must redact the key
from any string that contains it. config_dir() must vary per tool."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gungnir.keys import config_dir, key_path, load_key, save_key, scrub  # noqa: E402


class KeysTests(unittest.TestCase):

    def test_config_dir_varies_by_tool(self):
        a = config_dir("muninn")
        b = config_dir("heimdall")
        self.assertNotEqual(a, b)
        self.assertTrue(str(a).endswith("muninn"))
        self.assertTrue(str(b).endswith("heimdall"))

    def test_load_key_precedence_cli_wins(self):
        with mock.patch.dict(os.environ, {"WDGWARS_API_KEY": "from_env"}):
            self.assertEqual(load_key("muninn", cli_key="from_cli"), "from_cli")

    def test_load_key_env_when_no_cli(self):
        with mock.patch.dict(os.environ, {"WDGWARS_API_KEY": "from_env"}):
            self.assertEqual(load_key("muninn", cli_key=None), "from_env")

    def test_load_key_empty_when_nothing_set(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch("gungnir.keys.key_path") as kp:
            kp.return_value = Path(tempfile.gettempdir()) / "does-not-exist.key"
            self.assertEqual(load_key("muninn", cli_key=None), "")

    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "api.key"
            with mock.patch("gungnir.keys.key_path", return_value=fake), \
                 mock.patch.dict(os.environ, {}, clear=True):
                save_key("muninn", "secret-key-xyz")
                self.assertEqual(load_key("muninn"), "secret-key-xyz")

    def test_scrub_redacts_key(self):
        out = scrub("error: bad key fooBARbazQUUX", "fooBARbazQUUX")
        self.assertNotIn("fooBARbazQUUX", out)
        self.assertIn("fooB", out)  # prefix preserved
        self.assertIn("QUUX", out)  # suffix preserved

    def test_scrub_noop_when_key_absent(self):
        self.assertEqual(scrub("plain text", "missing-key-12345"), "plain text")

    def test_scrub_redacts_short_key_when_present(self):
        """Short keys ARE redacted when they appear in the text. The old
        Muninn behavior (no redaction for len <= 8) protected against
        nothing real and could leak short test keys."""
        out = scrub("error: bad key abcd1234 rejected", "abcd1234")
        self.assertNotIn("abcd1234", out)
        # Short keys redact to a literal "…" rather than first-4/last-4
        # (which would expose most of an 8-char secret).
        self.assertIn("…", out)

    def test_scrub_noop_on_empty_key(self):
        """An empty key string is a no-op — there's nothing to redact."""
        self.assertEqual(scrub("plain text", ""), "plain text")


if __name__ == "__main__":
    unittest.main()
