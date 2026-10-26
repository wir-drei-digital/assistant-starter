---
name: pflege
description: Hält den Assistenten sauber, damit Router, Regeln und Ordner zusammenpassen. Auslösen bei «prüf meinen Assistenten», «räum auf», «merk dir das», «ab jetzt immer so», wenn eine neue Regel dazukommt, wenn etwas nicht mehr gefunden wird, und am Ende jedes neuen Workflows.
---

# Pflege

Du hältst den Assistenten in Ordnung: Der Router zeigt auf Ordner, die es gibt, jede
Regel steht an genau einem Ort, und die Karte bleibt kurz. Ein Assistent zerfällt still,
mit Regeln an zwei Orten, Ordnern ohne Zeile im Router und Entwürfen, die nie bestätigt
wurden. Du findest das, bevor es sich summiert.

Die Schutzregeln in `AGENTS.md` gelten unverändert.

## Vier Wege

| Wenn ... | dann |
|---|---|
| «prüf meinen Assistenten», etwas wird nicht gefunden, der Assistent wirkt durcheinander | **Prüfen** |
| «räum auf», nach mehreren neuen Workflows, die Karte wird lang | **Aufräumen** |
| «merk dir das», «ab jetzt immer so», eine neue Vorliebe | **Regel aufnehmen** |
| ein Workflow wurde gerade eingerichtet | **Nach jedem neuen Workflow** |

### Prüfen

1. Führe `pruefen.py` aus, mit dem Python aus `_setup/werkzeuge.md`:
   `"<python>" "<assistenten-ordner>/pruefen.py" "<assistenten-ordner>"`. Eine Zeile mit ✓
   und einem Hinweis ist nur eine Information.
2. Lies danach den Inhalt nach [`references/strukturcheck.md`](references/strukturcheck.md),
   Teil B. Das Skript sieht Ordner und Tabellen, aber nicht, ob sich Regeln widersprechen.
3. Zeig den Befund im Chat, in der Form am Ende von `references/strukturcheck.md`.
   Geändert wird noch nichts.

**Ohne Python** (die Umgebung fehlt oder lässt sich nicht starten) prüfst du dieselben
Punkte durch Lesen: Teil A von `references/strukturcheck.md`. Sag dazu, dass du von Hand
geprüft hast.

### Aufräumen

Such nach:

- doppelten Regeln (dieselbe Regel an zwei Orten) und Regeln, die sich widersprechen
- Regeln am falschen Ort (siehe «Wo Regeln leben» in `AGENTS.md`)
- ENTWÜRFEN ohne «bestätigt am», die älter als ein paar Tage sind
- einer Karte `AGENTS.md`, die über 90 Zeilen wächst
- Dateien und Ordnern ausserhalb des Schemas: Workflows nicht unter
  `<bereich>/workflows/<name>/`, Ordner im Hauptordner ohne Nummer, Passwörter im Ordner

Für jeden Fund machst du einen Vorschlag: was, warum, Rückweg. Eine Regel bleibt an
einem Ort, die anderen Stellen bekommen einen Verweis oder fallen weg. Eine zu lange
Datei kürzt du nicht, du verschiebst Inhalt in eine Datei daneben und lässt einen
Verweis stehen.

### Regel aufnehmen

1. Bestimme den Ort:
   - gilt überall: `AGENTS.md`, Abschnitt «Eigene Regeln»
   - gilt für einen Bereich: `<bereich>/CONTEXT.md`, Abschnitt «Regeln für diesen Bereich»
   - gilt für einen Workflow: dessen `CONTEXT.md`, Abschnitt «Grenzen»
   - betrifft den Schreibstil: `_marke/voice.md`
2. Gibt es die Regel schon oder eine, die ihr widerspricht? Dann zeig beide und frag.
3. Schreib sie als ENTWURF und sag, wohin. Stimmt die Person zu, ersetzt du ENTWURF
   durch «bestätigt am <Datum>».

### Nach jedem neuen Workflow

Führe **Prüfen** aus. Achte besonders auf die Zeile im Router des Bereichs, die Zeile
des Bereichs im Haupt-Router, einen vollständigen Vertrag im Workflow und neue
Werkzeuge in `_setup/werkzeuge.md`.

## Jede Änderung

1. **Erst erklären:** was du ändern willst, warum, was bisher galt, und wie der Rückweg
   aussieht.
2. **Erst nach einem Ja schreiben.** Schweigen oder eine Rückfrage ist kein Ja.
3. **Überall ändern.** Ein Status steht im Workflow und im Router, ein Bereich im
   Haupt-Router und in seinem Ordner. Halbe Änderungen sind der Anfang jeder Unordnung.
4. **`CHANGELOG.md` ergänzen,** neueste zuerst: Datum, was, warum, Rückweg.
5. **Zum Schluss** noch einmal prüfen.

## Was du nicht tust

- Den Abschnitt «Eigene Regeln» umschreiben, ohne dass die Person es will.
- Schutzregeln in `AGENTS.md` abschwächen.
- Passwörter oder Schlüssel anfassen. Du sagst nur, wo sie hingehören: in den Ordner
  `secrets/` im Laufzeitordner.
- `support.md`, `pruefen.py`, `VERSION` und die beiden Skills ändern. Sie stammen von
  wirdrei.digital. Updates ersetzen `pruefen.py`, `VERSION` und die Skills und füllen
  `support.md`, `AGENTS.md` und `CONTEXT.md` mit den Werten aus `_setup/stand.md` neu,
  ohne «Eigene Regeln» und die Zeilen der Bereiche anzufassen. Ändert sich ein solcher
  Wert, etwa der Name der Firma, passt du ihn auch in `_setup/stand.md` an. Ist in den
  Dateien von wirdrei.digital etwas falsch, verweise auf `support.md`.
- Ordner auf Vorrat anlegen. Ein leerer Ordner verspricht etwas, das es nicht gibt.
- Einen Fakt an einer zweiten Stelle ablegen. Ein Ort, sonst ein Verweis.
