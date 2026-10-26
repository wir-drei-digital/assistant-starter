---
name: assistent-einrichten
description: Richtet in einem leeren Ordner einen persönlichen Assistenten ein, mit Karte, Router, Pflege und Workflow-Builder. Auslösen bei «Richte meinen Assistenten ein», «Assistent einrichten», «neuen Assistenten anlegen» oder wenn jemand mit dem Starter von wirdrei.digital beginnen will. Baut nichts neu, wenn im Ordner schon ein Assistent liegt, und macht eine abgebrochene Einrichtung fertig.
---

# Assistent einrichten

Du richtest im geöffneten Ordner das Grundgerüst eines persönlichen Assistenten ein. Die
Person ist meist neu bei KI. Sprich einfach, per Du, ohne Fachjargon, und erkläre jeden
Schritt in einem Satz, bevor du ihn machst. Die Vorlagen liegen in `vorlage/` neben
dieser Datei. Es gibt kein Installationsskript, du legst die Dateien mit deinen eigenen
Werkzeugen an.

Schreibregeln für alles, was du schreibst: Schweizer Hochdeutsch mit «ss», keine
Gedankenstriche, Du-Form.

## So begleitest du die Person

Die Person sitzt vielleicht zum ersten Mal vor so einem Programm. Sie soll sich jederzeit
auskennen und nie erschrecken.

- **Zum Start begrüssen.** Deine erste Nachricht beginnt wörtlich mit diesem Gruss:

  > Hallo, schön, dich kennenzulernen!
  >
  > Ich bin hier, um dir Zeit zu schenken. Was du nicht tun möchtest oder vor dir
  > herschiebst, kannst du ab jetzt mir geben.
  >
  > wirdrei.digital hat mich mit Liebe gebaut. Brauchst du einmal einen Menschen,
  > erreichst du sie hier: [wirdrei.digital/kontakt](https://wirdrei.digital/kontakt)
  >
  > **Starten wir die Installation! Ich freue mich!**

  Übernimm Absätze, Fettschrift und Link genau so, aber ohne das Zitatzeichen «>» und ohne die Zeilenumbrüche innerhalb
  eines Absatzes.

  Danach sagst du in einem Satz, dass die Einrichtung etwa zehn Minuten dauert und sie
  jederzeit unterbrechen kann. In derselben Nachricht folgen die zwei Fragen aus
  Schritt 2, ausser Schritt 1 verlangt zuerst eine Rückfrage. Den Gruss gibt es nur
  einmal, auch wenn du eine angefangene Einrichtung fertig machst.
- **Zeigen, wo ihr steht.** Beginne jede weitere Nachricht mit einer kurzen Zeile wie
  «Schritt 2 von 4: Das Grundgerüst». Die vier Etappen für die Person sind: die zwei
  Fragen, das Grundgerüst (Schritt 3), Python (Schritt 4), der Check (Schritte 5 bis 7).
- **Vor Rückfragen des Programms warnen.** Bevor du einen Befehl ausführst oder ausserhalb
  des Ordners schreibst, sag in einem Satz, was er macht, und dass das Programm gleich
  um Erlaubnis fragen kann. Beim ersten Mal ergänzt du: «Das ist normal. Du kannst
  zustimmen, ich ändere nur, was ich dir hier ankündige.» Fasse mehrere Befehle für
  denselben Zweck zusammen, damit nicht zehn Rückfragen nacheinander kommen.
- **Technik bleibt bei dir.** Zeig keine Befehlsausgaben, Pfade oder Prüfsummen, ausser
  die Person fragt danach. Sag stattdessen in einem Satz, was herausgekommen ist.
- **Ruhig bleiben, wenn etwas klemmt.** Ein Fehler ist nie die Schuld der Person. Sag
  kurz, was nicht geklappt hat, was du als Nächstes versuchst, und mach weiter. Nur wenn
  du sie wirklich brauchst, stellst du eine einzige, klare Frage.
- **Kurz halten.** Höchstens fünf, sechs Sätze pro Nachricht, keine langen Listen. Lieber
  einmal mehr nachfragen als alles auf einmal erklären.

## Begriffe

- **Assistenten-Ordner:** der Ordner, den die Person geöffnet hat (`<geöffneter-ordner>`).
  Im Fall `fremd` aus Schritt 1 ist es stattdessen `<geöffneter-ordner>/Assistent/`.
  Alle Pfade dieser Anleitung (Skill-Ordner, `CLAUDE.md`, `_setup/`, Manifest, Bereiche)
  sind relativ zum Assistenten-Ordner, nie zum geöffneten Ordner.
- **Laufzeitordner:** liegt ausserhalb, für uv, Python und Schlüssel. Ermittle ihn einmal
  als absoluten Pfad und nutze danach nur noch diesen:
  - Mac: `echo "$HOME/Library/Application Support/assistent"`
  - Windows in Git Bash: `echo "$LOCALAPPDATA\assistent"`, in PowerShell:
    `Join-Path $env:LOCALAPPDATA assistent`
  - Linux: `echo "$HOME/.local/share/assistent"`

  Schreib nie `~` oder Variablen in Prozentzeichen in einen Befehl, Git Bash ersetzt sie
  nicht. Der Pfad enthält oft Leerzeichen, darum steht er in Befehlen immer in
  Anführungszeichen.
- **Skill-Ordner:** wo das Programm, in dem du läufst, Skills im Projekt liest:
  - Claude Code und der Code-Tab von Claude Desktop: `.claude/skills`
  - Codex: `.agents/skills`
  - opencode: `.agents/skills` (opencode liest auch diesen Ordner)
- **Windows erkennen:** `uname` meldet `MINGW` oder `MSYS`, oder es gibt die Variable
  `LOCALAPPDATA`. Auch in Git Bash gilt dann alles, was hier für Windows steht. In
  PowerShell setzt du `&` vor einen Befehl, der mit einem Pfad in Anführungszeichen
  beginnt.

## 1. Prüfen, was schon da ist

Gibt es schon eine Python-Umgebung im Laufzeitordner, führe mit ihr `vorlage/pruefen.py`
so aus (in PowerShell mit `&` davor):

- Mac und Linux:
  `"<laufzeitordner>/venv/bin/python" "<pfad zu vorlage/pruefen.py>" ist-assistent "<geöffneter-ordner>"`
- Windows:
  `"<laufzeitordner>\venv\Scripts\python.exe" "<pfad zu vorlage/pruefen.py>" ist-assistent "<geöffneter-ordner>"`

Sonst prüfst du den geöffneten Ordner ohne Python durch Lesen, mit denselben Regeln:

- `assistent`: `AGENTS.md`, `CONTEXT.md` und `.claude/assistent-manifest.json` sind da.
- `angefangen`: `AGENTS.md` und `CONTEXT.md` sind da, das Manifest fehlt. Eine frühere
  Einrichtung wurde nicht fertig.
- `leer`: ausser `.DS_Store`, `desktop.ini` und versteckten Dateien liegt nichts im Ordner.
- `fremd`: alles andere.

Rufe auf dem Mac nie `python3` auf, solange es die Umgebung nicht gibt. Auf einem
frischen Mac öffnet das ein Installationsfenster.

Je nach Ergebnis:

- Bei `assistent` baust du nichts neu und überschreibst nichts. Sag, dass hier schon ein Assistent eingerichtet ist, und biete den Skill `pflege` an.
- Bei `angefangen` machst du nur die Schritte, deren Ergebnis noch fehlen, und überschreibst nie eine Datei, die schon da ist. Einen verschachtelten Ordner `Assistent/` baust du hier nie. Die Antworten auf die zwei Fragen stehen in `_setup/stand.md`, wenn es die Datei gibt. Sonst stellst du die Fragen aus Schritt 2 neu. Sag der Person, dass du eine angefangene Einrichtung fertig machst.
- Bei `fremd` schreibst du nie in bestehende Dateien. Schlag vor, im Unterordner `Assistent/` einzurichten, und frag, ob das passt. Gibt es `Assistent/` schon, prüfst du ihn genauso mit `ist-assistent`: Meldet das `angefangen`, biete an, die Einrichtung dort fertig zu machen, wie oben bei `angefangen`. Meldet es `assistent`, ist dort schon einer eingerichtet, und du bietest den Skill `pflege` an. Ist `Assistent/` sonst nicht leer, frag nach einem anderen Namen. Ab jetzt ist dieser Unterordner der Assistenten-Ordner, und du schreibst nur noch dort hinein.
- Bei `leer` geht es weiter.

## 2. Zwei Fragen, in einer Nachricht

1. Wie heisst du, und wie heisst deine Firma oder was machst du beruflich?
2. Welche Arbeit soll dir der Assistent abnehmen? Zwei, drei Beispiele reichen.

Mehr fragst du nicht. Unklares markierst du später als ENTWURF.

## 3. Das Gerüst schreiben

**Mit Platzhaltern** (lesen, füllen, im Assistenten-Ordner anlegen):

- `vorlage/AGENTS.md`, `vorlage/CONTEXT.md`, `vorlage/support.md`, `vorlage/CHANGELOG.md`
- `vorlage/_setup/stand.md` und `vorlage/_setup/werkzeuge.md` nach `_setup/`

**Unverändert kopieren**, mit `cp` (Mac, Linux, Git Bash) oder `Copy-Item` (PowerShell),
nie abtippen oder neu schreiben, sonst stimmen die Prüfsummen im Manifest nicht:

- `vorlage/pruefen.py` und `vorlage/VERSION` in den Assistenten-Ordner
- `vorlage/skills/pflege/` und `vorlage/skills/workflow-builder/` mit allen Dateien in den
  Skill-Ordner, zum Beispiel
  `cp -R "<pfad zu vorlage>/skills/pflege" "<assistenten-ordner>/.claude/skills/"`
- danach in beiden installierten Skills `SKILL.vorlage.md` in `SKILL.md` umbenennen, mit
  `mv` (Mac, Linux, Git Bash) oder `Rename-Item` (PowerShell). In der ZIP heissen sie
  anders, weil Claude beim Hochladen nur eine einzige `SKILL.md` erlaubt. Der Inhalt
  bleibt unverändert.
- danach diese Vorlagen in den Ordner `assets/` des installierten `workflow-builder`, damit
  spätere Workflows Bereiche anlegen können:
  - `vorlage/bereich/CONTEXT.md` als `assets/bereich-CONTEXT.md`
  - `vorlage/workflow/CONTEXT.md` als `assets/workflow-CONTEXT.md`
  - `vorlage/_marke/voice.md` als `assets/marke-voice.md`
  - `vorlage/_marke/firmendaten.md` als `assets/marke-firmendaten.md`

  Diese vier behalten ihre Platzhalter.

**Platzhalter:**

- `{{NAME}}`: Name der Person
- `{{TAETIGKEIT}}`: Firma oder Tätigkeit
- `{{AUFGABEN}}`: Antwort 2, kurz
- `{{SKILLS}}`: der Skill-Ordner, etwa `.claude/skills`
- `{{PROGRAMM}}`: das Programm, in dem du gerade läufst, etwa «Claude Desktop, Code-Tab»,
  «Claude Code», «Codex» oder «opencode»
- `{{RUNTIME}}`: der Laufzeitordner als absoluter Pfad, so wie du ihn unter «Begriffe»
  ermittelt hast, ohne `~` und ohne Variablen
- `{{DATUM}}`: heute, JJJJ-MM-TT
- `{{VERSION}}`: Inhalt von `vorlage/VERSION`
- `{{CLAUDE_FORM}}`: «ein Symlink auf AGENTS.md» oder «eine Datei mit @AGENTS.md»
- `{{UV}}`, `{{PYTHON}}`, `{{PYTHON_STAND}}` füllst du in Schritt 4, `{{BEREICH}}` in
  Schritt 7

`_setup/stand.md` hält alle Werte fest. Spätere Updates füllen `AGENTS.md`, `CONTEXT.md`
und `support.md` mit genau diesen Werten neu. Am Ende steht in den gefüllten Dateien kein
`{{` mehr.

Nicht in den Assistenten-Ordner kommen `vorlage/bereich/`, `vorlage/workflow/` und
`vorlage/_marke/`. Kein Bereich und kein Ordner entsteht im Voraus.

**`CLAUDE.md`:** Auf Mac und Linux führst du `ln -s AGENTS.md CLAUDE.md` im
Assistenten-Ordner aus und prüfst mit `test -L CLAUDE.md`. Auf Windows, auch in Git
Bash, oder wenn das nicht klappt, schreibst du eine Datei `CLAUDE.md` mit genau der
Zeile `@AGENTS.md`. Git Bash macht aus `ln -s` eine Kopie, darum dort nie `ln -s`.

## 4. Python einrichten

Sag vorher: «Ich installiere jetzt Python in einen eigenen Ordner ausserhalb deines
Assistenten. Das braucht keine Administratorrechte und ändert nichts an deinem System:
Alles liegt im Laufzeitordner, und wer ihn löscht, hat alles wieder weg.»

1. **uv installieren**, nur wenn `<laufzeitordner>/bin/uv` (Windows `bin\uv.exe`) fehlt.
   Die Variablen legen uv in den Laufzeitordner und lassen deine Einstellungen und den
   PATH unberührt:
   - Mac und Linux:
     `curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="<laufzeitordner>/bin" UV_NO_MODIFY_PATH=1 UV_UNMANAGED_INSTALL="<laufzeitordner>/bin" sh`
   - Windows: Wähl die Zeile nach der Shell, in der deine Befehle laufen. In PowerShell
     läuft das Installationsskript direkt, Git Bash startet dafür PowerShell.
   - Windows in PowerShell:
     `$env:UV_INSTALL_DIR="<laufzeitordner>\bin"; $env:UV_NO_MODIFY_PATH="1"; $env:UV_UNMANAGED_INSTALL="<laufzeitordner>\bin"; irm https://astral.sh/uv/install.ps1 | iex`
   - Windows in Git Bash:
     `powershell -ExecutionPolicy ByPass -c '$env:UV_INSTALL_DIR="<laufzeitordner>\bin"; $env:UV_NO_MODIFY_PATH="1"; $env:UV_UNMANAGED_INSTALL="<laufzeitordner>\bin"; irm https://astral.sh/uv/install.ps1 | iex'`
2. **Die Umgebung anlegen.** Gibt es sie schon (`venv/bin/python` oder
   `venv\Scripts\python.exe` im Laufzeitordner, siehe Schritt 1), legst du sie nie neu
   an: Sie gehört allen Assistenten dieser Person. Dann trägst du sie in Punkt 4 nur
   ein. Sonst, mit Python ebenfalls im Laufzeitordner:
   - Mac, Linux und Git Bash:
     `UV_PYTHON_INSTALL_DIR="<laufzeitordner>/python" "<uv>" venv "<laufzeitordner>/venv" --python 3.12 --managed-python --cache-dir "<laufzeitordner>/cache"`
   - PowerShell:
     `$env:UV_PYTHON_INSTALL_DIR="<laufzeitordner>\python"; & "<uv>" venv "<laufzeitordner>\venv" --python 3.12 --managed-python --cache-dir "<laufzeitordner>\cache"`
3. Den Ordner `secrets/` im Laufzeitordner anlegen, falls er fehlt.
4. **In `_setup/werkzeuge.md` eintragen**, als absolute Pfade ohne Anführungszeichen (die
   Vorlage setzt sie schon):
   - `{{UV}}`: `<laufzeitordner>/bin/uv` (Windows `<laufzeitordner>\bin\uv.exe`)
   - `{{PYTHON}}`: `<laufzeitordner>/venv/bin/python` (Windows
     `<laufzeitordner>\venv\Scripts\python.exe`)
   - `{{PYTHON_STAND}}`: «Python 3.12 über uv, eingerichtet am <Datum>»

Ab hier heisst `"<uv>"` und `"<python>"` in allen Anleitungen: der Pfad aus
`_setup/werkzeuge.md`, immer in Anführungszeichen.

Scheitert das (Firmen-Firewall, Richtlinien), sag es ehrlich: «Python liess sich hier
nicht installieren. Dein Assistent funktioniert trotzdem, nur Workflows mit Skripten
brauchen es. Wenn du es später willst, hilft dir `support.md` weiter.» Trag in
`_setup/werkzeuge.md` bei `{{PYTHON_STAND}}` ein, dass Python fehlt und warum, und bei
`{{UV}}` und `{{PYTHON}}` «fehlt». Dann mach weiter. Ohne Python prüfst du in Schritt 5
und 6 durch Lesen.

## 5. Prüfen

Führe `"<python>" "<assistenten-ordner>/pruefen.py" "<assistenten-ordner>"` aus und
erkläre das Ergebnis in einfachen Worten. Jede Zeile mit ✗ behebst du, bevor es
weitergeht. Eine Zeile mit ✓ und einem Hinweis ist nur eine Information, etwa dass
Python fehlt.

Ohne Python gehst du die Punkte des Strukturchecks durch Lesen durch:
`vorlage/skills/pflege/references/strukturcheck.md`.

## 6. Manifest schreiben

Als letzter Schreibschritt:
`"<python>" "<assistenten-ordner>/pruefen.py" manifest "<assistenten-ordner>" --version <VERSION>`.
Das Manifest hält fest, welche Dateien von uns stammen, damit spätere Updates nichts
überschreiben, was die Person selbst geändert hat.

Ohne Python schreibst du `.claude/assistent-manifest.json` im Assistenten-Ordner selbst,
auch wenn die Skills in `.agents/skills` liegen:

```json
{"version": "<VERSION>", "erstellt": "JJJJ-MM-TT", "dateien": {"AGENTS.md": "sha256:<hex>"}}
```

Aufgenommen werden `AGENTS.md`, `CONTEXT.md`, `support.md`, `pruefen.py`, `VERSION` und
jede Datei in `<skill-ordner>/pflege/` und `<skill-ordner>/workflow-builder/`, mit
Pfaden in Schrägstrich-Schreibweise relativ zum Assistenten-Ordner. Den Hash rechnest du
mit `shasum -a 256 <datei>` (Mac) oder `Get-FileHash -Algorithm SHA256 <datei>`
(Windows, Ergebnis klein geschrieben).

## 7. Den ersten Bereich empfehlen

Ordne Antwort 2 einem Thema zu: Finanzen, Kommunikation, Dokumente, Organisation oder
Marketing. Empfiehl eines und verlinke die Bibliothek, gefiltert auf den Einstieg:
`https://wirdrei.digital/workflows?stufe=einstieg&thema=<Thema>`. Trag das Thema in
`_setup/stand.md` bei `{{BEREICH}}` ein. Eine eigene Liste von Workflows hast du nicht,
und du holst auch keine.

Bitte die Person danach immer, im Code-Tab (oder in ihrem Programm) einen neuen Chat im
Assistenten-Ordner zu starten, bevor sie den ersten Workflow einfügt. Erklär es in einem
Satz: «Deine Karte und deine Regeln lädt der Assistent zu Beginn eines Chats, darum
kennt er sie erst im neuen Chat.» Im Fall `fremd` heisst das: den Ordner `Assistent/`
öffnen, nicht den Ordner darüber.

Erkläre dann: «Öffne in der Bibliothek einen Workflow, kopiere seinen Prompt und füge ihn
im neuen Chat ein. Ich richte ihn dann in deinem Assistenten ein.»

Zum Schluss in zwei, drei Sätzen: was jetzt da ist, dass `CHANGELOG.md` jede Änderung
festhält, und dass «prüf meinen Assistenten» den Skill `pflege` startet. Freu dich ruhig
mit der Person, sie hat gerade ihren eigenen Assistenten gebaut. Klemmt später etwas,
schreibt sie an info@wirdrei.digital, das steht auch in `support.md`.
