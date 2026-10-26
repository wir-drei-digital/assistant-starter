# assistant-starter

An open skill, `assistent-einrichten`, that sets up a small personal AI assistant in a
folder on your computer. It asks two questions, writes a map (`AGENTS.md`), a router
(`CONTEXT.md`), a support note and two built-in skills (`pflege` for upkeep,
`workflow-builder` for your own workflows), and runs a health check. After that you add
workflows one at a time from the [wirdrei.digital workflow library](https://wirdrei.digital/workflows).

Everything the assistant and its user read is in Swiss German (de-CH). Code, README and
commits are in English.

Made by [wirdrei.digital](https://wirdrei.digital). MIT licensed.

## Install

Download [`assistent-einrichten.zip`](https://github.com/wir-drei-digital/assistant-starter/releases/latest/download/assistent-einrichten.zip)
from the latest release. Each release also carries the same file as
`assistent-einrichten-vX.Y.Z.zip`.

### Claude Desktop (recommended)

1. Open Settings › Skills and upload the ZIP.
2. Create an empty folder, for example `Dokumente/Assistent`.
3. Open that folder in the **Code** tab.
4. Write: «Richte meinen Assistenten ein».
5. When the setup is done, start a new chat in the same folder before you paste the first
   workflow. The assistant loads its map and rules at the start of a chat.

The skill puts its own skills into `.claude/skills/` inside the folder.

### Claude Code (CLI)

Unzip into your personal skills folder, so the result is
`~/.claude/skills/assistent-einrichten/SKILL.md`:

```sh
unzip assistent-einrichten.zip -d ~/.claude/skills/
```

Then start `claude` in an empty folder and write «Richte meinen Assistenten ein».

### Codex

Codex reads skills from `.agents/skills/` in the working folder and its parents, and from
`~/.agents/skills/` for your user. Unzip into `~/.agents/skills/`, open an empty folder and
write «Richte meinen Assistenten ein». Codex reads `AGENTS.md` directly. The setup puts
the built-in skills into `.agents/skills/`.
Docs: [Codex skills](https://learn.chatgpt.com/docs/build-skills) (the old
`developers.openai.com/codex/skills` address redirects there),
[AGENTS.md in Codex](https://developers.openai.com/codex/guides/agents-md).

### opencode

opencode reads skills from `.opencode/skills/`, `.claude/skills/` and `.agents/skills/`
in the project, and from `~/.config/opencode/skills/`, `~/.claude/skills/` and
`~/.agents/skills/` globally. Unzip into `~/.config/opencode/skills/` (or one of the other
global folders), open an empty folder and write «Richte meinen Assistenten ein». opencode
reads `AGENTS.md` directly. The setup puts the built-in skills into `.agents/skills/`.
Docs: [opencode skills](https://opencode.ai/docs/skills/),
[opencode rules (AGENTS.md)](https://opencode.ai/docs/rules/).

Skill folders and doc URLs were checked on 2026-10-18. The setup has been designed for
Claude Desktop first; Codex and opencode follow their documented folders but have not been
tested end to end yet.

## What the setup creates

```
Assistent/
├── AGENTS.md          map: role, writing rules, protection rules, «Eigene Regeln»
├── CLAUDE.md          symlink to AGENTS.md (macOS/Linux) or the line @AGENTS.md (Windows)
├── CONTEXT.md         router: | Aufgabe | Ordner | Status |
├── support.md         when and how to reach wirdrei.digital
├── VERSION
├── CHANGELOG.md
├── pruefen.py         read-only health check
├── _setup/            stand.md (setup values, decisions), werkzeuge.md (tool paths, packages)
├── 01_finanzen/ …     areas appear with their first workflow, never in advance
└── .claude/
    ├── skills/pflege/, skills/workflow-builder/   (or .agents/skills/ in Codex/opencode)
    └── assistent-manifest.json
```

Areas have fixed numbers so every workflow lands on the same path for everybody:
`01_finanzen`, `02_kommunikation`, `03_dokumente`, `04_organisation`, `05_marketing`, own
themes from `10_` upward. A workflow lives in `<area>/workflows/<ordner>/CONTEXT.md`.

Python is installed with [uv](https://docs.astral.sh/uv/) into a runtime folder outside the
assistant (`~/Library/Application Support/assistent/` on macOS,
`<LOCALAPPDATA>\assistent\` on Windows). Everything lives there: `bin/` (uv, CLIs such as
`bexio`), `python/`, `venv/`, `cache/` and `secrets/`. The installer runs with
`UV_INSTALL_DIR=<runtime>/bin`, `UV_NO_MODIFY_PATH=1` and `UV_UNMANAGED_INSTALL=<runtime>/bin`
(no PATH or shell profile change, no receipt in the user's config folder), the venv is
created with `UV_PYTHON_INSTALL_DIR=<runtime>/python` and `--cache-dir <runtime>/cache`.
Deleting the runtime folder removes all of it. See the
[installer](https://docs.astral.sh/uv/reference/installer/) and
[environment variable](https://docs.astral.sh/uv/reference/environment/) docs.
The absolute, quoted paths of uv and Python are recorded in `_setup/werkzeuge.md`; skills and
workflows call `"<uv>"` and `"<python>"` from there. The assistant works without Python too;
`pruefen.py` reports a missing venv as information, and `pflege` then checks by reading.

## Health check

```sh
python pruefen.py [ORDNER]                           # read-only report, exit 1 on findings
python pruefen.py ist-assistent [ORDNER]             # leer | fremd | angefangen | assistent
python pruefen.py manifest [ORDNER] --version 1.0.0  # writes .claude/assistent-manifest.json
```

`ASSISTENT_RUNTIME` overrides the runtime folder (used by the tests).

## Patches

There is no self-update. When wirdrei.digital extends someone's assistant, it ships a patch
ZIP. `.claude/assistent-manifest.json` holds the SHA-256 of every file we delivered
(`AGENTS.md`, `CONTEXT.md`, `support.md`, `pruefen.py`, `VERSION` and the built-in skills),
as it looked after setup. Files without a manifest entry belong to the user. A patch
handles two kinds of shipped files differently, and writes nothing before the user says yes:

- `pruefen.py`, `VERSION` and the built-in skills have no placeholders and are copied
  unchanged at setup. A patch creates them if missing, replaces them if the hash still
  matches, and merges them with the user if they were changed.
- `AGENTS.md`, `CONTEXT.md` and `support.md` were filled with the person's values, so they
  are never copied over. A patch re-fills the new template with the values recorded in
  `_setup/stand.md` (`NAME`, `TAETIGKEIT`, `AUFGABEN`, `SKILLS`, `PROGRAMM`, `RUNTIME`),
  then carries over what the person owns: the section «Eigene Regeln» in `AGENTS.md`
  stays word for word, and every area row in the router rows of `CONTEXT.md` is kept.
  The result is shown to the person before it is written.

## Development

```sh
python3 -m unittest discover -s tests -v   # stdlib only, Python 3.10+
python3 scripts/build.py                   # dist/assistent-einrichten-v<VERSION>.zip and dist/assistent-einrichten.zip
```

The ZIP holds exactly one `SKILL.md`, because Claude Desktop rejects an upload with more. The
built-in skills therefore ship as `vorlage/skills/<name>/SKILL.vorlage.md`, and the setup
renames them to `SKILL.md` when it installs them. The ZIP root is the folder `assistent-einrichten/`; the build writes `VERSION` into
`assistent-einrichten/vorlage/VERSION` inside the ZIP only. Pushing a tag `vX.Y.Z` that
matches `VERSION` runs the tests on Ubuntu, macOS and Windows and then, on Ubuntu,
attaches both ZIPs to a GitHub release (`.github/workflows/release.yml`).

Design summary: [`docs/design.md`](docs/design.md).

## License and contact

MIT, see [LICENSE](LICENSE). Questions: info@wirdrei.digital or
[wirdrei.digital/kontakt](https://wirdrei.digital/kontakt).
