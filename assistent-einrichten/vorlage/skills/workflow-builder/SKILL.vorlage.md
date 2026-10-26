---
name: workflow-builder
description: Führt durch ein kurzes Gespräch und legt einen eigenen Workflow im Assistenten an. Auslösen bei «neuer Workflow», «neuer Ablauf», «kannst du das jedes Mal machen», «das mache ich jede Woche», wenn eine wiederkehrende Aufgabe dazukommen soll oder ein bestehender Workflow einen Schritt, eine Quelle oder eine Ausgabe braucht.
---

# Workflow-Builder

Aus einer Aufgabe, die die Person in ihren Worten beschreibt, wird ein Workflow an
seinem festen Platz: `<bereich>/workflows/<name>/CONTEXT.md`, mit Zeilen in beiden
Routern und einem Eintrag im `CHANGELOG.md`. Die Person muss nie wissen, was ein Router
oder ein Vertrag ist.

Die Schutzregeln in `AGENTS.md` gelten unverändert.

## So fragst du

- Höchstens zwei, drei Fragen pro Nachricht.
- Kein Jargon: «Ablauf» statt «Pipeline», «Ordner» statt «Pfad».
- Immer einen Vorschlag machen und bestätigen lassen, statt offen zu fragen.
- «Weiss nicht» ist eine gültige Antwort. Dann schlägst du etwas vor, markierst es als
  ENTWURF und gehst weiter.

## Ablauf

Die Fragen im Einzelnen: [`references/interview.md`](references/interview.md).

| Phase | Was passiert |
|---|---|
| **A. Verstehen** | Die Person beschreibt die Aufgabe: was reinkommt, was rauskommt, wo sie prüft |
| **B. Ort und Name** | Du schlägst Bereich und Namen vor, die Person bestätigt |
| **C. Quellen und Schreiben** | Was gelesen wird, wohin geschrieben wird, was tabu ist |
| **D. Programme und Werkzeuge** | Andere Programme, Bibliotheken, Schlüssel |
| **E. Regeln durchgehen** | Jede Regel einzeln bestätigen lassen. Pflicht |
| **F. Bauen** | Dateien anlegen, siehe unten |
| **G. Testlauf** | Einmal echt durchspielen, dann `pflege` |

**Leiter-Regel:** Was erst ein- oder zweimal vorkam, bekommt keinen Workflow. Sag das
freundlich, biete an, die Aufgabe jetzt einfach zu erledigen, und hör auf. Besteht die
Person darauf, baust du ihn trotzdem.

## Bereiche und Namen (Phase B)

Bereiche haben feste Nummern, bei allen Personen gleich:

| Thema | Ordner |
|---|---|
| Finanzen | `01_finanzen/` |
| Kommunikation | `02_kommunikation/` |
| Dokumente | `03_dokumente/` |
| Organisation | `04_organisation/` |
| Marketing | `05_marketing/` |

Passt keiner, legst du ein eigenes Thema ab `10_` an, mit der nächsten freien Nummer
(`10_vereine/`, `11_haus/`). Der Name des Workflows ist kurz, klein geschrieben, mit
Bindestrichen, aus den Worten der Person (`belege`, `offerten-nachfassen`).

## Bauen (Phase F)

Die Vorlagen liegen in `assets/` neben dieser Datei.

1. **Bereich, falls er fehlt:** `assets/bereich-CONTEXT.md` nach
   `<bereich>/CONTEXT.md` kopieren, `{{BEREICH}}` (etwa `01_finanzen`) und `{{THEMA}}`
   (etwa Finanzen) füllen. Im Haupt-Router `CONTEXT.md` eine Zeile direkt unter der
   letzten Zeile der Tabelle:
   ```
   | Finanzen | `01_finanzen/` | eingerichtet |
   ```
2. **Workflow:** `assets/workflow-CONTEXT.md` nach
   `<bereich>/workflows/<name>/CONTEXT.md` kopieren und aus den bestätigten Antworten
   füllen. Der Status ist `eingerichtet`. Alle Abschnitte bleiben: Status, Zweck, So
   arbeitest du, Quellen, Ausgabe, Grenzen, Test. Die Schritte sind so konkret, dass ein Assistent sie ohne Rückfrage
   ausführen kann.
3. **Router des Bereichs:** eine Zeile in die Tabelle von `<bereich>/CONTEXT.md`, direkt
   unter ihrer letzten Zeile:
   ```
   | <Aufgabe> | `workflows/<name>/` | eingerichtet |
   ```
4. **Gemeinsame Daten, nur wenn der Workflow sie braucht und sie fehlen:**
   `assets/marke-voice.md` nach `_marke/voice.md`, `assets/marke-firmendaten.md` nach
   `_marke/firmendaten.md`. Beide bleiben ENTWURF, bis die Person sie bestätigt.
5. **Werkzeuge:** Braucht der Workflow eine Python-Bibliothek, prüfst du zuerst in
   `_setup/werkzeuge.md`, ob sie schon da ist. Sonst installierst du sie mit den Pfaden
   von dort, in Anführungszeichen:
   `"<uv>" pip install --python "<python>" --cache-dir "<laufzeitordner>/cache" <paket>`
   und trägst sie dort ein.
6. **Schlüssel:** Braucht ein Programm einen Schlüssel oder ein Passwort, sagst du:
   «Bitte nicht hier in den Chat.» Du legst die Datei
   `<laufzeitordner>/secrets/<dienst>.env` an, mit den nötigen Namen und leeren Werten
   (`DIENST_TOKEN=`), und öffnest sie für die Person, ohne auf das Schliessen des Editors
   zu warten: auf dem Mac mit `open -e "<datei>"`, auf Windows in Git Bash mit
   `start "" notepad "<datei>"` und in PowerShell mit `Start-Process notepad "<datei>"`.
   Sie trägt die Werte ein und speichert. Die Werte liest du nie in den Chat, ein Skript
   liest sie selbst. In Dateien des Assistenten steht nur der Verweis auf die Datei.
7. **`CHANGELOG.md`:** Eintrag zuoberst mit Datum, was, warum und Rückweg
   (zum Beispiel «Ordner `01_finanzen/workflows/belege/` und die zwei Router-Zeilen
   löschen»).

Zwischenstände eines Laufs liegen im Workflow-Ordner, nie verstreut im Hauptordner. Kein
Ordner entsteht auf Vorrat.

## Testlauf (Phase G)

1. Lies nur `CONTEXT.md`, den Router des Bereichs und den neuen Vertrag, als hättest du
   das Gespräch vergessen. Kannst du den Workflow ohne Raten ausführen? Lücken behebst
   du in den Dateien, nicht im Chat.
2. Ein echter Lauf mit echten Daten, gemeinsam mit der Person.
3. Nach einem sauberen Lauf den Status auf `aktiv` setzen: im Vertrag, im Router des
   Bereichs und beim Bereich im Haupt-Router, falls dort noch `eingerichtet` steht. Das
   Datum hältst du unter «Test» fest.
4. Zum Schluss den Skill `pflege` anbieten («Soll ich kurz prüfen, ob alles sauber
   eingehängt ist?»).
