# Design summary

What the starter is, how the folder it builds is laid out, where rules live, how patches
work and what each platform needs. User-facing wording is German (de-CH); this document
and the code are English.

## Purpose

`assistent-einrichten` is a free, open skill. A person installs it in their AI program,
opens an empty folder and writes «Richte meinen Assistenten ein». The skill asks two
questions (name and business, which work to hand over), writes a small skeleton, installs
Python into a runtime folder outside the assistant, runs a health check and recommends a
first area of the [workflow library](https://wirdrei.digital/workflows). From then on the
person adds workflows one at a time by pasting their prompts.

The skeleton is also where the assistant collects what the person teaches it: rules,
workflows, writing style, company data.

Goals:

- Setup in a few minutes, with two questions instead of a questionnaire.
- Every library workflow has a fixed, predictable place.
- A maintenance skill keeps routing, rules and folders consistent.
- Patchable from day one without destroying what the person built.
- Works the same on macOS and Windows.

Non-goals: no prepared content, no shipped workflows (they come from the library), no
self-update, no per-program customisation beyond the skill folder and `CLAUDE.md`.

Failure modes the design guards against:

- A beginner gets stuck at setup (for example on Python) and gives up.
- After a few workflows the folder is a mess and the assistant cannot find its rules.
- A patch overwrites a rule the person taught the assistant.
- Passwords or keys end up in a folder that syncs to the cloud.

## Structure

```
Assistent/
├── AGENTS.md            map (60 to 90 lines), «Eigene Regeln» last
├── CLAUDE.md            symlink to AGENTS.md, or a file with the line @AGENTS.md
├── CONTEXT.md           router: | Aufgabe | Ordner | Status |
├── support.md           when and how to reach wirdrei.digital
├── VERSION
├── CHANGELOG.md         newest first: what, why, way back
├── pruefen.py           read-only health check (plus ist-assistent and manifest modes)
├── _setup/
│   ├── stand.md         setup values (name, business, tasks, skill folder, program,
│   │                    runtime folder) and one-time decisions with «bestätigt am»
│   └── werkzeuge.md     absolute paths of the runtime folder, uv and Python; packages
├── _marke/              created by the first workflow that needs it
│   ├── voice.md
│   └── firmendaten.md   Firma, Adresse, PLZ Ort, IBAN, MWST-Nr., E-Mail, Telefon
├── 01_finanzen/         created with its first workflow
│   ├── CONTEXT.md       area router and area rules
│   └── workflows/<ordner>/CONTEXT.md
└── .claude/
    ├── skills/pflege/, skills/workflow-builder/   (or .agents/skills/)
    └── assistent-manifest.json
```

- **Areas have fixed numbers** that follow the website's `thema` field: `01_finanzen`,
  `02_kommunikation`, `03_dokumente`, `04_organisation`, `05_marketing`; own themes from
  `10_` upward. An area exists only once it has a workflow; gaps are intended. So a
  workflow's path is the same for everyone, and library instructions, support and patches
  can find it.
- **Workflow folders** are `<area>/workflows/<ordner>/` with a `CONTEXT.md` contract:
  status, trigger, Zweck, So arbeitest du, Quellen, Ausgabe, Grenzen, Test. Connections to
  business software (bexio, CashCtrl, KLARA) are workflows in their area like any other.
- **Router contract:** the root `CONTEXT.md` and every area `CONTEXT.md` hold exactly one
  table `| Aufgabe | Ordner | Status |`; the `Ordner` cell is one backticked relative path
  ending in `/`. New rows go directly under the last row. Status is `geplant`,
  `eingerichtet` or `aktiv`. A new workflow and a new area start as `eingerichtet`; after
  a clean real run the workflow, its area row and (if still `eingerichtet`) the root row
  of the area become `aktiv`.
- **No empty folders in advance.** An empty folder promises something that does not exist.

## Rules placement

| Kind | Place |
|---|---|
| Role, writing rules, protection rules | `AGENTS.md` (shipped part) |
| The person's rules that apply everywhere | `AGENTS.md`, section «Eigene Regeln» |
| Rules for an area | `<area>/CONTEXT.md` |
| Rules for a workflow | its `CONTEXT.md`, section «Grenzen» |
| Writing style | `_marke/voice.md` |

Learned rules go to the right file, never into the agent's memory, marked ENTWURF until
the person confirms («bestätigt am <Datum>»). Structural changes get a `CHANGELOG.md`
entry and run through `pflege`, `workflow-builder` or a library workflow. Few broad rules
beat many narrow ones; a fact lives in exactly one place.

Protection rules in `AGENTS.md`: what the person teaches goes into files; nothing leaves
the computer without an explicit yes; passwords and keys never in the folder or the chat;
ask before deleting or overwriting; structure changes with a changelog entry; point to
`support.md` after two honest failed attempts or for requests beyond the library.

## Patches

There is no self-update. When wirdrei.digital extends an assistant on request, it ships
a patch ZIP with instructions for the assistant. To make that safe from day one:

- `.claude/assistent-manifest.json` records the version and the SHA-256 of every shipped
  file as it looked after setup (`AGENTS.md`, `CONTEXT.md`, `support.md`, `pruefen.py`,
  `VERSION`, every file of the two built-in skills). A file without an entry belongs to
  the person.
- `pruefen.py`, `VERSION` and the skills carry no placeholders and are copied unchanged at
  setup. A patch creates them if missing, replaces them if the hash matches, and merges
  them with the person if they changed.
- `AGENTS.md`, `CONTEXT.md` and `support.md` are never copied over. A patch fills the new
  template with the values in `_setup/stand.md`, keeps «Eigene Regeln» word for word and
  keeps every area row of the router.
- The person's own files (`_marke/`, `_setup/`, areas, workflows) change only by an
  explicit instruction in the patch.
- Before writing, the assistant copies the affected files next to the folder; rolling
  back means copying them back. Nothing is written before the person says yes.

## Python and secrets

uv installs Python without admin rights into a runtime folder outside the assistant, so
cloud-synced folders never hold thousands of files:

- macOS `~/Library/Application Support/assistent/`, Windows `<LOCALAPPDATA>\assistent\`,
  Linux `~/.local/share/assistent/`. The skill resolves it once to an absolute path and
  records it.
- Inside: `bin/` (uv and CLIs such as `bexio`), `python/`, `venv/`, `cache/`, `secrets/`.
  The uv installer runs with `UV_INSTALL_DIR`, `UV_NO_MODIFY_PATH` and
  `UV_UNMANAGED_INSTALL` pointing there; the venv uses `UV_PYTHON_INSTALL_DIR` and
  `--cache-dir`. Deleting the runtime folder removes everything.
- `_setup/werkzeuge.md` holds the absolute paths of uv and Python. Every instruction calls
  `"<uv>"` and `"<python>"` in quotes, because the paths often contain spaces.
- If Python cannot be installed, the assistant still works; only workflows with scripts
  need it. `pruefen.py` reports a missing venv as information, not as an error.
- Secrets live in `secrets/<dienst>.env` in the runtime folder. The assistant creates the
  file with empty keys and opens it in a text editor; the person fills it in. Values never
  appear in the chat. Programs with their own login (our CLIs) keep their own store.

## Platform notes

- The skill uses the open skill format (`SKILL.md` with frontmatter) and runs in Claude
  Code (also the Code tab of Claude Desktop, the recommended path for beginners), Codex
  and opencode.
- The map is `AGENTS.md`, which Codex and opencode read directly. Claude Code reads
  `CLAUDE.md`: a symlink on macOS and Linux, a file with `@AGENTS.md` on Windows, where
  symlinks need admin rights and Git Bash turns `ln -s` into a copy.
- The built-in skills go once into the skill folder of the running program:
  `.claude/skills/` for Claude Code, `.agents/skills/` for Codex and opencode. The health
  check accepts `.claude/skills/`, `.agents/skills/` and `.opencode/skills/`.
- Rules load at the start of a chat, so after setup the person starts a new chat in the
  assistant folder before pasting the first workflow.
- On Windows the agent may run in Git Bash or PowerShell. Instructions avoid `%VAR%` and
  `~`, use absolute quoted paths, and note that PowerShell needs `&` before a quoted path.
  Commands that differ come in one variant per shell: PowerShell runs the uv installer
  directly (Windows PowerShell 5.1 drops inner double quotes when it passes a string to
  `powershell.exe`), Git Bash calls `powershell -ExecutionPolicy ByPass -c '...'`.
  Editors open without blocking: `open -e`, `start "" notepad`, `Start-Process notepad`.
- `ist-assistent` tells the setup where it stands: `leer` (build), `fremd` (build in a
  new subfolder `Assistent/`, or finish it there if it reports `angefangen`), `angefangen`
  (finish only the missing steps, never overwrite, never nest) or `assistent` (build
  nothing, offer `pflege`).
