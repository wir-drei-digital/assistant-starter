import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import SKILL_DIR, VORLAGE, make_runtime

import pruefen

# The built-in skills ship as SKILL.vorlage.md: Claude accepts only one SKILL.md per upload.
SKILL_MDS = sorted([*SKILL_DIR.rglob("SKILL.md"), *SKILL_DIR.rglob("SKILL.vorlage.md")])
MARKDOWN = sorted(SKILL_DIR.rglob("*.md"))
PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")


def frontmatter(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").split("\n")
    assert lines[0] == "---", path
    fields = {}
    for line in lines[1:]:
        if line == "---":
            return fields
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    raise AssertionError(f"unterminated frontmatter in {path}")


def fill(text: str, skills: str) -> str:
    return PLACEHOLDER.sub(lambda m: skills if m.group(1) == "SKILLS" else "Test", text)


def add_row(context: Path, row: str) -> None:
    lines = context.read_text(encoding="utf-8").split("\n")
    header = next(i for i, l in enumerate(lines) if l.startswith("| Aufgabe | Ordner | Status |"))
    end = header + 2
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    lines.insert(end, row)
    context.write_text("\n".join(lines), encoding="utf-8")


class ContentTests(unittest.TestCase):
    def test_frontmatter_valid(self):
        self.assertEqual(len(SKILL_MDS), 3, SKILL_MDS)
        for path in SKILL_MDS:
            fields = frontmatter(path)
            self.assertEqual(fields.get("name"), path.parent.name, path)
            self.assertTrue(fields.get("description"), path)
            self.assertLess(len(fields["description"]), 1024, path)

    def test_user_facing_text_rules(self):
        for path in MARKDOWN + [VORLAGE / "pruefen.py"]:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(SKILL_DIR)
            self.assertNotIn("—", text, rel)
            self.assertNotIn("ß", text, rel)
            if path.suffix == ".md":
                self.assertIsNone(re.search(r"\bICM\b", text), rel)
            for m in re.finditer(r"wirdrei\.digital", text, re.IGNORECASE):
                self.assertEqual(m.group(0), "wirdrei.digital", rel)
            self.assertIsNone(re.search(r"wir ?drei digital", text, re.IGNORECASE), rel)

    def test_referenced_files_exist(self):
        for path in SKILL_MDS:
            text = path.read_text(encoding="utf-8")
            for ref in re.findall(r"`((?:vorlage|references)/[^`\s]+)`", text):
                if ref == "vorlage/VERSION":  # written into the ZIP by scripts/build.py
                    continue
                base = SKILL_DIR if ref.startswith("vorlage/") else path.parent
                self.assertTrue((base / ref).exists(), f"{path.relative_to(SKILL_DIR)}: {ref}")

    def test_only_one_skill_md(self):
        """Claude Desktop rejects a ZIP with more than one SKILL.md."""
        self.assertEqual(list(SKILL_DIR.rglob("SKILL.md")), [SKILL_DIR / "SKILL.md"])
        self.assertIn("SKILL.vorlage.md", (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))

    def test_setup_guards_existing_folder(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("ist-assistent", text)
        lines = text.split("\n")
        self.assertTrue(any("`assistent`" in l and "pflege" in l for l in lines))
        self.assertTrue(any("`fremd`" in l and "`Assistent/`" in l for l in lines))
        self.assertIn("nie", " ".join(l for l in lines if "`fremd`" in l or "überschreib" in l))

    def section(self, number: int) -> str:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(rf"(?ms)^## {number}\. .*?(?=^## |\Z)", text)
        self.assertIsNotNone(match, number)
        return match.group(0)

    def test_assistant_folder_is_explicit(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        definition = re.search(r"(?ms)^- \*\*Assistenten-Ordner:\*\*.*?(?=^- \*\*)", text).group(0)
        self.assertIn("`fremd`", definition)
        self.assertIn("`<geöffneter-ordner>/Assistent/`", definition)
        self.assertIn("relativ zum Assistenten-Ordner", text)
        calls = [c for c in re.findall(r"`([^`]*pruefen\.py[^`]*)`", text) if "python" in c]
        self.assertGreaterEqual(len(calls), 3, calls)
        for call in calls:
            self.assertTrue('"<assistenten-ordner>"' in call or '"<geöffneter-ordner>"' in call, call)

    def test_guides_newcomers(self):
        """Greets with an overview, shows progress and warns before permission prompts."""
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        start = text.find("## So begleitest du die Person")
        self.assertNotEqual(start, -1)
        guide = text[start:text.find("\n## ", start + 1)]
        self.assertIn("zehn", guide)
        self.assertIn("Fahren wir fort mit der Installation!", guide)
        self.assertIn("https://wirdrei.digital/kontakt", guide)
        self.assertIn("von 4", guide)
        self.assertIn("um Erlaubnis", guide)
        self.assertIn("nie die Schuld", guide)

    def test_new_chat_before_first_workflow(self):
        """Always, not only for `fremd`: rules load at the start of a chat."""
        step7 = self.section(7)
        paste = step7.find("füge ihn")
        self.assertNotEqual(paste, -1)
        before = step7[:paste]
        self.assertIn("neuen Chat", before)
        self.assertIn("Code-Tab", before)
        self.assertIn("Assistenten-Ordner", before)
        self.assertRegex(before, r"Regeln[^.]*(Anfang|Beginn)")
        self.assertNotRegex(before, r"Im Fall `fremd` bittest")

    def test_resume_started_setup(self):
        step1 = self.section(1)
        self.assertIn("`angefangen`", step1)
        line = next(l for l in step1.split("\n") if l.startswith("- Bei `angefangen`"))
        self.assertIn("fehlen", line)
        self.assertIn("überschreibst", line)
        self.assertIn("nie", line)
        self.assertIn("`Assistent/`", line)

    def test_copy_files_unchanged(self):
        step3 = self.section(3)
        self.assertIn("cp", step3)
        self.assertIn("Copy-Item", step3)
        self.assertRegex(step3, r"(?is)unverändert kopieren.*pruefen\.py")
        self.assertIn("nie ab", step3)

    def test_uv_stays_in_runtime_folder(self):
        step4 = self.section(4)
        for var in ("UV_INSTALL_DIR", "UV_NO_MODIFY_PATH", "UV_PYTHON_INSTALL_DIR"):
            self.assertIn(var, step4)
        self.assertIn("UV_INSTALL_DIR=\"<laufzeitordner>/bin\"", step4)
        self.assertIn("UV_PYTHON_INSTALL_DIR=\"<laufzeitordner>/python\"", step4)
        self.assertIn("$env:UV_INSTALL_DIR", step4)
        # Every variant pins the binary to the runtime folder; unmanaged = no self-update, no PATH.
        self.assertEqual(step4.count('UV_UNMANAGED_INSTALL="<laufzeitordner>/bin"'), 1)
        self.assertEqual(step4.count('$env:UV_UNMANAGED_INSTALL="<laufzeitordner>\\bin"'), 2)
        self.assertEqual(step4.count('$env:UV_NO_MODIFY_PATH="1"'), 2)
        self.assertIn("--cache-dir", step4)
        self.assertIn("ändert nichts an deinem System", step4)
        werkzeuge = (VORLAGE / "_setup" / "werkzeuge.md").read_text(encoding="utf-8")
        self.assertIn('`"{{UV}}"`', werkzeuge)
        self.assertIn('`"{{PYTHON}}"`', werkzeuge)
        changelog = (VORLAGE / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("Laufzeitordner", changelog)
        self.assertIn("alles weg", changelog)
        self.assertNotIn("~/.local/bin", SKILL_DIR.joinpath("SKILL.md").read_text(encoding="utf-8"))

    def test_windows_uv_install_without_nested_quotes_in_powershell(self):
        """PowerShell 5.1 drops inner double quotes when it passes a string to powershell.exe,
        so PowerShell runs the installer directly; only Git Bash calls powershell -c."""
        step4 = self.section(4)
        lines = step4.split("\n")
        ps = next(i for i, l in enumerate(lines) if l.strip().startswith("- Windows in PowerShell"))
        bash = next(i for i, l in enumerate(lines) if l.strip().startswith("- Windows in Git Bash"))
        ps_cmd = lines[ps + 1].strip()
        bash_cmd = lines[bash + 1].strip()
        self.assertTrue(ps_cmd.startswith("`$env:UV_INSTALL_DIR="), ps_cmd)
        self.assertNotIn("powershell", ps_cmd)
        self.assertTrue(ps_cmd.endswith("irm https://astral.sh/uv/install.ps1 | iex`"), ps_cmd)
        self.assertTrue(bash_cmd.startswith("`powershell -ExecutionPolicy ByPass -c '$env:"), bash_cmd)
        self.assertTrue(bash_cmd.endswith("| iex'`"), bash_cmd)
        self.assertRegex(step4, r"(?i)wähl[^.]*Shell")

    def test_step1_names_the_venv_python(self):
        """`"<python>"` is defined in step 4; step 1 names the venv path itself."""
        step1 = self.section(1)
        self.assertNotIn('"<python>"', step1)
        self.assertIn('"<laufzeitordner>/venv/bin/python"', step1)
        self.assertIn('"<laufzeitordner>\\venv\\Scripts\\python.exe"', step1)

    def test_fremd_resumes_started_subfolder(self):
        step1 = self.section(1)
        line = next(l for l in step1.split("\n") if l.startswith("- Bei `fremd`"))
        self.assertIn("ist-assistent", line)
        self.assertIn("`angefangen`", line)
        self.assertIn("fertig", line)

    def test_no_percent_variables_and_quoted_commands(self):
        """Git Bash does not expand %VAR%; paths with spaces need quotes."""
        for path in MARKDOWN:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(SKILL_DIR)
            self.assertNotRegex(text, r"%[A-Z]+%", rel)
            for token in ("<python>", "<uv>"):
                for m in re.finditer(re.escape(token), text):
                    before = text[m.start() - 1] if m.start() else ""
                    after = text[m.end()] if m.end() < len(text) else ""
                    if before == "`" and after == "`":
                        continue  # the name itself, explained in prose
                    self.assertEqual((before, after), ('"', '"'), f"{rel}: unquoted {token}")

    def test_stand_records_all_placeholder_values(self):
        stand = (VORLAGE / "_setup" / "stand.md").read_text(encoding="utf-8")
        for name in ("NAME", "TAETIGKEIT", "AUFGABEN", "SKILLS", "PROGRAMM", "RUNTIME"):
            self.assertIn("{{%s}}" % name, stand)
        used = set()
        for name in ("AGENTS.md", "CONTEXT.md", "support.md"):
            used |= set(PLACEHOLDER.findall((VORLAGE / name).read_text(encoding="utf-8")))
        self.assertLessEqual(used, set(PLACEHOLDER.findall(stand)))
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`{{PROGRAMM}}`", skill)
        self.assertRegex(skill, r"`\{\{RUNTIME\}\}`[^.]*absolut")

    def test_patch_rule_documented(self):
        readme = (SKILL_DIR.parent / "README.md").read_text(encoding="utf-8")
        self.assertIn("_setup/stand.md", readme)
        self.assertRegex(readme, r"never copied over")
        self.assertIn("Eigene Regeln", readme)
        self.assertRegex(readme, r"router rows")
        self.assertIn("releases/latest/download/assistent-einrichten.zip", readme)

    def test_design_doc_is_public(self):
        text = (SKILL_DIR.parent / "docs" / "design.md").read_text(encoding="utf-8")
        self.assertNotIn("Implementation Plan", text)
        for section in ("Purpose", "Structure", "Rules placement", "Patches", "Platform notes"):
            self.assertIn(f"## {section}", text)

    def test_public_text_has_no_internal_traces(self):
        """Generic patterns only: local paths, internal folders and tools, attributed decisions."""
        repo = SKILL_DIR.parent
        public = [repo / "README.md", repo / "docs" / "design.md", repo / "scripts" / "build.py",
                  repo / ".github" / "workflows" / "release.yml"]
        public += sorted(p for p in SKILL_DIR.rglob("*") if p.is_file())
        internal = (
            r"/Users/",
            r"[A-Z]:\\Users\\[A-Za-z]",  # a real Windows home, not a placeholder
            r"\b(1[0-2]_(internes|solutions|wiki)|0[1-9]_(clients|website|workshops|documents|workflows|compliance))\b",
            r"\bicm-(update|create|finalize)\b",
            r"\b_system/",
            r"\bw3d\b",
            r"git\.wirdrei\.digital",
            r"\bEntscheid(e|s)? (von )?[A-ZÄÖÜ][a-zäöü]+ \d",  # «Entscheid <Name> <Datum>»
        )
        for path in public:
            text = path.read_text(encoding="utf-8")
            for pattern in internal:
                with self.subTest(file=path.relative_to(repo).as_posix(), pattern=pattern):
                    self.assertNotRegex(text, pattern)

    def test_repo_names(self):
        repo = SKILL_DIR.parent
        readme = (repo / "README.md").read_text(encoding="utf-8")
        self.assertTrue(readme.startswith("# assistant-starter\n"))
        self.assertIn(
            "https://github.com/wir-drei-digital/assistant-starter/releases/latest/download/"
            "assistent-einrichten.zip", readme)
        for path in [repo / "README.md", repo / "docs" / "design.md"] + MARKDOWN:
            with self.subTest(file=path.name):
                self.assertNotRegex(path.read_text(encoding="utf-8"), r"assistent-(starter|workflows)")

    def test_router_status_coherent(self):
        context = (VORLAGE / "CONTEXT.md").read_text(encoding="utf-8")
        self.assertNotIn("im Ordner und hier", context)
        builder = (VORLAGE / "skills" / "workflow-builder" / "SKILL.vorlage.md").read_text(encoding="utf-8")
        self.assertNotIn("| geplant |", builder)
        self.assertIn("| eingerichtet |", builder)
        self.assertIn("Haupt-Router", self.builder_phase_g(builder))
        template = (VORLAGE / "workflow" / "CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("**Status: eingerichtet**", template)
        agents = (VORLAGE / "AGENTS.md").read_text(encoding="utf-8")
        rule5 = re.search(r"(?ms)^5\. .*?(?=^6\. )", agents).group(0)
        self.assertIn("workflow-builder", rule5)
        self.assertIn("Bibliothek", rule5)

    def builder_phase_g(self, text):
        return re.search(r"(?ms)^## Testlauf.*", text).group(0)

    def test_secrets_file_opened_for_the_person(self):
        builder = (VORLAGE / "skills" / "workflow-builder" / "SKILL.vorlage.md").read_text(encoding="utf-8")
        for needle in ('open -e "<datei>"', 'start "" notepad "<datei>"',
                       'Start-Process notepad "<datei>"', "<laufzeitordner>/secrets/<dienst>.env"):
            self.assertIn(needle, builder)
        # A bare `notepad "<datei>"` blocks Git Bash and PowerShell until the editor closes.
        self.assertNotRegex(builder, r'(?<!start "" )(?<!Start-Process )notepad "')
        self.assertRegex(builder, r"Werte[^.]*nie")

    def test_existing_venv_is_never_recreated(self):
        step4 = self.section(4)
        self.assertIn('"<uv>" venv', step4)
        skip = step4.find("schon")
        self.assertNotEqual(skip, -1)
        self.assertLess(skip, step4.find('"<uv>" venv'))
        self.assertIn("nie neu", step4)

    def test_python_fallback_documented(self):
        for path in (SKILL_DIR / "SKILL.md", VORLAGE / "skills" / "pflege" / "SKILL.vorlage.md"):
            self.assertIn("ohne python", path.read_text(encoding="utf-8").lower(), path)

    def test_agents_md_length_and_sections(self):
        text = (VORLAGE / "AGENTS.md").read_text(encoding="utf-8")
        lines = text.rstrip("\n").split("\n")
        self.assertGreaterEqual(len(lines), 60)
        self.assertLessEqual(len(lines), 90)
        sections = [l for l in lines if l.startswith("## ")]
        self.assertEqual(sections[-1], "## Eigene Regeln")
        self.assertIn("→ CONTEXT.md ist der Router", text.replace("`", "").replace("*", ""))
        for placeholder in ("{{NAME}}", "{{TAETIGKEIT}}", "{{AUFGABEN}}"):
            self.assertIn(placeholder, text)

    def test_support_md_terms(self):
        text = (VORLAGE / "support.md").read_text(encoding="utf-8")
        self.assertIn("info@wirdrei.digital", text)
        self.assertIn("wirdrei.digital/kontakt", text)
        sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
        self.assertTrue(any("ohne Garantie" in s for s in sentences))
        self.assertTrue(any("Erweiterungen" in s and "bezahlt" in s for s in sentences))

    def test_assembled_skeleton_passes_pruefen(self):
        old_env = os.environ.get("ASSISTENT_RUNTIME")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            make_runtime(tmp)
            root = tmp / "Assistent"
            root.mkdir()
            skills = ".claude/skills"

            # step 3: every vorlage file except bereich/, workflow/, _marke/, skills/
            for src in sorted(VORLAGE.rglob("*")):
                rel = src.relative_to(VORLAGE)
                if src.is_dir() or rel.parts[0] in ("bereich", "workflow", "_marke", "skills"):
                    continue
                dst = root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.suffix == ".md":
                    dst.write_text(fill(src.read_text(encoding="utf-8"), skills), encoding="utf-8")
                else:
                    shutil.copy2(src, dst)
            (root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            try:
                os.symlink("AGENTS.md", root / "CLAUDE.md")
            except OSError:  # Windows without the symlink privilege
                (root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
            shutil.copytree(VORLAGE / "skills", root / skills)
            for template in (root / skills).glob("*/SKILL.vorlage.md"):
                template.rename(template.with_name("SKILL.md"))
            assets = root / skills / "workflow-builder" / "assets"
            assets.mkdir()
            shutil.copy2(VORLAGE / "bereich" / "CONTEXT.md", assets / "bereich-CONTEXT.md")
            shutil.copy2(VORLAGE / "workflow" / "CONTEXT.md", assets / "workflow-CONTEXT.md")
            shutil.copy2(VORLAGE / "_marke" / "voice.md", assets / "marke-voice.md")
            shutil.copy2(VORLAGE / "_marke" / "firmendaten.md", assets / "marke-firmendaten.md")
            for path in root.rglob("*.md"):
                if "skills" not in path.parts:  # skills and their assets keep placeholders
                    self.assertNotIn("{{", path.read_text(encoding="utf-8"), path)
            pruefen.write_manifest(root, "1.0.0")
            self.assertEqual(pruefen.ist_assistent(root), "assistent")
            self.assertEqual([b for b in pruefen.check(root) if not b.ok], [])

            # one area and one workflow, built from the copied assets
            area = root / "01_finanzen"
            (area / "workflows" / "belege").mkdir(parents=True)
            (area / "CONTEXT.md").write_text(
                fill((assets / "bereich-CONTEXT.md").read_text(encoding="utf-8"), skills), encoding="utf-8")
            (area / "workflows" / "belege" / "CONTEXT.md").write_text(
                (assets / "workflow-CONTEXT.md").read_text(encoding="utf-8"), encoding="utf-8")
            add_row(root / "CONTEXT.md", "| Finanzen | `01_finanzen/` | geplant |")
            add_row(area / "CONTEXT.md", "| Belege erfassen | `workflows/belege/` | geplant |")

            befunde = pruefen.check(root)
            self.assertEqual([b for b in befunde if not b.ok], [])
            self.assertTrue(any(b.punkt == "Workflows in 01_finanzen" for b in befunde))
        if old_env is None:
            os.environ.pop("ASSISTENT_RUNTIME", None)
        else:
            os.environ["ASSISTENT_RUNTIME"] = old_env


if __name__ == "__main__":
    unittest.main()
