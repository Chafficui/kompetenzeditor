#!/usr/bin/env python3
"""
Extraktion von Qualifikationszielen aus externen Modulhandbüchern.
Nutzt pdftotext (poppler) für die Text-Extraktion.

Unterstützte Formate:
  - THM (Maschinenbau, WIng): Fach-/Methoden-/Sozial-/Selbstkompetenzen als Bulletpoints
  - Uni Kassel (Soziale Arbeit): Tabellarisches Format mit Fließtext
  - TU Darmstadt (Informatik): Nummerierte Abschnitte mit Fließtext/Bullets

Output: CSV mit (studiengang, hochschule, modul_id, modulname, satz_nr, satz)
"""

import csv
import re
import subprocess
from pathlib import Path

ABBREVIATIONS = [
    ('z. B.', 'z∅B∅'), ('z.B.', 'z∅B∅'), ('u. a.', 'u∅a∅'), ('u.a.', 'u∅a∅'),
    ('d. h.', 'd∅h∅'), ('d.h.', 'd∅h∅'), ('o. ä.', 'o∅ä∅'), ('o.ä.', 'o∅ä∅'),
    ('bzw.', 'bzw∅'), ('etc.', 'etc∅'), ('ggf.', 'ggf∅'), ('inkl.', 'inkl∅'),
    ('vgl.', 'vgl∅'), ('Prof.', 'Prof∅'), ('Dr.', 'Dr∅'), ('Nr.', 'Nr∅'),
    ('ca.', 'ca∅'), ('evtl.', 'evtl∅'), ('sog.', 'sog∅'), ('Abs.', 'Abs∅'),
    ('gem.', 'gem∅'), ('usw.', 'usw∅'),
]

OUTPUT_DIR = Path(__file__).parent.parent / "data"
EXTERN_DIR = Path(__file__).parent.parent / "materials" / "modulhandbuecher_extern"


def pdf_to_text(pdf_path: Path) -> str:
    result = subprocess.run(
        ['pdftotext', str(pdf_path), '-'],
        capture_output=True, text=True
    )
    return result.stdout


def protect_abbreviations(text: str) -> str:
    for orig, repl in ABBREVIATIONS:
        text = text.replace(orig, repl)
    return text


def restore_abbreviations(text: str) -> str:
    return text.replace('∅', '.')


def clean_sentences(raw_text: str) -> list[str]:
    """Clean raw competency text into individual sentences."""
    text = raw_text.strip()
    if not text:
        return []

    # Remove standalone page numbers
    text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)

    # Normalize bullet markers
    text = re.sub(r'[•●▪‣]\s*', '§B§', text)
    text = re.sub(r'\n\s*[-–]\s+', '\n§B§', text)

    # Handle "Die Studierenden können\n" as prefix
    text = re.sub(
        r'(Die Studierenden können)\s*\n',
        r'§PREFIX§\1 §\n',
        text
    )

    # Fix hyphenated line breaks
    text = re.sub(r'(\w)-\n\s*(\w)', r'\1\2', text)

    # Join continuation lines (line doesn't start with bullet or section header)
    text = re.sub(r'\n(?!§|Die Studierenden|Fachkompetenz|Methodenkompetenz|Sozialkompetenz|Selbstkompetenz|Schlüsselkompetenz|Qualifikationsziel|\d)', ' ', text)

    # Normalize whitespace
    text = re.sub(r'  +', ' ', text)

    # Split on bullets and newlines
    parts = re.split(r'§B§|\n', text)

    sentences = []
    current_prefix = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Handle prefix markers
        if '§PREFIX§' in part:
            prefix_match = re.search(r'§PREFIX§(.+?)§', part)
            if prefix_match:
                current_prefix = prefix_match.group(1)
            part = re.sub(r'§PREFIX§.+?§\s*', '', part).strip()
            if not part:
                continue

        # Skip section headers
        if re.match(r'^(Fach|Methoden|Sozial|Selbst|Schlüssel)kompetenz', part):
            continue
        if part.startswith("Qualifikationsziele"):
            continue
        if re.match(r'^Methodenkompetenz', part):
            continue
        # Skip lines that are just competency category headers with optional parenthetical
        if re.match(r'^(Fach|Methoden|Sozial|Selbst)kompetenzen?\s*(\(.*\))?\s*$', part):
            continue

        # Protect abbreviations
        part = protect_abbreviations(part)

        # Skip very short fragments
        if len(part) < 12:
            continue

        # Skip header-only lines
        if re.match(r'^Die Studierenden\s*(können)?\s*$', part):
            if 'können' in part:
                current_prefix = "Die Studierenden können "
            continue

        # Prepend prefix if sentence starts lowercase
        if part[0].islower() and current_prefix:
            part = current_prefix + part

        # If it's a full sentence with subject, reset prefix
        if re.match(r'^(Die Studierenden|Sie |Nach )', part, re.IGNORECASE):
            current_prefix = ""

        # Split on sentence boundaries (period + uppercase)
        sub_parts = re.split(r'(?<=\.)\s+(?=[A-Z])', part)
        for sp in sub_parts:
            sp = sp.strip()
            if len(sp) < 12:
                continue
            sp = restore_abbreviations(sp)
            # Final cleanup
            sp = re.sub(r'\s+', ' ', sp).strip()
            sentences.append(sp)

    return sentences


def extract_thm_maschinenbau(pdf_path: Path, studiengang: str, hochschule: str) -> list[dict]:
    """Extract from THM Maschinenbau format (Modulcode + Modulbezeichnung on same header line)."""
    text = pdf_to_text(pdf_path)
    rows = []

    # Split by "Qualifikationsziele und angestrebte Lernergebnisse"
    quali_blocks = re.split(r'(?=Qualifikationsziele und angestrebte Lernergebnisse)', text)

    for i, block in enumerate(quali_blocks[1:], 1):
        preceding = quali_blocks[i - 1]

        # Maschinenbau pattern: "Modulcode  Modulbezeichnung...\nB0010  Mathematik 1 / Mathematics 1"
        mb_match = re.search(
            r'Modulcode\s+Modulbezeichnung.*?\n\s*(\w+)\s+(.+?)(?:\n|$)',
            preceding
        )
        if not mb_match:
            continue

        modul_id = mb_match.group(1).strip()
        modulname = re.sub(r'\s*/\s*.+$', '', mb_match.group(2).strip())

        # Extract text until next module boundary
        quali_match = re.search(
            r'Qualifikationsziele und angestrebte Lernergebnisse\s*\n(.*?)(?=\nVerwendbarkeit|\nStudiensemester|\nDauer des Moduls|$)',
            block,
            re.DOTALL
        )
        if not quali_match:
            continue

        sentences = clean_sentences(quali_match.group(1).strip())
        for j, satz in enumerate(sentences, 1):
            rows.append({
                'studiengang': studiengang,
                'hochschule': hochschule,
                'modul_id': modul_id,
                'modulname': modulname,
                'satz_nr': j,
                'satz': satz,
            })

    return rows


def extract_thm_wing(pdf_path: Path, studiengang: str, hochschule: str) -> list[dict]:
    """Extract from THM WIng format (Modulcode on separate line, bullet points with •)."""
    text = pdf_to_text(pdf_path)
    rows = []

    # Split by "Qualifikationsziele und angestrebte Lernergebnisse"
    quali_blocks = re.split(r'(?=Qualifikationsziele und angestrebte Lernergebnisse)', text)

    for i, block in enumerate(quali_blocks[1:], 1):
        preceding = quali_blocks[i - 1]

        # WIng pattern: "Modulbezeichnung (deutsch / englisch)\n<name> / <english>"
        name_match = re.search(
            r'Modulbezeichnung\s*\(deutsch.*?\)\s*\n\s*(.+?)(?:\n|$)',
            preceding
        )
        code_match = re.search(r'Modulcode\s*\n\s*(\w+)', preceding)

        if not name_match or not code_match:
            continue

        modul_id = code_match.group(1).strip()
        modulname = re.sub(r'\s*/\s*.+$', '', name_match.group(1).strip())

        # Extract text until next module boundary
        quali_match = re.search(
            r'Qualifikationsziele und angestrebte Lernergebnisse\s*\n(.*?)(?=\nVerwendbarkeit|\nStudiensemester|\nDauer des Moduls|\n\d{4}\s+\w|$)',
            block,
            re.DOTALL
        )
        if not quali_match:
            continue

        sentences = clean_sentences(quali_match.group(1).strip())
        for j, satz in enumerate(sentences, 1):
            rows.append({
                'studiengang': studiengang,
                'hochschule': hochschule,
                'modul_id': modul_id,
                'modulname': modulname,
                'satz_nr': j,
                'satz': satz,
            })

    return rows


def extract_uni_kassel_sa(pdf_path: Path, studiengang: str, hochschule: str) -> list[dict]:
    """Extract from Uni Kassel Soziale Arbeit tabular format."""
    text = pdf_to_text(pdf_path)
    rows = []

    # Modules separated by "Nummer/Code"
    module_splits = re.split(r'(?=Nummer/Code\s)', text)

    for block in module_splits[1:]:
        code_match = re.search(r'Nummer/Code\s+(.+)', block)
        name_match = re.search(r'Modulname\s+(.+)', block)
        if not code_match or not name_match:
            continue

        modul_id = code_match.group(1).strip()
        modulname = name_match.group(1).strip()

        # The competency field label wraps across lines:
        # "Lernergebnisse, Kompe-\ntenzen, Qualifikations-\nziele"
        # Content follows until "Lehrveranstaltungsarten"
        quali_match = re.search(
            r'(?:Lernergebnisse|Qualifikations-?\s*ziele)\s+(.*?)(?=\nLehrveranstaltungsarten|\nLehr-\s*und\s*Lernmethoden)',
            block,
            re.DOTALL
        )
        if not quali_match:
            continue

        quali_text = quali_match.group(1).strip()
        # Remove wrapped table field label fragments
        quali_text = re.sub(r'^.*?(?:tenzen,\s*Qualifikations-?\s*ziele)\s*', '', quali_text, flags=re.DOTALL)
        # Also remove if only partial label
        quali_text = re.sub(r'^.*?ziele\s+', '', quali_text, count=1)

        sentences = clean_sentences(quali_text)

        for j, satz in enumerate(sentences, 1):
            rows.append({
                'studiengang': studiengang,
                'hochschule': hochschule,
                'modul_id': modul_id,
                'modulname': modulname,
                'satz_nr': j,
                'satz': satz,
            })

    return rows


def extract_tu_darmstadt(pdf_path: Path, studiengang: str, hochschule: str) -> list[dict]:
    """Extract from TU Darmstadt format (numbered sections with blank lines)."""
    text = pdf_to_text(pdf_path)
    rows = []

    # Remove footer lines
    text = re.sub(r'Modulhandbuch B\.\s*Sc\.\s*Informatik\s*\d+', '', text)

    # Modules start with "Modulname\n<name>"
    module_splits = re.split(r'(?=\nModulname\n)', text)

    for block in module_splits[1:]:
        name_match = re.search(r'Modulname\n\s*(.+?)\n', block)
        if not name_match:
            continue
        modulname = name_match.group(1).strip()

        code_match = re.search(r'Modul Nr\.\s*\n\s*([^\n]+)', block)
        modul_id = code_match.group(1).strip() if code_match else modulname[:20]
        # Clean: sometimes contains trailing table content
        modul_id = modul_id.split()[0] if modul_id else modulname[:20]

        # Section number is on its own line, then blank line, then title:
        # "3\n\nQualifikationsziele / Lernergebnisse\n"
        # Ends at "4\n\nVoraussetzung" or similar
        quali_match = re.search(
            r'\n\d\s*\n+\s*Qualifikationsziele\s*/?\s*Lernergebnisse\s*\n(.*?)(?=\n\d\s*\n+\s*(?:Voraussetzung|Prüfungsform)|$)',
            block,
            re.DOTALL
        )
        if not quali_match:
            continue

        quali_text = quali_match.group(1).strip()
        sentences = clean_sentences(quali_text)

        for j, satz in enumerate(sentences, 1):
            rows.append({
                'studiengang': studiengang,
                'hochschule': hochschule,
                'modul_id': modul_id,
                'modulname': modulname,
                'satz_nr': j,
                'satz': satz,
            })

    return rows


PDF_CONFIGS = [
    {
        'file': 'THM_Maschinenbau_BSc_MHB.pdf',
        'studiengang': 'Maschinenbau (B.Sc.)',
        'hochschule': 'TH Mittelhessen',
        'extractor': extract_thm_maschinenbau,
    },
    {
        'file': 'THM_Wirtschaftsingenieurwesen_BSc_MHB.pdf',
        'studiengang': 'Wirtschaftsingenieurwesen (B.Sc.)',
        'hochschule': 'TH Mittelhessen',
        'extractor': extract_thm_wing,
    },
    {
        'file': 'Uni_Kassel_Soziale_Arbeit_BA_MHB.pdf',
        'studiengang': 'Soziale Arbeit (B.A.)',
        'hochschule': 'Universität Kassel',
        'extractor': extract_uni_kassel_sa,
    },
    {
        'file': 'TU_Darmstadt_Informatik_BSc_MHB_PO2023.pdf',
        'studiengang': 'Informatik (B.Sc.)',
        'hochschule': 'TU Darmstadt',
        'extractor': extract_tu_darmstadt,
    },
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_csv = OUTPUT_DIR / "qualifikationsziele_extern.csv"

    all_rows = []

    for config in PDF_CONFIGS:
        pdf_path = EXTERN_DIR / config['file']
        if not pdf_path.exists():
            print(f"WARNUNG: {pdf_path} nicht gefunden, übersprungen.")
            continue

        print(f"\n--- {config['hochschule']}: {config['studiengang']} ---")

        rows = config['extractor'](
            pdf_path,
            config['studiengang'],
            config['hochschule'],
        )

        modules = set(r['modul_id'] for r in rows)
        print(f"  Module: {len(modules)}, Sätze: {len(rows)}")

        if rows:
            for r in rows[:3]:
                print(f"    [{r['modul_id']}] {r['satz'][:100]}...")

        all_rows.extend(rows)

    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'studiengang', 'hochschule', 'modul_id', 'modulname', 'satz_nr', 'satz'
        ])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n{'='*60}")
    print(f"GESAMT: {len(all_rows)} Sätze aus {len(set(r['hochschule'] for r in all_rows))} Hochschulen")

    for hs in sorted(set(r['hochschule'] for r in all_rows)):
        hs_rows = [r for r in all_rows if r['hochschule'] == hs]
        modules = set(r['modul_id'] for r in hs_rows)
        programs = set(r['studiengang'] for r in hs_rows)
        print(f"  {hs}: {len(modules)} Module, {len(hs_rows)} Sätze ({', '.join(programs)})")

    print(f"\nOutput: {output_csv}")


if __name__ == "__main__":
    main()
