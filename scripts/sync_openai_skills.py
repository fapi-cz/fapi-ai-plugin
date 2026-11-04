import argparse
import http.client
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import time
from urllib.parse import quote, urlencode
import uuid
import zipfile

import yaml


ROOT = Path(__file__).resolve().parent.parent
MAX_CONTENT_SIZE = 25 * 1024 * 1024
MAX_ARCHIVE_SIZE = 50 * 1024 * 1024


class SyncError(Exception):
    pass


class ApiError(SyncError):
    def __init__(self, status):
        self.status = status
        super().__init__(f"OpenAI Skills API returned HTTP {status}")


class OpenAIClient:
    def __init__(self, api_key, project_id="", organization_id=""):
        self.headers = {"Authorization": "Bearer " + api_key}
        if project_id:
            self.headers["OpenAI-Project"] = project_id
        if organization_id:
            self.headers["OpenAI-Organization"] = organization_id

    def request(self, method, path, archive=None):
        headers = dict(self.headers)
        body = None
        if archive is not None:
            boundary = uuid.uuid4().hex
            headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
            body = (
                f'--{boundary}\r\nContent-Disposition: form-data; name="files"; '
                'filename="skill.zip"\r\nContent-Type: application/zip\r\n\r\n'
            ).encode() + archive + f"\r\n--{boundary}--\r\n".encode()
        connection = http.client.HTTPSConnection("api.openai.com", timeout=30)
        try:
            connection.request(method, "/v1" + path, body=body, headers=headers)
            response = connection.getresponse()
            if response.status != 200:
                raise ApiError(response.status)
            content = response.read(MAX_ARCHIVE_SIZE + 1)
            if len(content) > MAX_ARCHIVE_SIZE:
                raise SyncError("OpenAI skill response exceeds the archive size limit")
            return content if path.endswith("/content") else json.loads(content)
        except (OSError, http.client.HTTPException):
            raise SyncError(
                "OpenAI connection failed; a write may have succeeded. Reconcile remote state before retrying."
            ) from None
        finally:
            connection.close()


def archive_files(content, name):
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        entries = [entry for entry in archive.infolist() if not entry.is_dir()]
        if len(entries) > 500 or sum(entry.file_size for entry in entries) > MAX_CONTENT_SIZE:
            raise SyncError(f"Skill bundle exceeds file/content limits: {name}")
        files = {}
        for entry in entries:
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or ".." in path.parts or path.parts[0] != name:
                raise SyncError(f"Unexpected bundle path for skill: {name}")
            relative = path.relative_to(name).as_posix()
            if relative in files:
                raise SyncError(f"Duplicate bundle file for skill: {name}")
            files[relative] = archive.read(entry)
        return files


def local_bundle(directory):
    if directory.is_symlink():
        raise SyncError("Skill directories must not be symlinks")
    files = {}
    content_size = 0
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise SyncError(f"Skill contains a symlink: {directory.name}")
        if not path.is_file() or path.name == ".DS_Store" or "__pycache__" in path.parts:
            continue
        content_size += path.stat().st_size
        if len(files) >= 500 or content_size > MAX_CONTENT_SIZE:
            raise SyncError(f"Skill bundle exceeds file/content limits: {directory.name}")
        files[path.relative_to(directory).as_posix()] = path.read_bytes()
    if [name for name in files if PurePosixPath(name).name.lower() == "skill.md"] != ["SKILL.md"]:
        raise SyncError(f"Exactly one root SKILL.md is required: {directory.name}")
    manifest = re.match(r"\A---\n(.*?)\n---", files["SKILL.md"].decode(), re.DOTALL)
    metadata = yaml.safe_load(manifest.group(1)) if manifest else None
    if (
        not isinstance(metadata, dict)
        or metadata.get("name") != directory.name
        or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", directory.name) is None
        or not isinstance(metadata.get("description"), str)
        or not metadata["description"].strip()
    ):
        raise SyncError(f"Invalid skill name or description: {directory.name}")
    if len(files) > 500 or sum(map(len, files.values())) > MAX_CONTENT_SIZE:
        raise SyncError(f"Skill bundle exceeds file/content limits: {directory.name}")
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in files.items():
            info = zipfile.ZipInfo(directory.name + "/" + name, (1980, 1, 1, 0, 0, 0))
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED)
    return files, output.getvalue()


def synchronize(skills_dir, registry, client, check=True):
    bundles = {path.name: local_bundle(path) for path in sorted(skills_dir.iterdir()) if path.is_dir()}
    if not bundles or not set(registry).issubset(bundles):
        raise SyncError("A registered skill source is missing or the skills directory is empty")
    if len(set(registry.values())) != len(registry) or any(
        re.fullmatch(r"skill_[A-Za-z0-9]+", skill_id) is None for skill_id in registry.values()
    ):
        raise SyncError("Invalid or duplicate registered skill IDs")
    remote = {}
    after = None
    seen_cursors = set()
    while True:
        query = {"limit": 100, "order": "asc"}
        if after:
            query["after"] = after
        page = client.request("GET", "/skills?" + urlencode(query))
        for skill in page["data"]:
            if skill["name"] not in bundles:
                continue
            if skill["name"] in remote:
                raise SyncError(f"Multiple hosted skills match: {skill['name']}")
            remote[skill["name"]] = skill
        if not page["has_more"]:
            break
        next_after = page["last_id"]
        if not next_after or next_after in seen_cursors:
            raise SyncError("OpenAI skill pagination did not advance")
        seen_cursors.add(next_after)
        after = next_after
    for name, skill_id in registry.items():
        if remote.get(name, {}).get("id") != skill_id:
            raise SyncError(f"Registered ID is missing or different; verify the OpenAI project: {name}")
    plan = []
    for name, (files, archive) in bundles.items():
        skill = remote.get(name)
        action = "create"
        if skill:
            path = f"/skills/{quote(skill['id'], safe='')}/versions/{quote(skill['latest_version'], safe='')}"
            action = "unchanged" if archive_files(client.request("GET", path + "/content"), name) == files else "update"
        plan.append({"name": name, "id": skill["id"] if skill else None,
                     "version": skill["latest_version"] if skill else None, "action": action})
    for item in plan:
        if check or item["action"] == "unchanged":
            continue
        path = "/skills" if item["id"] is None else f"/skills/{quote(item['id'], safe='')}/versions"
        uploaded = client.request("POST", path, archive=bundles[item["name"]][1])
        skill_id = item["id"] or uploaded["id"]
        version = uploaded.get("version", uploaded.get("latest_version"))
        if uploaded.get("name") != item["name"] or not isinstance(version, str):
            raise SyncError(f"Unexpected upload receipt for skill: {item['name']}")
        path = f"/skills/{quote(skill_id, safe='')}/versions/{quote(version, safe='')}"
        for attempt in range(5):
            try:
                client.request("GET", path)
                break
            except ApiError as error:
                if error.status != 404 or attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        if archive_files(client.request("GET", path + "/content"), item["name"]) != bundles[item["name"]][0]:
            raise SyncError(f"Uploaded content verification failed: {item['name']}")
        item.update(id=skill_id, version=version)
    return {
        "changed": any(item["action"] != "unchanged" for item in plan),
        "check_mode": check,
        "skills": plan,
        "fapi_pr_required": [
            {"name": item["name"], "id": item["id"]} for item in plan if item["name"] not in registry
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            raise SyncError("OPENAI_API_KEY is required")
        registry = json.loads((ROOT / "ansible/skills.json").read_text())
        client = OpenAIClient(key, os.environ.get("OPENAI_PROJECT_ID", ""), os.environ.get("OPENAI_ORGANIZATION_ID", ""))
        result = synchronize(ROOT / "plugins/fapi/skills", registry, client, check=not args.apply)
        print(json.dumps(result))
        return 0
    except SyncError as error:
        print(json.dumps({"error": str(error), "writes_may_have_completed": args.apply}))
    except Exception as error:
        print(json.dumps({"error": "Skill sync failed: " + type(error).__name__,
                          "writes_may_have_completed": args.apply}))
    return 1


if __name__ == "__main__":
    sys.exit(main())
