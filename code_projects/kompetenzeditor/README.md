# Kompetenzeditor (Frontend)

Nuxt-4-Frontend für den Kompetenzeditor: ein Editor für Kompetenzformulierungen
(Qualifikationsziele) in Modulhandbüchern, der Texte live gegen das FastAPI-Backend
(`code_projects/backend/`) analysiert. Der Editor markiert erkannte Verben, zeigt
Taxonomiestufen nach Anderson/Krathwohl an, weist auf problematische Formulierungen hin
und schlägt ähnliche, gut bewertete Formulierungen aus dem Gold-Standard vor.

Dieses Werkzeug ist Teil der Masterarbeit von Felix Beinßen (Hochschule Fulda). Der
Ordner `code_projects/lot_kohnert_prototype/` enthält zum Vergleich den
Vorgänger-Prototyp von Ludwig Loth — er ist eigenständig und nicht Teil dieses Tools.

## Technologie-Stack

- [Nuxt 4](https://nuxt.com/) (Vue 3, SPA-Modus — `routeRules: { '/**': { ssr: false } }`)
- [Vuetify](https://vuetifyjs.com/) für UI-Komponenten
- [TipTap](https://tiptap.dev/) als Rich-Text-Editor
- [Pinia](https://pinia.vuejs.org/) für den State (welche Kompetenzbeschreibung gerade
  bearbeitet wird)
- [Dexie](https://dexie.org/) (IndexedDB) für die **lokale** Speicherung der
  Kompetenzbeschreibungen im Browser — es gibt keine serverseitige Persistenz
- Paketmanager: [bun](https://bun.sh/) (`bun.lock` liegt im Repo); npm funktioniert
  ebenso

## Voraussetzung: Backend

Das Frontend benötigt das laufende FastAPI-Backend aus `code_projects/backend/` für die
Textanalyse. Der Dev-Server proxyt `/api/**` an `http://127.0.0.1:8000` (siehe
`nuxt.config.ts`). Setup des Backends: siehe Root-`README.md`, Abschnitt „Schnellstart“.

## Schnellstart

```bash
bun install
bun run dev
```

Der Dev-Server läuft standardmäßig auf `http://localhost:3000`. Alternativ mit npm:

```bash
npm install
npm run dev
```

### Backend per Docker

`docker-compose.yml` in diesem Verzeichnis baut ausschließlich das Backend (aus
`../backend/Dockerfile`) und mountet dessen `models/`- und `data/`-Verzeichnisse vom
Host:

```bash
docker compose up --build
```

Die Modelle (`code_projects/backend/models/`) müssen vorher lokal erzeugt worden sein
(`train_classifiers.py`, `build_reference_db.py`, siehe Root-`README.md`), da sie nur
gemountet, nicht im Image erzeugt werden.

### Weitere Skripte

```bash
bun run build      # Produktions-Build
bun run generate    # statische Generierung
bun run preview     # Produktions-Build lokal testen
```

## Struktur (`app/`)

| Pfad | Inhalt |
|---|---|
| `pages/index.vue` | Übersicht gespeicherter Kompetenzbeschreibungen (aus IndexedDB) |
| `pages/editor.vue` | TipTap-Editor mit Verb-Highlighting, Score-Anzeige und Vorschlägen |
| `pages/settings.vue` | Zeigt Backend-Status (`/api/health`) und Lade-Status der Modelle |
| `composables/useAnalysis.js` | Ruft `POST /api/analyze` auf und wertet das Ergebnis für die UI aus (Highlights, Score, Set-Analyse) |
| `composables/useDatabase.js` | Dexie/IndexedDB-Zugriff: Kompetenzbeschreibungen, Verblisten für die clientseitige Vorbefüllung |
| `stores/editor.js` | Pinia-Store für die aktuell bearbeitete Kompetenzbeschreibung |
| `extensions/verbHighlight.js` | TipTap-Extension zum Hervorheben erkannter Verben im Editor |
| `utils/levenshtein.js` | Hilfsfunktion (Textabgleich) |

Die eigentliche NLP-Logik (Regeln, Embeddings, Klassifikation) liegt vollständig im
Backend; das Frontend ruft nur `GET /api/health` und `POST /api/analyze` auf und stellt
das Ergebnis dar.

## Lizenz

Der Code steht unter der MIT-Lizenz des Repositories (siehe `LICENSE` im Wurzelverzeichnis).
