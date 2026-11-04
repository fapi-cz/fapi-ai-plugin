import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_openai_skills import ApiError, OpenAIClient, SyncError, archive_files, local_bundle, main, synchronize


class FakeAPI:
    def __init__(self, skills=(), page_size=100):
        self.skills = list(skills)
        self.page_size = page_size
        self.calls = []
        self.not_ready = 0
        self.ambiguous_write = False

    def request(self, method, path, archive=None):
        self.calls.append((method, path))
        parsed = urlsplit(path)
        parts = parsed.path.strip("/").split("/")
        if method == "GET" and parts == ["skills"]:
            after = parse_qs(parsed.query).get("after", [None])[0]
            start = next((i + 1 for i, skill in enumerate(self.skills) if skill["id"] == after), 0)
            page = self.skills[start:start + self.page_size]
            return {"data": page, "has_more": start + len(page) < len(self.skills),
                    "last_id": page[-1]["id"] if page else None}
        if method == "POST":
            if len(parts) == 1:
                import zipfile
                with zipfile.ZipFile(io.BytesIO(archive)) as uploaded:
                    name = uploaded.namelist()[0].split("/")[0]
                skill = {"id": "skill_new" + str(len(self.skills)), "name": name, "latest_version": "0"}
                self.skills.append(skill)
            else:
                skill = next(skill for skill in self.skills if skill["id"] == parts[1])
            skill["latest_version"] = str(int(skill["latest_version"]) + 1)
            skill["archive"] = archive
            if self.ambiguous_write:
                self.ambiguous_write = False
                raise SyncError("Connection failed after upload")
            return {**skill, "version": skill["latest_version"]}
        skill = next(skill for skill in self.skills if skill["id"] == parts[1])
        if parts[-1] == "content":
            return skill["archive"]
        if self.not_ready:
            self.not_ready -= 1
            raise ApiError(404)
        return {"skill_id": skill["id"], "version": skill["latest_version"]}


class SyncSkillsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def source(self, name, content="Original instructions"):
        directory = self.root / name
        directory.mkdir(exist_ok=True)
        (directory / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test workflow\n---\n{content}\n"
        )
        return directory

    def hosted(self, name, skill_id):
        return {"name": name, "id": skill_id, "latest_version": "1",
                "archive": local_bundle(self.root / name)[1]}

    def test_updates_references_preserves_ids_and_repeated_runs_skip_identical_content(self):
        stable = self.source("fapi-stable")
        changed = self.source("fapi-changed")
        api = FakeAPI([self.hosted(stable.name, "skill_stable"),
                       self.hosted(changed.name, "skill_changed")], page_size=1)
        (changed / "references").mkdir()
        (changed / "references/rules.md").write_text("New delivery workflow")
        self.source("fapi-new")
        registry = {stable.name: "skill_stable", changed.name: "skill_changed"}

        result = synchronize(self.root, registry, api, check=False)

        self.assertTrue(result["changed"])
        self.assertEqual([row["action"] for row in result["skills"]], ["update", "create", "unchanged"])
        self.assertEqual(result["skills"][0]["id"], "skill_changed")
        remote = next(skill for skill in api.skills if skill["id"] == "skill_changed")
        self.assertEqual(archive_files(remote["archive"], changed.name)["references/rules.md"],
                         b"New delivery workflow")
        self.assertTrue(any("after=" in path for _, path in api.calls))
        writes = sum(method == "POST" for method, _ in api.calls)

        repeated = synchronize(self.root, registry, api, check=False)

        self.assertFalse(repeated["changed"])
        self.assertEqual(sum(method == "POST" for method, _ in api.calls), writes)
        self.assertEqual(repeated["fapi_pr_required"], result["fapi_pr_required"])
        self.assertEqual(result["fapi_pr_required"][0]["name"], "fapi-new")
        self.assertIsNotNone(result["fapi_pr_required"][0]["id"])

    def test_check_mode_plans_updates_and_creation_without_any_writes(self):
        self.source("fapi-existing")
        api = FakeAPI([self.hosted("fapi-existing", "skill_existing")])
        self.source("fapi-existing", "Changed instructions")
        self.source("fapi-new")

        result = synchronize(self.root, {"fapi-existing": "skill_existing"}, api)

        self.assertTrue(result["check_mode"])
        self.assertEqual([row["action"] for row in result["skills"]], ["update", "create"])
        self.assertIsNone(result["fapi_pr_required"][0]["id"])
        self.assertTrue(all(method == "GET" for method, _ in api.calls))
        self.assertEqual(api.skills[0]["latest_version"], "1")

    def test_wrong_project_or_duplicate_names_stop_before_any_write(self):
        self.source("fapi-one")
        skill = self.hosted("fapi-one", "skill_one")
        for records in [[], [skill, {**skill, "id": "skill_other"}]]:
            with self.subTest(records=len(records)):
                api = FakeAPI(records)
                with self.assertRaises(SyncError):
                    synchronize(self.root, {"fapi-one": "skill_one"}, api, check=False)
                self.assertFalse(any(method == "POST" for method, _ in api.calls))

    def test_version_visibility_retries_reads_and_ambiguous_writes_are_not_retried(self):
        self.source("fapi-one")
        api = FakeAPI([self.hosted("fapi-one", "skill_one")])
        self.source("fapi-one", "Updated")
        api.not_ready = 2
        with patch("sync_openai_skills.time.sleep") as sleep:
            synchronize(self.root, {"fapi-one": "skill_one"}, api, check=False)
        self.assertEqual(sleep.call_count, 2)
        self.source("fapi-one", "Another update")
        api.ambiguous_write = True
        before = sum(method == "POST" for method, _ in api.calls)
        with self.assertRaises(SyncError):
            synchronize(self.root, {"fapi-one": "skill_one"}, api, check=False)
        self.assertEqual(sum(method == "POST" for method, _ in api.calls), before + 1)
        self.assertFalse(synchronize(self.root, {"fapi-one": "skill_one"}, api, check=False)["changed"])

    def test_symlinks_and_nested_skill_manifests_are_rejected_before_api_access(self):
        directory = self.source("fapi-one")
        target = self.root / "outside.txt"
        target.write_text("Not part of a skill")
        link = directory / "external.txt"
        link.symlink_to(target)
        api = FakeAPI()
        with self.assertRaises(SyncError):
            synchronize(self.root, {}, api)
        self.assertEqual(api.calls, [])
        link.unlink()
        (directory / "references").mkdir()
        (directory / "references/SKILL.md").write_text("Nested manifest")
        with self.assertRaises(SyncError):
            local_bundle(directory)

    def test_transport_and_cli_errors_do_not_expose_credentials_or_retry_writes(self):
        with patch("sync_openai_skills.http.client.HTTPSConnection") as connection:
            connection.return_value.request.side_effect = OSError("secret-value")
            with self.assertRaises(SyncError) as error:
                OpenAIClient("secret-value").request("POST", "/skills", archive=b"zip")
            self.assertNotIn("secret-value", str(error.exception))
            self.assertEqual(connection.return_value.request.call_count, 1)
        output = io.StringIO()
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}), patch.object(sys, "argv", ["sync"]):
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(), 1)
        self.assertEqual(json.loads(output.getvalue())["error"], "OPENAI_API_KEY is required")


if __name__ == "__main__":
    unittest.main()
