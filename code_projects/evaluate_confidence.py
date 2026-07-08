"""
Evaluation: Klassifikationsleistung aufgeschluesselt nach Konfidenz-Bins.

Zeigt, wie sich Precision/Recall/F1 fuer Typ- und Taxonomie-Klassifikation
verhalten, wenn man die Vorhersagen nach der SVM-Konfidenz gruppiert.

Ausgabe im LaTeX-tabellenfreundlichen Format.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score

sys.path.insert(0, str(Path(__file__).parent / "backend"))
from embedding_service import EmbeddingService

DATA_DIR = Path(__file__).parent.parent / "data"

# Konfidenz-Bins: (Name, Untergrenze inkl., Obergrenze exkl.)
CONFIDENCE_BINS = [
    ("niedrig",  0.0, 0.5),
    ("mittel",   0.5, 0.8),
    ("hoch",     0.8, 1.01),  # 1.01 damit 1.0 eingeschlossen ist
]


def primary_taxonomy(val):
    """Extrahiert die primaere Taxonomiestufe (vor dem ersten Semikolon)."""
    if not val or not val.strip():
        return ""
    return val.strip().split(";")[0].strip()


def load_test_set():
    """Laedt den Testdatensatz aus goldstandard.csv."""
    rows = []
    with open(DATA_DIR / "goldstandard.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["split"] == "test":
                r["taxonomie_primary"] = primary_taxonomy(r.get("taxonomie", ""))
                rows.append(r)
    return rows


def assign_bin(confidence):
    """Ordnet einen Konfidenzwert einem Bin zu."""
    for name, low, high in CONFIDENCE_BINS:
        if low <= confidence < high:
            return name
    return "hoch"  # Fallback fuer exakt 1.0


def evaluate_by_confidence(test_rows, emb_service):
    """
    Fuehrt Typ- und Taxonomie-Klassifikation durch und gruppiert
    die Ergebnisse nach Konfidenz-Bins.

    Gibt zurueck:
        typ_by_bin: dict[bin_name] -> {"y_true": [...], "y_pred": [...], "confidences": [...]}
        tax_by_bin: dict[bin_name] -> {"y_true": [...], "y_pred": [...], "confidences": [...]}
    """
    sentences = [r["satz"] for r in test_rows]
    embeddings = emb_service.encode(sentences)

    typ_by_bin = defaultdict(lambda: {"y_true": [], "y_pred": [], "confidences": []})
    tax_by_bin = defaultdict(lambda: {"y_true": [], "y_pred": [], "confidences": []})

    for i, r in enumerate(test_rows):
        # Typ-Klassifikation
        pred_typ, conf_typ = emb_service.classify_type(embeddings[i])
        bin_typ = assign_bin(conf_typ)
        typ_by_bin[bin_typ]["y_true"].append(r["typ"])
        typ_by_bin[bin_typ]["y_pred"].append(pred_typ)
        typ_by_bin[bin_typ]["confidences"].append(conf_typ)

        # Taxonomie-Klassifikation (nur fuer tatsaechliche K-Saetze mit Annotation)
        if r["typ"] == "K" and r["taxonomie_primary"]:
            pred_tax, conf_tax = emb_service.classify_taxonomy(embeddings[i])
            bin_tax = assign_bin(conf_tax)
            tax_by_bin[bin_tax]["y_true"].append(r["taxonomie_primary"])
            tax_by_bin[bin_tax]["y_pred"].append(str(pred_tax))
            tax_by_bin[bin_tax]["confidences"].append(conf_tax)

    return typ_by_bin, tax_by_bin


def compute_bin_metrics(bin_data, average="weighted"):
    """Berechnet Metriken fuer ein einzelnes Konfidenz-Bin."""
    y_true = bin_data["y_true"]
    y_pred = bin_data["y_pred"]
    n = len(y_true)

    if n == 0:
        return {"n": 0, "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "mean_conf": 0.0}

    return {
        "n": n,
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average=average, zero_division=0),
        "recall": recall_score(y_true, y_pred, average=average, zero_division=0),
        "f1": f1_score(y_true, y_pred, average=average, zero_division=0),
        "mean_conf": float(np.mean(bin_data["confidences"])),
    }


def print_divider(char="=", width=80):
    print(char * width)


def print_table(title, bin_names, metrics_list):
    """Druckt eine Ergebnis-Tabelle im Klartext."""
    print(f"\n  {title}")
    print_divider("-")
    header = f"  {'Bin':<12} {'n':>6} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Mean Conf':>10}"
    print(header)
    print_divider("-")

    for name, m in zip(bin_names, metrics_list):
        if m["n"] == 0:
            print(f"  {name:<12} {m['n']:>6}       ---        ---        ---        ---")
        else:
            print(f"  {name:<12} {m['n']:>6} {m['accuracy']:>10.3f} {m['precision']:>10.3f} {m['recall']:>10.3f} {m['f1']:>10.3f} {m['mean_conf']:>10.3f}")

    print_divider("-")


def print_latex_table(title, bin_names, metrics_list, label):
    """Druckt eine LaTeX-Tabelle zum Kopieren."""
    print(f"\n% --- {title} ---")
    print(r"\begin{table}[htbp]")
    print(r"  \centering")
    print(f"  \\caption{{{title}}}")
    print(f"  \\label{{tab:{label}}}")
    print(r"  \begin{tabular}{l r r r r r}")
    print(r"    \toprule")
    print(r"    Konfidenz-Bin & $n$ & Accuracy & Precision & Recall & F1 \\")
    print(r"    \midrule")

    for name, m in zip(bin_names, metrics_list):
        if m["n"] == 0:
            print(f"    {name} & {m['n']} & --- & --- & --- & --- \\\\")
        else:
            print(f"    {name} & {m['n']} & {m['accuracy']:.3f} & {m['precision']:.3f} & {m['recall']:.3f} & {m['f1']:.3f} \\\\")

    print(r"    \bottomrule")
    print(r"  \end{tabular}")
    print(r"\end{table}")


def print_high_confidence_analysis(typ_by_bin, tax_by_bin):
    """Analyse: Was passiert, wenn nur hoch-konfidente Vorhersagen vertraut werden?"""
    print_divider("=")
    print("  ANALYSE: Nur hoch-konfidente Vorhersagen (Konfidenz > 0.8)")
    print_divider("=")

    # Typ
    high_typ = typ_by_bin.get("hoch", {"y_true": [], "y_pred": []})
    all_n_typ = sum(len(typ_by_bin[b]["y_true"]) for b in typ_by_bin)
    high_n_typ = len(high_typ["y_true"])

    print(f"\n  Typ-Klassifikation:")
    print(f"    Gesamtanzahl Saetze:      {all_n_typ}")
    print(f"    Davon hoch-konfident:     {high_n_typ} ({100*high_n_typ/all_n_typ:.1f}%)" if all_n_typ else "")

    if high_n_typ > 0:
        acc = accuracy_score(high_typ["y_true"], high_typ["y_pred"])
        f1 = f1_score(high_typ["y_true"], high_typ["y_pred"], average="weighted", zero_division=0)
        print(f"    Accuracy (hoch-konfident): {acc:.3f}")
        print(f"    F1 (hoch-konfident):       {f1:.3f}")

        # Vergleich mit Gesamtergebnis
        all_true = []
        all_pred = []
        for b in typ_by_bin:
            all_true.extend(typ_by_bin[b]["y_true"])
            all_pred.extend(typ_by_bin[b]["y_pred"])
        all_f1 = f1_score(all_true, all_pred, average="weighted", zero_division=0)
        print(f"    F1 (alle Saetze):          {all_f1:.3f}")
        print(f"    Differenz:                 +{f1 - all_f1:.3f}" if f1 >= all_f1 else f"    Differenz:                 {f1 - all_f1:.3f}")

    # Taxonomie
    high_tax = tax_by_bin.get("hoch", {"y_true": [], "y_pred": []})
    all_n_tax = sum(len(tax_by_bin[b]["y_true"]) for b in tax_by_bin)
    high_n_tax = len(high_tax["y_true"])

    print(f"\n  Taxonomie-Zuordnung (nur K-Saetze):")
    print(f"    Gesamtanzahl K-Saetze:    {all_n_tax}")
    print(f"    Davon hoch-konfident:     {high_n_tax} ({100*high_n_tax/all_n_tax:.1f}%)" if all_n_tax else "")

    if high_n_tax > 0:
        acc = accuracy_score(high_tax["y_true"], high_tax["y_pred"])
        f1 = f1_score(high_tax["y_true"], high_tax["y_pred"], average="weighted", zero_division=0)
        print(f"    Accuracy (hoch-konfident): {acc:.3f}")
        print(f"    F1 (hoch-konfident):       {f1:.3f}")

        all_true = []
        all_pred = []
        for b in tax_by_bin:
            all_true.extend(tax_by_bin[b]["y_true"])
            all_pred.extend(tax_by_bin[b]["y_pred"])
        all_f1 = f1_score(all_true, all_pred, average="weighted", zero_division=0)
        print(f"    F1 (alle K-Saetze):        {all_f1:.3f}")
        print(f"    Differenz:                 +{f1 - all_f1:.3f}" if f1 >= all_f1 else f"    Differenz:                 {f1 - all_f1:.3f}")


def print_threshold_sweep(typ_by_bin, tax_by_bin):
    """Zeigt Coverage vs. F1 fuer verschiedene Konfidenz-Schwellenwerte."""
    print(f"\n")
    print_divider("=")
    print("  SCHWELLENWERT-ANALYSE: Coverage vs. F1")
    print_divider("=")

    # Sammle alle Daten
    all_typ_true, all_typ_pred, all_typ_conf = [], [], []
    for b in typ_by_bin:
        all_typ_true.extend(typ_by_bin[b]["y_true"])
        all_typ_pred.extend(typ_by_bin[b]["y_pred"])
        all_typ_conf.extend(typ_by_bin[b]["confidences"])

    all_tax_true, all_tax_pred, all_tax_conf = [], [], []
    for b in tax_by_bin:
        all_tax_true.extend(tax_by_bin[b]["y_true"])
        all_tax_pred.extend(tax_by_bin[b]["y_pred"])
        all_tax_conf.extend(tax_by_bin[b]["confidences"])

    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    print(f"\n  {'Schwelle':>10} | {'n_Typ':>6} {'Cov%':>6} {'F1_Typ':>8} | {'n_Tax':>6} {'Cov%':>6} {'F1_Tax':>8}")
    print(f"  {'-'*68}")

    for threshold in thresholds:
        # Typ
        mask_typ = [c >= threshold for c in all_typ_conf]
        sel_true_typ = [t for t, m in zip(all_typ_true, mask_typ) if m]
        sel_pred_typ = [p for p, m in zip(all_typ_pred, mask_typ) if m]
        n_typ = len(sel_true_typ)
        cov_typ = 100 * n_typ / len(all_typ_true) if all_typ_true else 0

        if n_typ > 0:
            f1_typ = f1_score(sel_true_typ, sel_pred_typ, average="weighted", zero_division=0)
        else:
            f1_typ = 0.0

        # Taxonomie
        mask_tax = [c >= threshold for c in all_tax_conf]
        sel_true_tax = [t for t, m in zip(all_tax_true, mask_tax) if m]
        sel_pred_tax = [p for p, m in zip(all_tax_pred, mask_tax) if m]
        n_tax = len(sel_true_tax)
        cov_tax = 100 * n_tax / len(all_tax_true) if all_tax_true else 0

        if n_tax > 0:
            f1_tax = f1_score(sel_true_tax, sel_pred_tax, average="weighted", zero_division=0)
        else:
            f1_tax = 0.0

        print(f"  {threshold:>10.1f} | {n_typ:>6} {cov_typ:>5.1f}% {f1_typ:>8.3f} | {n_tax:>6} {cov_tax:>5.1f}% {f1_tax:>8.3f}")

    # LaTeX-Tabelle fuer Schwellenwert-Analyse
    print(f"\n% --- Schwellenwert-Analyse (LaTeX) ---")
    print(r"\begin{table}[htbp]")
    print(r"  \centering")
    print(r"  \caption{Coverage und F1-Score bei verschiedenen Konfidenz-Schwellenwerten}")
    print(r"  \label{tab:konfidenz-schwellenwert}")
    print(r"  \begin{tabular}{r r r r r r r}")
    print(r"    \toprule")
    print(r"    Schwelle & $n_\text{Typ}$ & Cov.\% & F1\textsubscript{Typ} & $n_\text{Tax}$ & Cov.\% & F1\textsubscript{Tax} \\")
    print(r"    \midrule")

    for threshold in thresholds:
        mask_typ = [c >= threshold for c in all_typ_conf]
        sel_true_typ = [t for t, m in zip(all_typ_true, mask_typ) if m]
        sel_pred_typ = [p for p, m in zip(all_typ_pred, mask_typ) if m]
        n_typ = len(sel_true_typ)
        cov_typ = 100 * n_typ / len(all_typ_true) if all_typ_true else 0
        f1_typ = f1_score(sel_true_typ, sel_pred_typ, average="weighted", zero_division=0) if n_typ else 0.0

        mask_tax = [c >= threshold for c in all_tax_conf]
        sel_true_tax = [t for t, m in zip(all_tax_true, mask_tax) if m]
        sel_pred_tax = [p for p, m in zip(all_tax_pred, mask_tax) if m]
        n_tax = len(sel_true_tax)
        cov_tax = 100 * n_tax / len(all_tax_true) if all_tax_true else 0
        f1_tax = f1_score(sel_true_tax, sel_pred_tax, average="weighted", zero_division=0) if n_tax else 0.0

        print(f"    {threshold:.1f} & {n_typ} & {cov_typ:.1f} & {f1_typ:.3f} & {n_tax} & {cov_tax:.1f} & {f1_tax:.3f} \\\\")

    print(r"    \bottomrule")
    print(r"  \end{tabular}")
    print(r"\end{table}")


def main():
    print("Lade Embedding-Service...")
    emb_service = EmbeddingService()
    emb_service.load()

    print("Lade Testdatensatz...")
    test_rows = load_test_set()
    n_total = len(test_rows)
    n_k = sum(1 for r in test_rows if r["typ"] == "K")
    n_k_annotated = sum(1 for r in test_rows if r["typ"] == "K" and primary_taxonomy(r.get("taxonomie", "")))
    print(f"  Gesamt: {n_total} Saetze, davon {n_k} Typ K, {n_k_annotated} mit Taxonomie-Annotation")

    print("\nKlassifiziere und gruppiere nach Konfidenz...")
    typ_by_bin, tax_by_bin = evaluate_by_confidence(test_rows, emb_service)

    # --- Ergebnisse ausgeben ---
    bin_names = [name for name, _, _ in CONFIDENCE_BINS]

    # Typ-Klassifikation
    print_divider("=")
    print("  KONFIDENZ-ANALYSE: Embedding-Ansatz (SBERT + SVM)")
    print_divider("=")

    typ_metrics = [compute_bin_metrics(typ_by_bin.get(name, {"y_true": [], "y_pred": [], "confidences": []}))
                   for name in bin_names]
    print_table("Typ-Klassifikation (K/I/S) nach Konfidenz-Bin", bin_names, typ_metrics)

    # Gesamt-Metriken Typ
    all_true_typ = []
    all_pred_typ = []
    for b in typ_by_bin:
        all_true_typ.extend(typ_by_bin[b]["y_true"])
        all_pred_typ.extend(typ_by_bin[b]["y_pred"])
    total_typ_metrics = {
        "n": len(all_true_typ),
        "accuracy": accuracy_score(all_true_typ, all_pred_typ),
        "precision": precision_score(all_true_typ, all_pred_typ, average="weighted", zero_division=0),
        "recall": recall_score(all_true_typ, all_pred_typ, average="weighted", zero_division=0),
        "f1": f1_score(all_true_typ, all_pred_typ, average="weighted", zero_division=0),
        "mean_conf": 0.0,
    }
    print(f"  {'GESAMT':<12} {total_typ_metrics['n']:>6} {total_typ_metrics['accuracy']:>10.3f} {total_typ_metrics['precision']:>10.3f} {total_typ_metrics['recall']:>10.3f} {total_typ_metrics['f1']:>10.3f}")
    print_divider("-")

    # Taxonomie-Klassifikation
    tax_metrics = [compute_bin_metrics(tax_by_bin.get(name, {"y_true": [], "y_pred": [], "confidences": []}))
                   for name in bin_names]
    print_table("Taxonomie-Zuordnung (nur K-Saetze) nach Konfidenz-Bin", bin_names, tax_metrics)

    # Gesamt-Metriken Taxonomie
    all_true_tax = []
    all_pred_tax = []
    for b in tax_by_bin:
        all_true_tax.extend(tax_by_bin[b]["y_true"])
        all_pred_tax.extend(tax_by_bin[b]["y_pred"])
    if all_true_tax:
        total_tax_metrics = {
            "n": len(all_true_tax),
            "accuracy": accuracy_score(all_true_tax, all_pred_tax),
            "precision": precision_score(all_true_tax, all_pred_tax, average="weighted", zero_division=0),
            "recall": recall_score(all_true_tax, all_pred_tax, average="weighted", zero_division=0),
            "f1": f1_score(all_true_tax, all_pred_tax, average="weighted", zero_division=0),
            "mean_conf": 0.0,
        }
        print(f"  {'GESAMT':<12} {total_tax_metrics['n']:>6} {total_tax_metrics['accuracy']:>10.3f} {total_tax_metrics['precision']:>10.3f} {total_tax_metrics['recall']:>10.3f} {total_tax_metrics['f1']:>10.3f}")
        print_divider("-")

    # Hoch-Konfidenz-Analyse
    print_high_confidence_analysis(typ_by_bin, tax_by_bin)

    # Schwellenwert-Analyse
    print_threshold_sweep(typ_by_bin, tax_by_bin)

    # LaTeX-Tabellen
    print(f"\n")
    print_divider("=")
    print("  LATEX-TABELLEN (zum Kopieren)")
    print_divider("=")

    print_latex_table(
        "Typ-Klassifikation nach Konfidenz-Bin",
        bin_names + ["Gesamt"],
        typ_metrics + [total_typ_metrics],
        "konfidenz-typ",
    )
    if all_true_tax:
        print_latex_table(
            "Taxonomie-Zuordnung nach Konfidenz-Bin (nur K-S\\\"atze)",
            bin_names + ["Gesamt"],
            tax_metrics + [total_tax_metrics],
            "konfidenz-taxonomie",
        )

    print(f"\nFertig.")


if __name__ == "__main__":
    main()
