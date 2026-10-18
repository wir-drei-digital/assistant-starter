import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import PRUEFEN, make_assistant, make_runtime, write

import pruefen


def run_cli(*args, env=None):
    return subprocess.run([sys.executable, str(PRUEFEN), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", env=env)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self._env = os.environ.get("ASSISTENT_RUNTIME")
        make_runtime(self.tmp)

    def tearDown(self):
        if self._env is None:
            os.environ.pop("ASSISTENT_RUNTIME", None)
        else:
            os.environ["ASSISTENT_RUNTIME"] = self._env
        for p in self.tmp.rglob("*"):
            try:
                p.chmod(0o755)
            except OSError:
                pass
        self._tmp.cleanup()

    def problems(self, root):
        return [b for b in pruefen.check(root) if not b.ok]


class CheckTests(Base):
    def test_clean_assistant_has_no_findings(self):
        root = make_assistant(self.tmp)
        befunde = pruefen.check(root)
        self.assertTrue(befunde)
        self.assertEqual([b for b in befunde if not b.ok], [])
        result = run_cli(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_claude_md_symlink_and_import_both_ok(self):
        for mode in ("symlink", "import"):
            root = make_assistant(self.tmp / mode, claude=mode)
            self.assertEqual(self.problems(root), [], mode)

    def test_claude_md_missing_or_wrong_is_finding(self):
        root = make_assistant(self.tmp / "missing", claude="missing")
        found = self.problems(root)
        self.assertEqual(len(found), 1)
        self.assertIn("CLAUDE.md", found[0].punkt + found[0].hinweis)

        root = make_assistant(self.tmp / "wrong", claude="missing")
        write(root / "CLAUDE.md", "# Eigene Karte\n")
        found = self.problems(root)
        self.assertEqual(len(found), 1)
        self.assertIn("CLAUDE.md", found[0].punkt + found[0].hinweis)

    def test_missing_required_file(self):
        for name in ("AGENTS.md", "CONTEXT.md", "support.md", "VERSION", "CHANGELOG.md"):
            root = make_assistant(self.tmp / name.replace(".", "_"))
            if name == "AGENTS.md":
                (root / "CLAUDE.md").unlink()
                write(root / "CLAUDE.md", "@AGENTS.md\n")
            (root / name).unlink()
            found = self.problems(root)
            naming = [b for b in found if name in b.punkt + b.hinweis]
            self.assertEqual(len(naming), 1, (name, found))
            if name != "CONTEXT.md":
                self.assertEqual(len(found), 1, (name, found))

    def test_router_row_without_folder(self):
        root = make_assistant(self.tmp)
        with open(root / "CONTEXT.md", "a", encoding="utf-8") as f:
            f.write("| Kommunikation | `02_kommunikation/` | geplant |\n")
        found = self.problems(root)
        self.assertEqual(len(found), 1, found)
        self.assertIn("02_kommunikation/", found[0].hinweis)

        root = make_assistant(self.tmp / "b")
        with open(root / "01_finanzen" / "CONTEXT.md", "a", encoding="utf-8") as f:
            f.write("| Bexio | `workflows/bexio/` | geplant |\n")
        found = self.problems(root)
        self.assertEqual(len(found), 1, found)
        self.assertIn("workflows/bexio/", found[0].hinweis)

    def test_area_folder_without_row(self):
        root = make_assistant(self.tmp)
        (root / "02_kommunikation").mkdir()
        write(root / "02_kommunikation" / "CONTEXT.md",
              "# K\n\n| Aufgabe | Ordner | Status |\n|---|---|---|\n")
        found = self.problems(root)
        self.assertEqual(len(found), 1, found)
        self.assertIn("02_kommunikation", found[0].hinweis)

        root = make_assistant(self.tmp / "b")
        write(root / "01_finanzen" / "workflows" / "bexio" / "CONTEXT.md", "# bexio\n")
        found = self.problems(root)
        self.assertEqual(len(found), 1, found)
        self.assertIn("01_finanzen/workflows/bexio", found[0].hinweis)

    def test_workflow_without_context_md(self):
        root = make_assistant(self.tmp)
        (root / "01_finanzen" / "workflows" / "belege" / "CONTEXT.md").unlink()
        found = self.problems(root)
        self.assertEqual(len(found), 1, found)
        self.assertIn("01_finanzen/workflows/belege", found[0].hinweis)

    def test_router_table_missing_or_malformed(self):
        cases = {
            "missing": "# Router\n\nKeine Tabelle hier.\n",
            "header": "# Router\n\n| Aufgabe | Ordner |\n|---|---|\n| Pflege | `x/` |\n",
            "row": "# Router\n\n| Aufgabe | Ordner | Status |\n|---|---|---|\n| kaputt | `01_finanzen/` |\n",
            "cell": "# Router\n\n| Aufgabe | Ordner | Status |\n|---|---|---|\n| Finanzen | 01_finanzen | aktiv |\n",
            "status": "# Router\n\n| Aufgabe | Ordner | Status |\n|---|---|---|\n| Finanzen | `01_finanzen/` | fertig |\n",
            "two": "# R\n\n| Aufgabe | Ordner | Status |\n|---|---|---|\n\n| Aufgabe | Ordner | Status |\n|---|---|---|\n",
        }
        for case, text in cases.items():
            root = make_assistant(self.tmp / case, areas={})
            write(root / "CONTEXT.md", text)
            if case in ("row", "cell", "status"):
                (root / "01_finanzen").mkdir()
                write(root / "01_finanzen" / "CONTEXT.md", "# F\n\n| Aufgabe | Ordner | Status |\n|---|---|---|\n")
            try:
                found = self.problems(root)
            except Exception as exc:  # pragma: no cover - the point of the test
                self.fail(f"{case}: exception {exc!r}")
            self.assertEqual(len(found), 1, (case, found))
            self.assertIn("CONTEXT.md", found[0].hinweis, case)

    def test_secret_patterns(self):
        root = make_assistant(self.tmp)
        bad = [".env", "x.env", "bexio-token.txt", "api-key.txt", "Passwort.docx"]
        good = ["tokenizer-notizen.md", "geheimnisvoll.md"]
        for name in bad + good:
            write(root / "01_finanzen" / "workflows" / "belege" / name, "x")
        os.makedirs(root / ".git", exist_ok=True)
        write(root / ".git" / "secret-token.txt", "x")
        found = self.problems(root)
        self.assertEqual(len(found), 1, found)
        for name in bad:
            self.assertIn(name, found[0].hinweis)
        for name in good + ["secret-token.txt"]:
            self.assertNotIn(name, found[0].hinweis)
        for name in bad:
            self.assertTrue(pruefen.verdaechtig(name), name)
        for name in good:
            self.assertFalse(pruefen.verdaechtig(name), name)

    def test_paths_with_spaces_umlauts_and_crlf(self):
        base = self.tmp / "OneDrive - Firma"
        root = make_assistant(base, name="Zoë Assistent", newline="\r\n", claude="import",
                              areas={"01_finanzen": ["belege", "bexio"], "02_kommunikation": ["schreiben"]})
        self.assertEqual(self.problems(root), [])
        result = run_cli(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_python_env_check(self):
        """A missing venv is information, not a finding: the assistant works without it."""
        root = make_assistant(self.tmp)
        make_runtime(self.tmp / "leer", venv=False)
        self.assertEqual(self.problems(root), [])
        python = [b for b in pruefen.check(root) if b.punkt.startswith("Python")]
        self.assertEqual(len(python), 1)
        self.assertIn("ohne Python", python[0].hinweis)
        result = run_cli(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stdout, r"(?m)^✓ Python.*ohne Python")
        os.environ["ASSISTENT_RUNTIME"] = str(self.tmp / "runtime")
        self.assertEqual(self.problems(root), [])
        python = [b for b in pruefen.check(root) if b.punkt.startswith("Python")]
        self.assertEqual(python[0].hinweis, "")

    def test_runtime_dir_platform_defaults(self):
        os.environ.pop("ASSISTENT_RUNTIME")
        home = Path.home()
        self.assertEqual(pruefen.runtime_dir("darwin"), home / "Library/Application Support/assistent")
        self.assertEqual(pruefen.runtime_dir("linux"), home / ".local/share/assistent")
        os.environ["LOCALAPPDATA"] = str(self.tmp / "local")
        self.assertEqual(pruefen.runtime_dir("win32"), self.tmp / "local" / "assistent")

    def test_report_is_german_and_has_no_traceback_on_unreadable_file(self):
        root = make_assistant(self.tmp)
        (root / "01_finanzen" / "CONTEXT.md").write_bytes(b"\xff\xfe kaputt \x80\n")
        (root / "CONTEXT.md").chmod(0)
        if os.access(root / "CONTEXT.md", os.R_OK):
            self.skipTest("running as a user who can read everything")
        result = run_cli(root)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        self.assertIn("nicht lesbar", result.stdout)
        self.assertIn("support.md", result.stdout)
        self.assertRegex(result.stdout, r"(?m)^✗ ")
        self.assertRegex(result.stdout, r"(?m)^✓ ")

    def test_no_write_in_default_mode(self):
        root = make_assistant(self.tmp)

        def snapshot():
            return {str(p): (p.lstat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
                    for p in sorted(root.rglob("*"))}

        before = snapshot()
        run_cli(root)
        pruefen.check(root)
        self.assertEqual(before, snapshot())


class IstAssistentTests(Base):
    def test_ist_assistent_detects_existing(self):
        empty = self.tmp / "leer"
        empty.mkdir()
        (empty / ".DS_Store").write_text("x")
        (empty / "desktop.ini").write_text("x")
        self.assertEqual(pruefen.ist_assistent(empty), "leer")

        other = self.tmp / "fremd"
        other.mkdir()
        (other / "Steuern 2025.pdf").write_text("x")
        self.assertEqual(pruefen.ist_assistent(other), "fremd")

        half = make_assistant(self.tmp / "halb", manifest=False)
        self.assertEqual(pruefen.ist_assistent(half), "angefangen")
        result = run_cli("ist-assistent", half)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "angefangen"))

        only_map = self.tmp / "nur-karte"
        only_map.mkdir()
        (only_map / "AGENTS.md").write_text("# Karte\n")
        self.assertEqual(pruefen.ist_assistent(only_map), "fremd")

        root = make_assistant(self.tmp)
        self.assertEqual(pruefen.ist_assistent(root), "assistent")
        result = run_cli("ist-assistent", root)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "assistent"))
        result = run_cli("ist-assistent", empty)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "leer"))


class ManifestTests(Base):
    def test_manifest_written_and_only_listed_files(self):
        root = make_assistant(self.tmp, manifest=False)
        write(root / "_marke" / "voice.md", "x")
        write(root / ".claude" / "skills" / "eigener-skill" / "SKILL.md", "x")
        write(root / ".claude" / "skills" / "pflege" / "references" / "strukturcheck.md", "y")
        path = pruefen.write_manifest(root, "1.0.0")
        self.assertEqual(path, root / ".claude" / "assistent-manifest.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "1.0.0")
        self.assertRegex(data["erstellt"], r"^\d{4}-\d{2}-\d{2}$")
        expected = {
            "AGENTS.md", "CONTEXT.md", "support.md", "pruefen.py", "VERSION",
            ".claude/skills/pflege/SKILL.md",
            ".claude/skills/pflege/references/strukturcheck.md",
            ".claude/skills/workflow-builder/SKILL.md",
        }
        self.assertEqual(set(data["dateien"]), expected)
        for rel, digest in data["dateien"].items():
            self.assertEqual(digest, "sha256:" + hashlib.sha256((root / rel).read_bytes()).hexdigest())
        self.assertFalse(any(k.startswith(("01_", "_marke")) for k in data["dateien"]))

        # update keeps the creation date and moves the version
        data["erstellt"] = "2026-01-01"
        path.write_text(json.dumps(data), encoding="utf-8")
        write(root / "support.md", "neu\n")
        result = run_cli("manifest", root, "--version", "1.1.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual((data["version"], data["erstellt"]), ("1.1.0", "2026-01-01"))
        self.assertEqual(data["dateien"]["support.md"],
                         "sha256:" + hashlib.sha256(b"neu\n").hexdigest())

    def test_manifest_covers_agents_skill_folder(self):
        root = make_assistant(self.tmp, skills=".agents/skills", manifest=False)
        data = json.loads(pruefen.write_manifest(root, "1.0.0").read_text(encoding="utf-8"))
        self.assertIn(".agents/skills/pflege/SKILL.md", data["dateien"])
        self.assertEqual(self.problems(root), [])

    def test_manifest_rejects_bad_version(self):
        root = make_assistant(self.tmp, manifest=False)
        result = run_cli("manifest", root, "--version", "eins")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr + result.stdout)
        self.assertFalse((root / ".claude" / "assistent-manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
