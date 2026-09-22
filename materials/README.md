# Materials (Quell-PDFs)

Dieser Ordner enthält die Modulhandbuch-PDFs, aus denen die Qualifikationsziele
extrahiert wurden (19 Dateien, 4 Hochschulen). Zusammen mit den CSV-Dateien in `data/`
bilden sie den vollständigen Basis-Datensatz der Arbeit (siehe
[`data/README.md`](../data/README.md)).

Die PDFs sind öffentlich zugängliche Modulhandbücher der jeweiligen Hochschulen; das
Urheberrecht liegt bei diesen. Sie sind hier ausschließlich zur Nachvollziehbarkeit und
Reproduzierbarkeit der Studie enthalten und fallen nicht unter die MIT-/CC-BY-Lizenz des
Repositories.

## Struktur

### `materials/Modulhandbücher/` — Hochschule Fulda

Eingabe für `code_projects/extract_qualifikationsziele.py` (15 Dateien; der Studiengangsname
wird aus dem Dateinamen abgeleitet):

```
materials/Modulhandbücher/
├── Angewandte-Informatik-BA-Modulbeschreibungen.pdf
├── Angewandte-Informatik-MA-Modulbeschreibungen.pdf
├── Data-Science-MA-Modulbeschreibungen.pdf
├── Digitale-Medien-BA-Modulbeschreibungen.pdf
├── Elektrotechnik-und-Informationstechnik-BA-Modulbeschreibungen.pdf
├── Erneuerbare-Energien-BA-Modulbeschreibungen.pdf
├── Food-Processing-MA-Modulbeschreibungen.pdf
├── Global-Software-Development-MA-Modulbeschreibungen.pdf
├── Industrielle-Biotechnologie-BA-Modulbeschreibungen.pdf
├── Lebensmitteltechnologie-BA-Modulbeschreibungen.pdf
├── Mechatronik-BA-Modulbeschreibungen.pdf
├── Wirtschaftsinformatik-BA-Modulbeschreibungen.pdf
├── Wirtschaftsingenieurwesen-BA-Modulbeschreibungen.pdf
├── Wirtschaftsingenieurwesen-MA-Modulbeschreibungen.pdf
└── Wirtschaftsingenieurwesen-Life-Sciences-BA-Modulbeschreibungen.pdf
```

### `materials/modulhandbuecher_extern/` — externe Hochschulen

Eingabe für `code_projects/extract_externe_modulhandbuecher.py`:

```
materials/modulhandbuecher_extern/
├── THM_Maschinenbau_BSc_MHB.pdf
├── THM_Wirtschaftsingenieurwesen_BSc_MHB.pdf
├── Uni_Kassel_Soziale_Arbeit_BA_MHB.pdf
└── TU_Darmstadt_Informatik_BSc_MHB_PO2023.pdf
```
