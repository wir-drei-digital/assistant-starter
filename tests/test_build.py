import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from helpers import REPO


def build(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(repo / "scripts" / "build.py")],
                          capture_output=True, text=True, encoding="utf-8")


class BuildTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name) / "repo"
        shutil.copytree(REPO, self.repo, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"))
        self.version = (REPO / "VERSION").read_text(encoding="utf-8").strip()

    def tearDown(self):
        self._tmp.cleanup()

    def zip_path(self) -> Path:
        return self.repo / "dist" / f"assistent-einrichten-v{self.version}.zip"

    def test_zip_root_is_skill_folder(self):
        result = build(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with zipfile.ZipFile(self.zip_path()) as z:
            names = z.namelist()
        self.assertIn("assistent-einrichten/SKILL.md", names)
        self.assertIn("assistent-einrichten/vorlage/pruefen.py", names)
        self.assertTrue(all(n.startswith("assistent-einrichten/") for n in names), names)
        self.assertFalse(any("__pycache__" in n or n.endswith(".DS_Store") for n in names))

    def test_zip_contains_version_matching_repo_version(self):
        self.assertRegex(self.version, r"^\d+\.\d+\.\d+$")
        result = build(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with zipfile.ZipFile(self.zip_path()) as z:
            self.assertEqual(z.read("assistent-einrichten/vorlage/VERSION").decode().strip(), self.version)
        self.assertFalse((self.repo / "assistent-einrichten" / "vorlage" / "VERSION").exists())

    def test_stable_zip_has_same_content(self):
        """The website links releases/latest/download/assistent-einrichten.zip."""
        result = build(self.repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        stable = self.repo / "dist" / "assistent-einrichten.zip"
        self.assertTrue(stable.is_file())
        self.assertEqual(stable.read_bytes(), self.zip_path().read_bytes())

    def test_release_workflow(self):
        text = (REPO / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        for runner in ("ubuntu-latest", "macos-latest", "windows-latest"):
            self.assertIn(runner, text)
        release = text[text.index("  release:"):]
        self.assertIn("needs: test", release)
        self.assertIn("runs-on: ubuntu-latest", release)
        self.assertIn("dist/assistent-einrichten.zip", release)

    def test_build_fails_without_skill_md(self):
        (self.repo / "assistent-einrichten" / "SKILL.md").unlink()
        result = build(self.repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SKILL.md", result.stdout + result.stderr)
        self.assertFalse(self.zip_path().exists())

    def test_build_fails_with_wrong_name(self):
        skill = self.repo / "assistent-einrichten" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace(
            "name: assistent-einrichten", "name: etwas-anderes"), encoding="utf-8")
        result = build(self.repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("name", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
