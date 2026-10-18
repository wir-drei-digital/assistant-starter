#!/usr/bin/env python3
"""Build dist/assistent-einrichten-v<VERSION>.zip with the skill folder as the ZIP root.

dist/assistent-einrichten.zip is a byte-identical copy with a stable name, so
releases/latest/download/assistent-einrichten.zip always points to the newest release.

The VERSION file at the repo root is written into the ZIP as
assistent-einrichten/vorlage/VERSION; the source tree is not touched.
"""

from __future__ import annotations

import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = "assistent-einrichten"
SKIP_NAMES = {".DS_Store", "desktop.ini", "Thumbs.db"}
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def frontmatter(text: str) -> dict[str, str]:
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip().strip("\"'")
    return {}


def fail(message: str) -> int:
    print(f"build failed: {message}", file=sys.stderr)
    return 1


def main() -> int:
    version = (REPO / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        return fail(f"VERSION must look like 1.2.3, got {version!r}")
    skill_dir = REPO / SKILL
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return fail(f"{SKILL}/SKILL.md is missing")
    name = frontmatter(skill_md.read_text(encoding="utf-8")).get("name")
    if name != SKILL:
        return fail(f"SKILL.md frontmatter name is {name!r}, expected {SKILL!r}")

    files = sorted(p for p in skill_dir.rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts and p.name not in SKIP_NAMES
                   and p.relative_to(skill_dir).as_posix() != "vorlage/VERSION")

    out = REPO / "dist" / f"{SKILL}-v{version}.zip"
    out.parent.mkdir(exist_ok=True)

    def add(z: zipfile.ZipFile, arcname: str, data: bytes) -> None:
        info = zipfile.ZipInfo(arcname, FIXED_TIME)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, data)

    with zipfile.ZipFile(out, "w") as z:
        for path in files:
            add(z, f"{SKILL}/{path.relative_to(skill_dir).as_posix()}", path.read_bytes())
        add(z, f"{SKILL}/vorlage/VERSION", f"{version}\n".encode())
    stable = out.with_name(f"{SKILL}.zip")
    shutil.copyfile(out, stable)
    print(f"built {out.relative_to(REPO)} and {stable.relative_to(REPO)} ({len(files) + 1} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
