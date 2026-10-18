# Strukturcheck

Teil A sind dieselben Punkte, die `pruefen.py` prüft. Mit Python übernimmt das Skript
sie, ohne Python liest du sie selbst nach. Teil B ist Inhalt, den nur du beurteilen
kannst. Beide Teile lesen nur. Geändert wird erst nach einem Ja, über den Ablauf in
`SKILL.md`.

## A. Was auch `pruefen.py` prüft

**A1 Pflichtdateien.** Im Hauptordner liegen `AGENTS.md`, `CONTEXT.md`, `support.md`,
`VERSION` und `CHANGELOG.md`.

**A2 `CLAUDE.md`.** Sie ist ein Symlink auf `AGENTS.md` oder eine Datei mit der Zeile
`@AGENTS.md`.

**A3 Skills.** `pflege` und `workflow-builder` liegen je mit `SKILL.md` in einem
Skill-Ordner: `.claude/skills/`, `.agents/skills/` oder `.opencode/skills/`.

**A4 Router.** Die `CONTEXT.md` im Hauptordner und jede `CONTEXT.md` eines Bereichs hat
genau eine Tabelle mit der Kopfzeile `| Aufgabe | Ordner | Status |` und darunter
`|---|---|---|`. In jeder Zeile steht der Ordner in Backticks und endet mit «/»
(im Hauptordner `01_finanzen/`, im Bereich `workflows/belege/`). Der Status ist
`geplant`, `eingerichtet` oder `aktiv`.

**A5 Router gegen Ordner.** Jede Zeile zeigt auf einen Ordner, den es gibt. Jeder
Ordner mit zwei Ziffern und Unterstrich vorne (`01_finanzen/`) hat eine Zeile im
Haupt-Router. Jeder Ordner unter `<bereich>/workflows/` hat eine Zeile im Router seines
Bereichs.

**A6 Workflows.** Jeder Ordner unter `<bereich>/workflows/` hat eine `CONTEXT.md`.

**A7 Python (nur zur Information).** Im Laufzeitordner gibt es `venv/bin/python` (Mac,
Linux) oder `venv\Scripts\python.exe` (Windows). Fehlt sie, ist das kein Fehler:
`pruefen.py` zeigt dann ✓ mit einem Hinweis, und nur Workflows mit Skripten brauchen sie.

**A8 Passwörter und Schlüssel.** Keine Datei im Ordner heisst `.env` oder endet auf
`.env`, und keine trägt `secret`, `passwort`, `password`, `apikey`, `api-key` oder
`token` als eigenes Wort im Namen (`bexio-token.txt` ja, `tokenizer-notizen.md` nein).
Der Ordner `.git/` zählt nicht. Solche Dateien gehören in `secrets/` im Laufzeitordner.

## B. Was nur du beurteilen kannst

**B1 Status passt.** Der Status im Router und im `CONTEXT.md` des Workflows ist
derselbe. Weichen sie ab, gilt der Workflow, der Router wird nachgezogen.

**B2 Verträge vollständig.** Jede `CONTEXT.md` eines Workflows hat die Abschnitte
Status, Zweck, So arbeitest du, Quellen, Ausgabe, Grenzen und Test. Nennt ein Vertrag
ein Werkzeug, eine Datei oder einen Ort, gibt es das auch.

**B3 Regeln an einem Ort.** Keine Regel steht doppelt, keine widerspricht einer anderen.
Schreibstil steht nur in `_marke/voice.md`, Firmendaten nur in `_marke/firmendaten.md`.

**B4 Entwürfe.** Jeder ENTWURF ist entweder frisch oder wird der Person zur Bestätigung
vorgelegt.

**B5 Grösse.** `AGENTS.md` bis 90 Zeilen, Router bis 50, Vertrag eines Workflows bis 80.
Darüber verschieben statt kürzen.

**B6 Spur.** Die Zahl in `VERSION` steht im `CHANGELOG.md`, und jeder Eintrag dort nennt
einen Rückweg.

**B7 Werkzeuge.** Was ein Workflow installiert, steht in `_setup/werkzeuge.md`.

## Der Befund

Kurz, direkt im Chat, nicht in eine Datei:

```
Prüfung vom TT.MM.JJJJ, Version 1.0.0
Technik (pruefen.py oder von Hand): in Ordnung
Inhalt: 2 Punkte

Was nicht stimmt
- A5  02_kommunikation hat keine Zeile im Router
- B3  Die Anrede steht in voice.md und in 02_kommunikation/CONTEXT.md

Vorschlag
1. Zeile im Router ergänzen (Rückweg: Zeile löschen)
2. Anrede nur in voice.md behalten, im Bereich ein Verweis

Noch ist nichts geändert. Sag, was du davon willst.
```
