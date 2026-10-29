"""The formula pins the resolver's dependencies and retains tested resources."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("update_formula", Path(__file__).resolve().parents[1] / ".github/scripts/update_formula.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


def release(name, version):
    return {"info": {"name": name, "version": version}, "urls": [
        {"packagetype": "sdist", "url": f"https://files.pythonhosted.org/{name}-{version}.tar.gz",
         "digests": {"sha256": "a" * 64}}]}


class UpdateFormulaTest(unittest.TestCase):
    def test_resolved_resources_are_pinned_without_installing_packages(self):
        report = {"install": [{"metadata": {"name": name, "version": version}} for name, version in
                              [("party-continuum", "0.10.0"), ("httpx", "0.28.1"), ("httpcore", "1.0.9")]]}
        with patch.object(updater.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(report))) as run, patch.object(updater, "metadata", side_effect=release):
            text = updater.resources("0.10.0")
        self.assertIn('resource "httpx"', text)
        self.assertIn('resource "httpcore"', text)
        self.assertNotIn('resource "party-continuum"', text)
        self.assertIn('sha256 "' + "a" * 64 + '"', text)
        self.assertIn("--dry-run", run.call_args.args[0])
        self.assertIn("--only-binary=:all:", run.call_args.args[0])

    def test_same_release_preserves_already_tested_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            formula = Path(tmp) / "continuum.rb"
            data = release("party-continuum", "0.10.0")
            formula.write_text('url "' + data["urls"][0]["url"] + '"\nsha256 "' + "a" * 64 + '"\nvirtualenv_install_with_resources\n')
            before = formula.read_text()
            with patch.object(updater, "FORMULA", formula), patch.object(updater, "metadata", return_value=data), patch.object(updater, "resources") as resolve:
                self.assertEqual(updater.main(), 0)
            resolve.assert_not_called()
            self.assertEqual(formula.read_text(), before)

    def test_missing_declared_transport_cannot_publish_a_formula(self):
        report = {"install": [{"metadata": {"name": "party-continuum", "version": "0.10.0"}}]}
        with patch.object(updater.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(report))):
            with self.assertRaisesRegex(ValueError, "HTTPX"):
                updater.resources("0.10.0")


if __name__ == "__main__":
    unittest.main()
