"""Publisher contract tests. All HTTP calls are mocked; no author token is needed."""
from email.parser import BytesParser
from email.policy import default
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from zipfile import ZipFile, ZipInfo

SPEC = importlib.util.spec_from_file_location(
    "upload_curseforge", Path(__file__).resolve().parents[1] / "scripts/upload_curseforge.py"
)
publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publisher)


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.project = {
            "name": "Forever Frost Alert", "version": "0.3.0",
            "curseForgeProjectId": 1796931, "gameFlavor": "Forever",
            "gameVersion": "1.60.1", "interfaceVersion": 16001,
            "uploadFile": "dist/ForeverFrostAlert-0.3.0-forever.zip",
            "addonFolder": "ForeverIcyVeins",
            "changelogFile": "docs/publication/RELEASE_NOTES.md",
        }
        self.release = {"tagName": "v0.3.0", "isDraft": False, "isPrerelease": True, "body": "## Changes\nFrost wings"}
        self.archive = self.root / self.project["uploadFile"]
        self.receipt = self.root / "receipt.json"
        self.metadata_file = self.root / "docs/publication/project-metadata.json"
        self.metadata_file.parent.mkdir(parents=True)
        self.metadata_file.write_text(json.dumps(self.project), encoding="utf-8")
        (self.root / self.project["changelogFile"]).write_text("Fallback notes", encoding="utf-8")
        self.write_zip()
        self.stdout = io.StringIO()
        self.addCleanup(patch.stopall)
        patch("sys.stdout", self.stdout).start()

    def write_zip(self, version="0.3.0", interface=16001, stamp=(2026, 11, 13, 0, 0, 0), lua="-- addon"):
        self.archive.parent.mkdir(exist_ok=True)
        with ZipFile(self.archive, "w") as package:
            package.writestr(ZipInfo("ForeverIcyVeins/ForeverIcyVeins.toc", stamp), f"## Interface: {interface}\n## Version: {version}\nForeverIcyVeins.lua\n")
            package.writestr(ZipInfo("ForeverIcyVeins/ForeverIcyVeins.lua", stamp), lua)

    def test_release_metadata_uses_forever_version_and_correct_release_type(self):
        for prerelease, expected in [(True, "beta"), (False, "release")]:
            with self.subTest(prerelease=prerelease):
                self.release["isPrerelease"] = prerelease
                archive, metadata, identity = publisher.upload_plan(self.root, self.release)
                self.assertEqual(archive, self.archive)
                self.assertEqual(metadata["releaseType"], expected)
                self.assertEqual(metadata["gameVersionNames"], ["1.60.1"])
                self.assertEqual(metadata["changelog"], self.release["body"])
                self.assertEqual(identity["projectId"], 1796931)
        self.release["body"] = ""
        self.assertEqual(publisher.upload_plan(self.root, self.release)[1]["changelog"], "Fallback notes")

    def test_rejects_drafts_missing_flags_and_mismatched_tags(self):
        for changes in [{"isDraft": True}, {"tagName": "v0.2.0"}, {"isPrerelease": "true"}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                publisher.upload_plan(self.root, {**self.release, **changes})

    def test_rejects_zip_with_wrong_version_or_client(self):
        for version, interface in [("0.2.0", 16001), ("0.3.0", 120001)]:
            with self.subTest(version=version, interface=interface):
                self.write_zip(version, interface)
                with self.assertRaises(ValueError):
                    publisher.upload_plan(self.root, self.release)

    def test_fingerprint_ignores_zip_timestamps_but_detects_content_changes(self):
        before = publisher.upload_plan(self.root, self.release)[2]
        self.write_zip(stamp=(2027, 1, 1, 0, 0, 0))
        self.assertEqual(before, publisher.upload_plan(self.root, self.release)[2])
        self.write_zip(lua="-- changed addon")
        self.assertNotEqual(before, publisher.upload_plan(self.root, self.release)[2])

    def test_dry_run_needs_no_token_and_makes_no_request(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(publisher.request, "build_opener") as network:
            publisher.publish(self.root, self.release, self.receipt, dry_run=True)
        network.assert_not_called()
        self.assertFalse(self.receipt.exists())
        self.assertIn("No CurseForge request was sent", self.stdout.getvalue())

    def test_missing_token_stops_before_network(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(publisher.request, "build_opener") as network:
            with self.assertRaisesRegex(ValueError, "Missing CF_API_TOKEN"):
                publisher.publish(self.root, self.release, self.receipt)
        network.assert_not_called()

    def test_upload_sends_multipart_header_token_and_writes_receipt(self):
        token = "test-author-token-never-log"
        with patch.dict(os.environ, {"CF_API_TOKEN": token}), patch.object(publisher.request, "build_opener") as factory:
            factory.return_value.open.return_value.__enter__.return_value = io.BytesIO(b'{"id": 12345}')
            result = publisher.publish(self.root, self.release, self.receipt)
        factory.return_value.open.assert_called_once()
        req = factory.return_value.open.call_args.args[0]
        self.assertEqual(req.full_url, "https://wow.curseforge.com/api/projects/1796931/upload-file")
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.get_header("X-api-token"), token)
        message = BytesParser(policy=default).parsebytes(
            f"Content-Type: {req.get_header('Content-type')}\r\nMIME-Version: 1.0\r\n\r\n".encode() + req.data
        )
        parts = {part.get_param("name", header="content-disposition"): part for part in message.iter_parts()}
        self.assertEqual(json.loads(parts["metadata"].get_payload(decode=True))["gameVersionNames"], ["1.60.1"])
        self.assertEqual(parts["file"].get_payload(decode=True), self.archive.read_bytes())
        self.assertEqual(parts["file"].get_filename(), self.archive.name)
        self.assertNotIn(token, self.stdout.getvalue())
        self.assertNotIn(token.encode(), req.data)
        self.assertEqual(json.loads(self.receipt.read_text()), result)
        self.assertEqual(result["fileId"], 12345)
        self.assertIsInstance(factory.call_args.args[0], publisher.NoRedirect)

    def test_successful_receipt_prevents_duplicate_upload(self):
        identity = publisher.upload_plan(self.root, self.release)[2]
        previous = {**identity, "fileId": 12345, "releaseType": "beta"}
        self.receipt.write_text(json.dumps(previous))
        with patch.object(publisher.request, "build_opener") as network:
            result = publisher.publish(self.root, self.release, self.root / "new.json", self.receipt)
        network.assert_not_called()
        self.assertEqual(result, previous)
        self.assertFalse((self.root / "new.json").exists())

    def test_receipt_for_different_content_is_rejected(self):
        self.receipt.write_text(json.dumps({**publisher.upload_plan(self.root, self.release)[2], "fileId": 12345}))
        self.write_zip(lua="-- changed")
        with patch.object(publisher.request, "build_opener") as network, self.assertRaisesRegex(ValueError, "receipt does not match"):
            publisher.publish(self.root, self.release, self.root / "new.json", self.receipt)
        network.assert_not_called()

    def test_http_failure_does_not_expose_token_or_server_body(self):
        token = "private-test-token"
        failure = HTTPError("https://wow.curseforge.com", 401, token, {}, io.BytesIO(token.encode()))
        with patch.dict(os.environ, {"CF_API_TOKEN": token}), patch.object(publisher.request, "build_opener") as factory:
            factory.return_value.open.side_effect = failure
            with self.assertRaisesRegex(ValueError, "HTTP 401") as caught:
                publisher.publish(self.root, self.release, self.receipt)
        self.assertNotIn(token, str(caught.exception) + self.stdout.getvalue())
        self.assertFalse(self.receipt.exists())

    def test_timeout_is_not_retried(self):
        with patch.dict(os.environ, {"CF_API_TOKEN": "test"}), patch.object(publisher.request, "build_opener") as factory:
            factory.return_value.open.side_effect = TimeoutError()
            with self.assertRaisesRegex(ValueError, "result is unknown"):
                publisher.publish(self.root, self.release, self.receipt)
        factory.return_value.open.assert_called_once()
        self.assertFalse(self.receipt.exists())

    def test_malformed_success_is_not_recorded(self):
        for payload in [b"[]", b'{"id": true}', b'{"id": -1}', b'not json']:
            with self.subTest(payload=payload), patch.dict(os.environ, {"CF_API_TOKEN": "test"}), patch.object(publisher.request, "build_opener") as factory:
                factory.return_value.open.return_value.__enter__.return_value = io.BytesIO(payload)
                with self.assertRaises(ValueError):
                    publisher.publish(self.root, self.release, self.receipt)
                self.assertFalse(self.receipt.exists())


if __name__ == "__main__":
    unittest.main()
