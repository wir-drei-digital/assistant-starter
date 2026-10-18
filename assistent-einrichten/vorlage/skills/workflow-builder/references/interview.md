# Interview: die Fragen, Phase A bis E

Die Fragen sind für dich geschrieben. Stell sie natürlich, in den Worten der Person,
zwei, drei auf einmal. Nach jeder Phase fasst du in einem kurzen Absatz zusammen, was du
verstanden hast, und lässt korrigieren, bevor du weitergehst.

## A. Verstehen

1. **Was soll passieren?** «Erklär es mir wie einer neuen Mitarbeiterin: Was kommt
   rein, was soll am Ende rauskommen?»
2. **Einmal echt durchgehen.** «Denk an das letzte Mal, als du das von Hand gemacht
   hast. Was kam zuerst, was dann?»
3. **Wie oft?** Täglich, wöchentlich, je Ereignis, ein paarmal im Jahr. Kam es erst
   ein- oder zweimal vor, gilt die Leiter-Regel aus `SKILL.md`.
4. **Was löst es aus?** Die Person entscheidet, eine Mail kommt, ein Datum ist erreicht,
   jemand fragt danach. Das wird die Zeile «Auslöser» im Vertrag.
5. **Wo prüfst du, bevor es weitergeht?** Jeder solche Moment wird ein Prüfpunkt mit
   einer konkreten Handlung. Erzeugt der Workflow ein Dokument, schlägst du davor eine
   Selbstprüfung vor: «Bevor du es anschaust, prüfe ich meinen Entwurf selbst gegen
   deine Regeln.»
6. **Was ist jedes Mal gleich, was ist neu?** Gleiches (Regeln, eine Vorlage, eine
   Liste) wird eine Datei im Workflow-Ordner, zum Beispiel `regeln.md`. Neues sind die
   Daten des Laufs.
7. **Wie sieht «fertig» aus?** Eine Datei, ein gefüllter Ordner, eine nachgeführte
   Liste, ein Entwurf.

## B. Ort und Name

Meist ohne Fragen. Du liest `CONTEXT.md` und die Bereichs-Router und schlägst vor:
«Ich lege das als `belege` im Bereich Finanzen ab, also unter
`01_finanzen/workflows/belege/`. Passt das?»

Offen fragst du nur, wenn die Aufgabe offensichtlich in einen bestehenden Workflow
gehört oder einen ersetzt. Dann klärst du, welchen.

## C. Quellen und Schreiben

1. **Lesen:** «Wo liegt, was ich dafür brauche?» Ordner, Dateien, Mails. Was ausserhalb
   des Assistenten-Ordners liegt, wird nur gelesen, ausser die Person sagt ausdrücklich
   etwas anderes.
2. **Schreiben:** Standard ist der Workflow-Ordner. Soll etwas anderswo landen, nennst du
   jeden Zielordner einzeln und fragst: «Darf ich in [Ordner] schreiben? Nur dorthin?»
   Jedes Ja kommt mit Datum in den Abschnitt «Quellen» des Vertrags.
3. **Ausschlüsse:** «Ist etwas Heikles dabei, etwa Verträge, Personaldaten oder
   Gesundheitsdaten?» Was draussen bleibt, steht namentlich unter «Grenzen». Den
   Entscheid trifft die Person.

## D. Programme und Werkzeuge

1. «Spielt ein anderes Programm eine Rolle: Mail, Excel, Word, ein Webdienst, etwas mit
   Anmeldung?»
2. Wenn ja: Wähl den einfachsten Zugang, der funktioniert. Lokale Dateien vor Exporten,
   Exporte vor Schnittstellen, lesen vor schreiben. Bau in kleinen Schritten und prüf
   jeden an echten Daten.
3. Braucht es einen Schlüssel: die Regel aus Schritt 6 in `SKILL.md`. Wurde einer doch in
   den Chat geschrieben, bittest du die Person, ihn beim Dienst zu ersetzen und den neuen
   direkt in die Datei zu legen.
4. Braucht es eine Python-Bibliothek: Schritt 5 in `SKILL.md`. Gibt es keine
   Python-Umgebung, sag es und biete einen Weg ohne Skript an.

## E. Regeln durchgehen (Pflicht vor dem Bauen)

Jede Regel, die dieser Workflow trägt, legst du als Vorschlag vor, eine Zeile je Regel,
«passt» oder «passt nicht»:

- was er liest, wohin er schreibt, was er nie tut
- jedes Schreibrecht ausserhalb des Workflow-Ordners
- jeder Ausschluss
- an jedem Prüfpunkt: was genau schaut die Person an
- bei Programmen: welches Konto, was er dort darf, wo der Schlüssel liegt
- ob der Workflow `_marke/voice.md` oder `_marke/firmendaten.md` braucht

Erst wenn jede Zeile bestätigt ist, beginnt Phase F. Was unbestätigt bleibt, kommt als
ENTWURF in den Vertrag.
