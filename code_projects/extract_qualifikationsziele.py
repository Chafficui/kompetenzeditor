#!/usr/bin/env python3
"""
Extracts Qualifikationsziele from FBAI Modulhandbuch PDFs.
Output: CSV with columns (studiengang, modul_id, modulname, satz_nr, satz)

Strategy v6: Page-based extraction.
  - Process each PDF page individually
  - Find module ID + name on the SAME page as Qualifikationsziele
  - Handles both ID-at-top and ID-at-bottom page layouts
  - Multi-page Qualifikationsziele: content continues until "Inhalte" is found
"""

import csv
import re
from pathlib import Path

import fitz  # PyMuPDF

ABBREVIATIONS = [
    ('z. B.', 'z∅B∅'), ('z.B.', 'z∅B∅'), ('u. a.', 'u∅a∅'), ('u.a.', 'u∅a∅'),
    ('d. h.', 'd∅h∅'), ('d.h.', 'd∅h∅'), ('o. ä.', 'o∅ä∅'), ('o.ä.', 'o∅ä∅'),
    ('bzw.', 'bzw∅'), ('etc.', 'etc∅'), ('ggf.', 'ggf∅'), ('inkl.', 'inkl∅'),
    ('vgl.', 'vgl∅'), ('Prof.', 'Prof∅'), ('Dr.', 'Dr∅'), ('Nr.', 'Nr∅'),
    ('ca.', 'ca∅'), ('evtl.', 'evtl∅'), ('sog.', 'sog∅'),
]

# Module ID pattern: 2-4 uppercase letters + 3-5 digits
MODULE_ID_RE = re.compile(r'([A-Z]{2,4}\d{3,5})')


def parse_studiengang(filename: str) -> str:
    name = filename.replace("-Modulbeschreibungen.pdf", "")
    name = name.replace("-", " ")
    if " BA " in name or name.endswith(" BA"):
        name = name.replace(" BA", "") + " (B.Sc.)"
    elif " MA " in name or name.endswith(" MA"):
        name = name.replace(" MA", "") + " (M.Sc.)"
    return name.strip()


def find_module_id_on_page(page_text: str) -> tuple[str, str] | None:
    """
    Find the module ID and name on a page.
    Handles two layouts:
      1. ID on its own line, name on next line (AI PDFs — ID at bottom)
      2. ID + name on the same line area (LT PDFs — ID at top)
    Filters out TOC entries (names with dot-leaders).
    """
    # Pattern: ID on own line, name on next line
    matches = list(re.finditer(
        r'^([A-Z]{2,4}\d{3,5})\s*\n([^\n]+?)$',
        page_text, re.MULTILINE
    ))

    for m in matches:
        name = m.group(2).strip()
        # Skip TOC entries
        if '...' in name or '…' in name or re.search(r'\.{2,}', name):
            continue
        # Skip very short names or numeric-only
        if len(name) < 3 or name.isdigit():
            continue
        # Skip if name is "Modulcode FB:" or similar metadata
        if name.startswith('Modulcode') or name.startswith('Englische'):
            continue
        return m.group(1), name

    return None


def extract_modules_page_based(pdf_path: Path):
    """
    Page-based extraction: for each page with Qualifikationsziele,
    find the module ID on the same page, extract content.
    Yields (modul_id, modulname, quali_raw_text).
    """
    with fitz.open(pdf_path) as doc:
        pages = [page.get_text() for page in doc]

    for pg_idx, page_text in enumerate(pages):
        # Find Qualifikationsziele on this page
        quali_match = re.search(r'Qualifikationsziele:?\s*\n', page_text)
        if not quali_match:
            continue

        # Find module ID on this page
        module_info = find_module_id_on_page(page_text)
        if not module_info:
            # Try previous page (in case of split layout)
            if pg_idx > 0:
                module_info = find_module_id_on_page(pages[pg_idx - 1])
            if not module_info:
                continue

        modul_id, modulname = module_info

        # Extract Qualifikationsziele text
        quali_start = quali_match.end()
        remaining = page_text[quali_start:]

        # End at "2\nInhalte" or "Inhalte des Moduls"
        end_match = re.search(
            r'(?:\n\s*2\s*\n\s*Inhalte|\nInhalte des Moduls)',
            remaining
        )

        if end_match:
            quali_text = remaining[:end_match.start()]
        else:
            # Qualifikationsziele might continue on next page
            quali_text = remaining
            if pg_idx + 1 < len(pages):
                next_page = pages[pg_idx + 1]
                # Only continue if next page doesn't start a new module
                if not re.search(r'Qualifikationsziele:?\s*\n', next_page[:500]):
                    end_match2 = re.search(
                        r'(?:\n\s*2\s*\n\s*Inhalte|\nInhalte des Moduls)',
                        next_page
                    )
                    if end_match2:
                        quali_text += '\n' + next_page[:end_match2.start()]
                    else:
                        quali_text += '\n' + next_page[:2000]

        yield modul_id, modulname, quali_text.strip()


def clean_quali_text(raw: str) -> list[str]:
    """Process raw Qualifikationsziele text into clean sentences."""
    # Step 0: Mark standalone "Die Studierenden …" headers BEFORE line-joining
    # They appear on their own line in the PDF and would otherwise merge into paragraphs
    text = re.sub(
        r'\nDie Studierenden\s*[…\.]{0,3}\s*\n',
        '\n§H§\n', raw
    )
    text = re.sub(
        r'^Die Studierenden\s*[…\.]{0,3}\s*\n',
        '§H§\n', text
    )
    text = re.sub(
        r'\nThe students\s*[…\.]{0,3}\s*\n',
        '\n§HE§\n', text, flags=re.IGNORECASE
    )

    # Step 1: Normalize bullet markers (bullet on its own line or inline)
    text = re.sub(r'[•●▪‣·]\s*\n', '§B§', text)
    text = re.sub(r'[•●▪‣·]\s+', '§B§', text)
    # Also handle dash bullets
    text = re.sub(r'\n\s*[-–]\s+', '\n§B§', text)

    # Step 2: Fix hyphenated line breaks
    text = re.sub(r'-\n\s*', '⌀', text)  # temp marker

    # Step 3: Join remaining line breaks (PDF wrapping) but not before bullets/headers
    text = re.sub(r'\n(?!§[BH])', ' ', text)

    # Step 4: Restore hyphenation (remove hyphen + join)
    text = text.replace('⌀', '')

    # Step 5: Split on bullet markers
    parts = [p.strip() for p in text.split('§B§') if p.strip()]

    sentences = []
    header_prefix = ""

    for part in parts:
        header_set_this_part = False

        # Handle header markers BEFORE length check (markers are short)
        if '§H§' in part or '§HE§' in part:
            is_english = '§HE§' in part
            part = part.replace('§H§', '').replace('§HE§', '').strip()
            header_prefix = "The students " if is_english else "Die Studierenden "
            header_set_this_part = True
            if not part or len(part) < 5:
                continue

        if len(part) < 5:
            continue

        # Detect standalone header patterns (various formats)
        if re.match(r'^Die Studierenden\s*[…\.]{0,3}\s*$', part):
            header_prefix = "Die Studierenden "
            continue
        if re.match(r'^The students\s*[…\.]{0,3}\s*$', part, re.IGNORECASE):
            header_prefix = "The students "
            continue
        # "Die Teilnehmenden/Studierenden sind in der Lage:" / "...in der Lage ..."
        if re.match(
            r'^(Die\s+)?(Studierenden|Teilnehmenden|Teilnehmer\*?innen)\s+sind\s+in\s+der\s+Lage\s*[:\.…]*\s*$',
            part, re.IGNORECASE
        ):
            continue
        # "Nach erfolgreicher Teilnahme...sind die Studierenden in der Lage ..."
        if re.search(r'sind\s+(die\s+)?(Studierenden|Teilnehmenden)\s+in\s+der\s+Lage\s*[:\.…]*\s*$', part):
            continue

        # If part has its own subject, don't prepend — but don't reset
        # header_prefix if it was just set by a §H§ marker in this same part
        if re.match(r'^(Die Studierenden|The students|Sie |They )\s*\w', part, re.IGNORECASE):
            if not header_set_this_part:
                header_prefix = ""

        # Prepend header if sentence starts lowercase
        if part[0].islower() and header_prefix:
            part = header_prefix + part

        # Protect abbreviations
        for orig, repl in ABBREVIATIONS:
            part = part.replace(orig, repl)

        # Normalize whitespace
        part = re.sub(r'\s+', ' ', part).strip()

        # Skip if too short
        if len(part) < 15:
            continue

        # Split multi-sentence entries
        sub_parts = re.split(r'(?<=\.)\s+(?=[A-Z])', part)
        for sp in sub_parts:
            sp = sp.strip()
            # Filter out any remaining header fragments
            if re.match(r'^Die Studierenden\s*[…\.]{0,3}\s*$', sp):
                header_prefix = "Die Studierenden "
                continue
            if re.search(r'sind\s+(die\s+)?(Studierenden|Teilnehmenden)\s+in\s+der\s+Lage\s*[:\.…]*\s*$', sp):
                continue
            if len(sp) < 15:
                continue
            sp = sp.replace('∅', '.')
            sentences.append(sp)

    return sentences


def main():
    materials_dir = Path(__file__).parent.parent / "materials" / "Modulhandbücher"
    output_csv = Path(__file__).parent.parent / "data" / "qualifikationsziele.csv"
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(materials_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    total_modules = 0
    total_sentences = 0
    rows = []

    for pdf_path in pdf_files:
        studiengang = parse_studiengang(pdf_path.name)
        print(f"\n--- {studiengang} ({pdf_path.name}) ---")

        module_count = 0
        for modul_id, modulname, quali_text in extract_modules_page_based(pdf_path):
            sentences = clean_quali_text(quali_text)
            if not sentences:
                continue

            module_count += 1
            for j, satz in enumerate(sentences, 1):
                rows.append({
                    'studiengang': studiengang,
                    'modul_id': modul_id,
                    'modulname': modulname,
                    'satz_nr': j,
                    'satz': satz,
                })
                total_sentences += 1

            print(f"  {modul_id} {modulname}: {len(sentences)} Sätze")

        total_modules += module_count
        print(f"  → {module_count} Module extrahiert")

    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['studiengang', 'modul_id', 'modulname', 'satz_nr', 'satz'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'='*60}")
    print(f"GESAMT: {total_modules} Module, {total_sentences} Sätze")
    print(f"Output: {output_csv}")

    # Quality check
    print(f"\n--- Stichprobe (erste 15 Sätze) ---")
    for r in rows[:15]:
        print(f"  [{r['modul_id']} {r['modulname'][:30]}] {r['satz'][:100]}")


if __name__ == "__main__":
    main()
