"""Shared fixtures: small assistant trees built in temp dirs."""

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO / "assistent-einrichten"
VORLAGE = SKILL_DIR / "vorlage"
PRUEFEN = VORLAGE / "pruefen.py"

sys.dont_write_bytecode = True  # keep vorlage/ free of __pycache__
if str(VORLAGE) not in sys.path:
    sys.path.insert(0, str(VORLAGE))

HEADER = "| Aufgabe | Ordner | Status |\n|---|---|---|\n"


def write(path: Path, text: str, newline: str = "\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def make_runtime(base: Path, venv: bool = True) -> Path:
    """Create a fake runtime folder and point ASSISTENT_RUNTIME at it."""
    runtime = base / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    if venv:
        python = runtime / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        python.parent.mkdir(parents=True, exist_ok=True)
        python.write_text("")
    os.environ["ASSISTENT_RUNTIME"] = str(runtime)
    return runtime


def make_assistant(tmp, areas=None, claude="symlink", newline="\n", skills=".claude/skills",
                   name="Assistent", manifest=True) -> Path:
    """Build a clean assistant tree under tmp/name and return its root.

    areas maps an area folder to its workflow folder names.
    claude is "symlink", "import" or "missing".
    """
    if areas is None:
        areas = {"01_finanzen": ["belege"]}
    root = Path(tmp) / name
    root.mkdir(parents=True, exist_ok=True)

    write(root / "AGENTS.md", "# Assistent\n\nKarte.\n", newline)
    write(root / "support.md", "# Support\n", newline)
    write(root / "VERSION", "1.0.0\n", newline)
    write(root / "CHANGELOG.md", "# Changelog\n\n## 1.0.0 Einrichtung\n", newline)
    write(root / "pruefen.py", "# copy\n", newline)

    rows = [
        f"| Assistent pflegen | `{skills}/pflege/` | aktiv |",
        f"| Eigenen Workflow bauen | `{skills}/workflow-builder/` | aktiv |",
    ]
    for area, workflows in areas.items():
        rows.append(f"| {area} | `{area}/` | eingerichtet |")
        area_rows = [f"| {w} | `workflows/{w}/` | geplant |" for w in workflows]
        write(root / area / "CONTEXT.md",
              f"# {area}\n\n" + HEADER + "".join(r + "\n" for r in area_rows), newline)
        for w in workflows:
            write(root / area / "workflows" / w / "CONTEXT.md", f"# {w}\n", newline)
    write(root / "CONTEXT.md", "# Router\n\n" + HEADER + "".join(r + "\n" for r in rows), newline)

    for skill in ("pflege", "workflow-builder"):
        write(root / skills / skill / "SKILL.md", f"---\nname: {skill}\ndescription: x\n---\n", newline)

    if claude == "symlink":
        try:
            os.symlink("AGENTS.md", root / "CLAUDE.md")
        except OSError:  # Windows without the symlink privilege
            write(root / "CLAUDE.md", "@AGENTS.md\n", newline)
    elif claude == "import":
        write(root / "CLAUDE.md", "@AGENTS.md\n", newline)

    if manifest:
        write(root / ".claude" / "assistent-manifest.json",
              json.dumps({"version": "1.0.0", "erstellt": "2026-10-18", "dateien": {}}))
    return root
