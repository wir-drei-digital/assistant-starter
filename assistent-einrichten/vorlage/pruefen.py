#!/usr/bin/env python3
"""Health check for an assistant folder built by the assistent-einrichten skill.

Usage:
    python pruefen.py [ORDNER]                          read-only check, German report
    python pruefen.py ist-assistent [ORDNER]            prints leer, fremd, angefangen or assistent
    python pruefen.py manifest [ORDNER] --version X.Y.Z writes .claude/assistent-manifest.json

Only the manifest mode writes. Standard library only, Python 3.10 or newer.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

REQUIRED = ("AGENTS.md", "CONTEXT.md", "support.md", "VERSION", "CHANGELOG.md")
SHIPPED = ("AGENTS.md", "CONTEXT.md", "support.md", "pruefen.py", "VERSION")
SKILLS = ("pflege", "workflow-builder")
SKILL_DIRS = (".claude/skills", ".agents/skills", ".opencode/skills")
MANIFEST = Path(".claude") / "assistent-manifest.json"
HEADER = ("Aufgabe", "Ordner", "Status")
STATUS = ("geplant", "eingerichtet", "aktiv")
IGNORED_NAMES = {".DS_Store", "desktop.ini", "Thumbs.db"}
SECRET_WORDS = {"secret", "secrets", "passwort", "passwoerter", "passwörter",
                "password", "passwords", "apikey", "token", "tokens"}
AREA = re.compile(r"^\d{2}_")
ORDNER_CELL = re.compile(r"^`([^`]+/)`$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass
class Befund:
    ok: bool
    punkt: str
    hinweis: str = ""


class Unlesbar(Exception):
    """A file exists but cannot be read."""


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def read_text(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise Unlesbar(str(exc)) from exc
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def runtime_dir(platform: str | None = None) -> Path:
    """Folder outside the assistant that holds venv/ and secrets/."""
    env = os.environ.get("ASSISTENT_RUNTIME")
    if env:
        return Path(env)
    platform = platform or sys.platform
    if platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "assistent"
    if platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "assistent"
    return Path.home() / ".local" / "share" / "assistent"


def visible_dirs(path: Path) -> list[Path]:
    try:
        entries = list(path.iterdir())
    except OSError:
        return []
    return sorted(p for p in entries if p.is_dir() and not p.name.startswith((".", "_")))


# ---------------------------------------------------------------- router

def parse_router(text: str) -> tuple[list[tuple[str, str, str]] | None, str]:
    """Return (rows, problem). rows is None when the table is missing or malformed."""

    def cells(line: str) -> list[str]:
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [c.strip() for c in line.split("|")]

    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines)
              if line.strip().startswith("|") and tuple(cells(line)) == HEADER]
    if not starts:
        return None, "keine Tabelle mit den Spalten «Aufgabe | Ordner | Status» gefunden"
    if len(starts) > 1:
        return None, "die Tabelle «Aufgabe | Ordner | Status» steht mehr als einmal darin"
    i = starts[0] + 1
    if i >= len(lines) or not re.fullmatch(r"\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?", lines[i].strip()):
        return None, "unter der Kopfzeile der Tabelle fehlt die Trennzeile |---|---|---|"
    rows = []
    for number, line in enumerate(lines[i + 1:], start=i + 2):
        if not line.strip().startswith("|"):
            break
        parts = cells(line)
        if len(parts) != 3:
            return None, f"Zeile {number} der Tabelle hat {len(parts)} statt 3 Spalten"
        rows.append((parts[0], parts[1], parts[2]))
    return rows, ""


def check_router(root: Path, folder: Path, label: str, children: list[Path]) -> list[Befund]:
    """Check one router CONTEXT.md against the folders it should list.

    children are the folders that need a row, relative to `folder`.
    """
    path = folder / "CONTEXT.md"
    punkt = f"Router {label}"
    if not path.is_file():
        return [Befund(False, punkt, f"{label} fehlt.")]
    try:
        text = read_text(path)
    except Unlesbar:
        return [Befund(False, punkt, f"{label} ist nicht lesbar. Ist die Datei noch offen oder gesperrt?")]
    rows, problem = parse_router(text)
    if rows is None:
        return [Befund(False, punkt, f"{label}: {problem}.")]

    befunde = []
    listed = set()
    unreadable = False
    for aufgabe, ordner, status in rows:
        match = ORDNER_CELL.match(ordner)
        if not match:
            unreadable = True
            befunde.append(Befund(False, punkt, f"{label}: in der Zeile «{aufgabe}» steht der Ordner "
                                                f"nicht als `ordner/` in Backticks ({ordner})."))
            continue
        rel = match.group(1)
        if status not in STATUS:
            befunde.append(Befund(False, punkt, f"{label}: die Zeile «{aufgabe}» hat den Status «{status}». "
                                                f"Erlaubt sind {', '.join(STATUS)}."))
        target = folder / rel
        if ".." in Path(rel).parts or not target.is_dir():
            befunde.append(Befund(False, punkt, f"{label} zeigt auf `{rel}`, diesen Ordner gibt es nicht."))
            continue
        listed.add(nfc(rel.rstrip("/")))
    for child in [] if unreadable else children:  # an unreadable row may be the missing one
        rel = nfc(child.relative_to(folder).as_posix())
        if rel not in listed:
            shown = child.relative_to(root).as_posix()
            befunde.append(Befund(False, punkt, f"Der Ordner {shown} hat keine Zeile in {label}."))
    return befunde or [Befund(True, punkt)]


def check_structure(root: Path) -> list[Befund]:
    areas = [p for p in visible_dirs(root) if AREA.match(p.name)]
    befunde = check_router(root, root, "CONTEXT.md", areas) if (root / "CONTEXT.md").is_file() else []
    for area in areas:
        workflow_root = area / "workflows"
        workflows = visible_dirs(workflow_root)
        befunde += check_router(root, area, f"{area.name}/CONTEXT.md", workflows)
        missing = [w for w in workflows if not (w / "CONTEXT.md").is_file()]
        for w in missing:
            befunde.append(Befund(False, "Workflow", f"Im Workflow {w.relative_to(root).as_posix()} "
                                                     "fehlt die CONTEXT.md."))
        if workflows and not missing:
            befunde.append(Befund(True, f"Workflows in {area.name}"))
    return befunde


# ---------------------------------------------------------------- other checks

def check_required(root: Path) -> list[Befund]:
    befunde = []
    for name in REQUIRED:
        if (root / name).is_file():
            befunde.append(Befund(True, f"{name} vorhanden"))
        else:
            befunde.append(Befund(False, f"{name} vorhanden", f"Die Datei {name} fehlt."))
    return befunde


def check_claude_md(root: Path) -> Befund:
    punkt = "CLAUDE.md zeigt auf AGENTS.md"
    path = root / "CLAUDE.md"
    if path.is_symlink():
        target = os.readlink(path)
        if Path(target).name == "AGENTS.md" and path.exists():
            return Befund(True, punkt)
        return Befund(False, punkt, f"CLAUDE.md ist eine Verknüpfung auf {target} statt auf AGENTS.md.")
    if not path.is_file():
        return Befund(False, punkt, "Die Datei CLAUDE.md fehlt. Sie braucht nur die eine Zeile @AGENTS.md.")
    try:
        text = read_text(path)
    except Unlesbar:
        return Befund(False, punkt, "CLAUDE.md ist nicht lesbar.")
    if "@AGENTS.md" in (line.strip() for line in text.split("\n")):
        return Befund(True, punkt)
    return Befund(False, punkt, "CLAUDE.md verweist nicht auf AGENTS.md. "
                                "Sie braucht die Zeile @AGENTS.md, sonst liest Claude die Karte nicht.")


def check_skills(root: Path) -> Befund:
    punkt = "Mitgelieferte Skills vorhanden"
    for base in SKILL_DIRS:
        if all((root / base / s / "SKILL.md").is_file() for s in SKILLS):
            return Befund(True, punkt)
    return Befund(False, punkt, "Die Skills pflege und workflow-builder fehlen in "
                                + ", ".join(f"{d}/" for d in SKILL_DIRS) + ".")


def check_python() -> Befund:
    """Information only: the assistant works without Python."""
    punkt = "Python-Umgebung"
    venv = runtime_dir() / "venv"
    if (venv / "bin" / "python").exists() or (venv / "Scripts" / "python.exe").exists():
        return Befund(True, punkt)
    return Befund(True, punkt, f"keine in {venv}. Das ist in Ordnung: Der Assistent funktioniert "
                               "auch ohne Python, nur Workflows mit Skripten brauchen sie.")


def verdaechtig(name: str) -> bool:
    """True if a file name looks like it holds a password or key."""
    lower = nfc(name).lower()
    if lower == ".env" or lower.endswith(".env") or lower.startswith(".env."):
        return True
    stem = lower.rsplit(".", 1)[0] if "." in lower.lstrip(".") else lower
    words = [w for w in re.split(r"[^a-z0-9äöü]+", stem) if w]
    if SECRET_WORDS.intersection(words):
        return True
    return any(a == "api" and b == "key" for a, b in zip(words, words[1:]))


def check_secrets(root: Path) -> Befund:
    punkt = "Keine Passwörter oder Schlüssel im Ordner"
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            if verdaechtig(name):
                found.append((Path(dirpath) / name).relative_to(root).as_posix())
    if not found:
        return Befund(True, punkt)
    return Befund(False, punkt, "Diese Dateien sehen nach Passwörtern oder Schlüsseln aus: "
                                + ", ".join(sorted(found))
                                + f". Sie gehören in {runtime_dir() / 'secrets'}, nicht in diesen Ordner.")


def check(root: Path) -> list[Befund]:
    root = Path(root)
    befunde = check_required(root)
    befunde.append(check_claude_md(root))
    befunde.append(check_skills(root))
    befunde += check_structure(root)
    befunde.append(check_python())
    befunde.append(check_secrets(root))
    return befunde


# ---------------------------------------------------------------- setup helpers

def ist_assistent(root: Path) -> str:
    """leer, fremd, angefangen (map and router, no manifest yet) or assistent."""
    root = Path(root)
    if (root / "AGENTS.md").is_file() and (root / "CONTEXT.md").is_file():
        return "assistent" if (root / MANIFEST).is_file() else "angefangen"
    try:
        entries = [p.name for p in root.iterdir()]
    except OSError:
        return "leer" if not root.exists() else "fremd"
    if all(n.startswith(".") or n in IGNORED_NAMES for n in entries):
        return "leer"
    return "fremd"


def shipped_files(root: Path) -> list[Path]:
    files = [root / n for n in SHIPPED if (root / n).is_file()]
    for base in SKILL_DIRS:
        for skill in SKILLS:
            folder = root / base / skill
            if folder.is_dir():
                files += sorted(p for p in folder.rglob("*")
                                if p.is_file() and "__pycache__" not in p.parts and p.name not in IGNORED_NAMES)
    return files


def write_manifest(root: Path, version: str) -> Path:
    root = Path(root)
    if not VERSION_RE.match(version):
        raise ValueError(f"Die Version «{version}» hat nicht die Form 1.2.3.")
    path = root / MANIFEST
    erstellt = datetime.date.today().isoformat()
    if path.is_file():
        try:
            erstellt = json.loads(read_text(path)).get("erstellt", erstellt)
        except (ValueError, AttributeError, Unlesbar):
            pass
    dateien = {p.relative_to(root).as_posix(): "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()
               for p in shipped_files(root)}
    data = {"version": version, "erstellt": erstellt, "dateien": dict(sorted(dateien.items()))}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return path


# ---------------------------------------------------------------- CLI

def report(root: Path, befunde: list[Befund]) -> str:
    lines = [f"Prüfung von {root}", ""]
    for b in befunde:
        if b.ok:
            lines.append(f"✓ {b.punkt}: {b.hinweis}" if b.hinweis else f"✓ {b.punkt}")
        else:
            lines.append(f"✗ {b.punkt}: {b.hinweis}")
    lines.append("")
    if all(b.ok for b in befunde):
        lines.append("Alles in Ordnung.")
    else:
        lines.append("Einiges braucht Aufmerksamkeit. Der Skill pflege hilft beim Beheben. "
                     "Kommst du nicht weiter, steht in support.md, wie du uns erreichst.")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    try:
        if argv and argv[0] == "ist-assistent":
            print(ist_assistent(Path(argv[1] if len(argv) > 1 else ".")))
            return 0
        if argv and argv[0] == "manifest":
            rest = argv[1:]
            if "--version" not in rest or rest.index("--version") + 1 >= len(rest):
                print("Aufruf: python pruefen.py manifest [ORDNER] --version 1.2.3", file=sys.stderr)
                return 2
            i = rest.index("--version")
            version = rest[i + 1]
            folders = rest[:i] + rest[i + 2:]
            path = write_manifest(Path(folders[0] if folders else "."), version)
            print(f"Manifest geschrieben: {path}")
            return 0
        root = Path(argv[0] if argv else ".")
        if not root.is_dir():
            print(f"Den Ordner {root} gibt es nicht.", file=sys.stderr)
            return 2
        befunde = check(root)
        print(report(root.resolve(), befunde))
        return 0 if all(b.ok for b in befunde) else 1
    except Exception as exc:  # the user must never see a traceback
        print(f"Die Prüfung ist abgebrochen: {exc}. In support.md steht, wie du uns erreichst.",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
