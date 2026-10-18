# Werkzeuge

Was auf diesem Computer für den Assistenten installiert ist. Workflows tragen hier ein,
was sie installieren, und prüfen vorher, ob es schon da ist.

## Pfade

Ruf diese Pfade immer genau so auf, in Anführungszeichen, denn sie enthalten oft
Leerzeichen. In PowerShell setzt du `&` vor den ersten Pfad eines Befehls. Wo eine
Anleitung `"<uv>"`, `"<python>"` oder `"<laufzeitordner>"` schreibt, gilt der Pfad von hier.

- **Laufzeitordner:** `"{{RUNTIME}}"`
- **uv:** `"{{UV}}"`
- **Python:** `"{{PYTHON}}"`

Im Laufzeitordner liegen `bin/` (uv und Programme wie `bexio`), `python/`, `venv/` (die
Python-Umgebung), `cache/` und `secrets/` (Passwörter und Schlüssel, eine Datei
`<dienst>.env` je Dienst). Nichts davon gehört in den Assistenten-Ordner.

## Python

{{PYTHON_STAND}}

Bibliotheken installierst du so in die Umgebung:
`"<uv>" pip install --python "<python>" --cache-dir "<laufzeitordner>/cache" <paket>`

## Installiert

| Werkzeug | Version | Wofür | Von welchem Workflow | Installiert am |
|---|---|---|---|---|
