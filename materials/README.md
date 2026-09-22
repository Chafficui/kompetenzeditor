# Materials (Quell-PDFs)

Der Inhalt dieses Ordners ist per `.gitignore` von der Versionierung ausgeschlossen
(Regel `materials/**` in der Root-`.gitignore`, nur diese README ist ausgenommen), da die
Modulhandbücher urheberrechtlich bei den jeweiligen Hochschulen liegen. Wer die
Extraktionsskripte in `code_projects/` ausführen möchte, muss die PDFs selbst hier
ablegen.

Der vollständige Basis-Datensatz der Arbeit besteht aus **diesen PDFs + den CSV-Dateien
in `data/`**. Ohne die PDFs lässt sich nur mit den bereits extrahierten/annotierten Daten
in `data/` weiterarbeiten (siehe [`data/README.md`](../data/README.md)); die
Extraktionsskripte selbst benötigen die Originale.

## Erwartete Struktur

### `materials/Modulhandbücher/` — Hochschule Fulda

Erwartet von `code_projects/extract_qualifikationsziele.py`. Die folgenden 15
Dateinamen sind **erwartete Dateinamen** (aus den Studiengangsnamen abgeleitet,
Leerzeichen durch Bindestriche ersetzt, Suffix `-Modulbeschreibungen.pdf`):

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

Erwartet von `code_projects/extract_externe_modulhandbuecher.py`:

```
materials/modulhandbuecher_extern/
├── THM_Maschinenbau_BSc_MHB.pdf
├── THM_Wirtschaftsingenieurwesen_BSc_MHB.pdf
├── Uni_Kassel_Soziale_Arbeit_BA_MHB.pdf
└── TU_Darmstadt_Informatik_BSc_MHB_PO2023.pdf
```

## PDFs ins Repository aufnehmen

Da `materials/**` per `.gitignore` ausgeschlossen ist, werden Dateien in diesem Ordner
standardmäßig **nicht** committet. Wer die PDFs dennoch versionieren möchte:

```bash
git add -f materials/
```

Alternativ die beiden Zeilen `materials/**` und `!materials/README.md` in der
Root-`.gitignore` entfernen.
