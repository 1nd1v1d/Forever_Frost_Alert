"""Publish a tested release ZIP through CurseForge's author API (stdlib only)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib import error, request
import uuid
from zipfile import BadZipFile, ZipFile

API_BASE = "https://wow.curseforge.com"


def upload_plan(root, release):
    root = Path(root).resolve()
    project = json.loads((root / "docs/publication/project-metadata.json").read_text(encoding="utf-8"))
    version = project["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?", version):
        raise ValueError("Invalid project version")
    if release.get("tagName") != f"v{version}" or release.get("isDraft") is not False:
        raise ValueError("The published release tag must match the project version exactly")
    if not isinstance(release.get("isPrerelease"), bool):
        raise ValueError("Release must declare whether it is a pre-release")
    project_id = project["curseForgeProjectId"]
    if type(project_id) is not int or project_id <= 0:
        raise ValueError("A positive CurseForge project ID is required")
    archive = (root / project["uploadFile"]).resolve()
    if not archive.is_relative_to(root) or not archive.is_file():
        raise ValueError("The addon ZIP must exist inside the release checkout")
    addon_folder = project["addonFolder"]
    fingerprint = hashlib.sha256()
    with ZipFile(archive) as package:
        toc = package.read(f"{addon_folder}/{addon_folder}.toc").decode("utf-8")
        if not re.search(rf"^## Version: {re.escape(version)}\s*$", toc, re.MULTILINE):
            raise ValueError("ZIP version does not match the release")
        if not re.search(rf"^## Interface: {project['interfaceVersion']}\s*$", toc, re.MULTILINE):
            raise ValueError("ZIP interface does not match the declared client")
        # Ignore ZIP timestamps so reruns of an unchanged tag have the same identity.
        for name in sorted(package.namelist()):
            fingerprint.update(name.encode("utf-8") + b"\0")
            fingerprint.update(hashlib.sha256(package.read(name)).digest())
    changelog = release.get("body") or (root / project["changelogFile"]).read_text(encoding="utf-8")
    release_type = "beta" if release["isPrerelease"] else "release"
    metadata = {
        "displayName": f"{project['name']} {version} - {project['gameFlavor']} ({release_type.title()})",
        "changelog": changelog,
        "changelogType": "markdown",
        "gameVersionNames": [project["gameVersion"]],
        "releaseType": release_type,
    }
    identity = {
        "projectId": project_id,
        "tag": release["tagName"],
        "version": version,
        "packageContentSha256": fingerprint.hexdigest(),
    }
    return archive, metadata, identity


def multipart_body(archive, metadata):
    boundary = f"ForeverFrostAlert-{uuid.uuid4().hex}"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"metadata\"\r\n"
        "Content-Type: application/json; charset=utf-8\r\n\r\n"
    ).encode() + json.dumps(metadata, ensure_ascii=False).encode("utf-8")
    body += (
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
        f"filename=\"{archive.name}\"\r\nContent-Type: application/zip\r\n\r\n"
    ).encode() + archive.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward an author token through an unexpected HTTP redirect.
        return None


def publish(root, release, receipt_path, existing_receipt=None, dry_run=False):
    archive, metadata, identity = upload_plan(root, release)
    print(f"Project {identity['projectId']}: {archive.name} ({metadata['releaseType']}, {metadata['gameVersionNames'][0]})")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    if existing_receipt and Path(existing_receipt).is_file():
        previous = json.loads(Path(existing_receipt).read_text(encoding="utf-8"))
        if any(previous.get(key) != value for key, value in identity.items()) or type(previous.get("fileId")) is not int or previous["fileId"] <= 0:
            raise ValueError("Existing upload receipt does not match this project, tag and package")
        print(f"Already uploaded as CurseForge file {previous['fileId']}; skipping duplicate upload.")
        return previous
    if dry_run:
        print("Dry run complete. No CurseForge request was sent; no token is required.")
        return None
    token = os.environ.get("CF_API_TOKEN", "").strip()
    if not token:
        raise ValueError("Missing CF_API_TOKEN. Add it as a GitHub Actions repository secret, or use dry-run mode.")
    body, content_type = multipart_body(archive, metadata)
    req = request.Request(
        f"{API_BASE}/api/projects/{identity['projectId']}/upload-file",
        data=body,
        headers={"X-Api-Token": token, "Content-Type": content_type},
        method="POST",
    )
    # One POST only. A timed-out upload may already have reached CurseForge.
    try:
        with request.build_opener(NoRedirect()).open(req, timeout=120) as response:
            result = json.load(response)
    except error.HTTPError as exc:
        raise ValueError(f"CurseForge rejected the upload (HTTP {exc.code}). Check the token, permissions and author dashboard.") from None
    except (error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        raise ValueError("Upload result is unknown. Check the CurseForge file list before retrying; no automatic retry was made.") from None
    if not isinstance(result, dict) or type(result.get("id")) is not int or result["id"] <= 0:
        raise ValueError("No valid file ID was returned. Check CurseForge before retrying.")
    receipt = {**identity, "fileId": result["id"], "releaseType": metadata["releaseType"]}
    print(f"Upload accepted: CurseForge file {result['id']}. Moderation may still be pending.")
    receipt_path = Path(receipt_path)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--release-json", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, default=Path("dist/curseforge-upload.json"))
    parser.add_argument("--existing-receipt", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        release = json.loads(args.release_json.read_text(encoding="utf-8"))
        publish(args.root, release, args.receipt, args.existing_receipt, args.dry_run)
    except (ValueError, KeyError, OSError, BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
