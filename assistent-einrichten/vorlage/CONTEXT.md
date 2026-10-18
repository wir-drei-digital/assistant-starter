# Router: welche Aufgabe, welcher Ordner

Jeder Bereich hat eine eigene `CONTEXT.md` mit seinen Workflows und Regeln. Lade nur,
was die Aufgabe braucht.

| Aufgabe | Ordner | Status |
|---|---|---|
| Assistent pflegen: prüfen, aufräumen, eine Regel aufnehmen | `{{SKILLS}}/pflege/` | aktiv |
| Eigenen Workflow bauen | `{{SKILLS}}/workflow-builder/` | aktiv |

Je Bereich kommt eine Zeile dazu, sobald sein erster Workflow entsteht, zum Beispiel
«Finanzen» mit dem Ordner `01_finanzen/` und dem Status `eingerichtet`. Die Zeile legt
der Workflow an, der den Bereich braucht, oder der Skill `workflow-builder`, direkt unter
der letzten Zeile der Tabelle. Der Ordner steht immer in Backticks und endet mit «/».

## Statusmodell

- `geplant`: angelegt, aber noch nicht mit echten Daten getestet
- `eingerichtet`: verbunden, ein echter Testlauf steht aus
- `aktiv`: im Betrieb

Ein Workflow wechselt erst nach einem sauberen echten Durchlauf auf `aktiv`, in seiner
`CONTEXT.md` und in der Zeile im Router seines Bereichs. Hier, im Haupt-Router, wechselt
der Bereich mit seinem ersten aktiven Workflow von `eingerichtet` auf `aktiv`.

## Wenn keine Zeile passt

Wenn keine Zeile passt: einmalig erledigen, wiederkehrend → workflow-builder.
Im Zweifel fragen.

## Zum Nachlesen

- Was zuletzt geändert wurde: `CHANGELOG.md`
- Was installiert ist: `_setup/werkzeuge.md`
- Wann und wie wirdrei.digital hilft: `support.md`
