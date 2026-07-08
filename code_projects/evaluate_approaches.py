"""
Evaluation: Vergleich der drei Ansätze (regelbasiert, embedding, hybrid)
auf dem Gold-Standard-Datensatz (5617 Sätze, 4 Hochschulen).

Berechnet:
- Typ-Klassifikation: F1 (gewichtet) für K/I/S
- Taxonomie-Zuordnung: F1 (gewichtet) für Stufen 1-6 (Primärstufe)
- Aufschlüsselung nach Schwierigkeitskategorie
- Aufschlüsselung nach Hochschule
- Precision@k für Empfehlungssystem
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import spacy
from scipy.stats import chi2
from sklearn.metrics import classification_report, confusion_matrix, f1_score

sys.path.insert(0, str(Path(__file__).parent / "backend"))
from rule_based import RuleBasedAnalyzer
from embedding_service import EmbeddingService
from similarity import SimilaritySearch

DATA_DIR = Path(__file__).parent.parent / "data"
BACKEND_DIR = Path(__file__).parent / "backend"
RESULTS_DIR = Path(__file__).parent.parent / "evaluation_results"
RESULTS_DIR.mkdir(exist_ok=True)


def primary_taxonomy(val):
    if not val or not val.strip():
        return ""
    return val.strip().split(";")[0].strip()


def load_dataset():
    rows = []
    with open(DATA_DIR / "goldstandard.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["taxonomie_primary"] = primary_taxonomy(r.get("taxonomie", ""))
            rows.append(r)
    train = [r for r in rows if r["split"] == "train"]
    test = [r for r in rows if r["split"] == "test"]
    return train, test


def assign_difficulty(rows, nlp, analyzer):
    for r in rows:
        if r["typ"] != "K":
            r["schwierigkeit"] = "nicht-K"
            continue
        doc = nlp(r["satz"])
        lemmata = [t.lemma_.lower() for t in doc if t.pos_ in ("VERB", "AUX")]

        has_listed = False
        has_bad = False
        for lemma in lemmata:
            vr = analyzer.check_verb(lemma)
            if vr.kategorie in ("empfohlen", "mehrdeutig"):
                has_listed = True
            elif vr.kategorie == "nicht_empfohlen":
                has_bad = True

        if has_listed:
            r["schwierigkeit"] = "standard"
        elif has_bad:
            r["schwierigkeit"] = "nicht-empfohlen"
        else:
            r["schwierigkeit"] = "unbekannt"


def evaluate_rule_based(test_rows, nlp, analyzer):
    y_true_typ, y_pred_typ = [], []
    y_true_tax, y_pred_tax = [], []

    for r in test_rows:
        doc = nlp(r["satz"])
        verbs = []
        has_subject = False

        for token in doc:
            if token.dep_ in ("sb", "nk") and "studierend" in token.lemma_.lower():
                has_subject = True
            if token.pos_ in ("VERB", "AUX"):
                vr = analyzer.check_verb(token.lemma_.lower())
                verbs.append(vr)

        rule_result = analyzer.classify(verbs, has_subject)

        if rule_result is not None:
            pred_typ = rule_result.typ
            pred_tax = rule_result.taxonomie
        else:
            pred_typ = "K" if has_subject else "S"
            pred_tax = None

        y_true_typ.append(r["typ"])
        y_pred_typ.append(pred_typ)

        if r["typ"] == "K" and r["taxonomie_primary"]:
            y_true_tax.append(r["taxonomie_primary"])
            y_pred_tax.append(str(pred_tax) if pred_tax else "0")

    return y_true_typ, y_pred_typ, y_true_tax, y_pred_tax


def evaluate_embedding(test_rows, emb_service):
    sentences = [r["satz"] for r in test_rows]
    embeddings = emb_service.encode(sentences)

    y_true_typ, y_pred_typ = [], []
    y_true_tax, y_pred_tax = [], []

    for i, r in enumerate(test_rows):
        pred_typ, _ = emb_service.classify_type(embeddings[i])
        y_true_typ.append(r["typ"])
        y_pred_typ.append(pred_typ)

        if r["typ"] == "K" and r["taxonomie_primary"]:
            pred_tax, _ = emb_service.classify_taxonomy(embeddings[i])
            y_true_tax.append(r["taxonomie_primary"])
            y_pred_tax.append(str(pred_tax))

    return y_true_typ, y_pred_typ, y_true_tax, y_pred_tax


def evaluate_hybrid(test_rows, nlp, analyzer, emb_service):
    sentences = [r["satz"] for r in test_rows]
    embeddings = emb_service.encode(sentences)

    y_true_typ, y_pred_typ = [], []
    y_true_tax, y_pred_tax = [], []
    source_counts = Counter()

    for i, r in enumerate(test_rows):
        doc = nlp(r["satz"])
        verbs = []
        has_subject = False

        for token in doc:
            if token.dep_ in ("sb", "nk") and "studierend" in token.lemma_.lower():
                has_subject = True
            if token.pos_ in ("VERB", "AUX"):
                vr = analyzer.check_verb(token.lemma_.lower())
                verbs.append(vr)

        rule_result = analyzer.classify(verbs, has_subject)

        if rule_result is not None:
            pred_typ = rule_result.typ
            pred_tax = rule_result.taxonomie
            source_counts["regel"] += 1
        else:
            pred_typ, _ = emb_service.classify_type(embeddings[i])
            if pred_typ == "K":
                pred_tax, _ = emb_service.classify_taxonomy(embeddings[i])
            else:
                pred_tax = None
            source_counts["embedding"] += 1

        y_true_typ.append(r["typ"])
        y_pred_typ.append(pred_typ)

        if r["typ"] == "K" and r["taxonomie_primary"]:
            y_true_tax.append(r["taxonomie_primary"])
            y_pred_tax.append(str(pred_tax) if pred_tax else "0")

    return y_true_typ, y_pred_typ, y_true_tax, y_pred_tax, source_counts


def evaluate_precision_at_k(test_rows, emb_service, sim_search, k=5):
    k_sentences = [r for r in test_rows if r["typ"] == "K" and r["taxonomie_primary"]]
    sentences = [r["satz"] for r in k_sentences]
    embeddings = emb_service.encode(sentences)

    precision_sum = 0
    count = 0

    for i, r in enumerate(k_sentences):
        true_tax = r["taxonomie_primary"]
        similar = sim_search.find_similar(
            query_embedding=embeddings[i],
            top_k=k,
            filter_typ="K",
            exclude_text=r["satz"],
        )
        if similar:
            relevant = sum(1 for s in similar if primary_taxonomy(str(s.taxonomie)) == true_tax)
            precision_sum += relevant / len(similar)
            count += 1

    return precision_sum / count if count > 0 else 0


def format_report(name, y_true_typ, y_pred_typ, y_true_tax, y_pred_tax, test_rows=None):
    lines = [f"\n{'='*60}", f"  {name}", f"{'='*60}\n"]

    lines.append("--- Typ-Klassifikation (K/I/S) ---")
    lines.append(classification_report(y_true_typ, y_pred_typ, digits=3, zero_division=0))

    valid_tax = [(t, p) for t, p in zip(y_true_tax, y_pred_tax) if p != "0"]
    unclassified = sum(1 for p in y_pred_tax if p == "0")

    if valid_tax:
        vt_true, vt_pred = zip(*valid_tax)
        lines.append(f"--- Taxonomie-Zuordnung (Primärstufe, {len(valid_tax)} klassifiziert, {unclassified} nicht zuordenbar) ---")
        lines.append(classification_report(
            vt_true, vt_pred, labels=["1","2","3","4","5","6"],
            target_names=["Erinnern", "Verstehen", "Anwenden", "Analysieren", "Bewerten", "Erschaffen"],
            digits=3, zero_division=0
        ))

        lines.append("Confusion Matrix:")
        cm = confusion_matrix(vt_true, vt_pred, labels=["1","2","3","4","5","6"])
        lines.append("       1     2     3     4     5     6")
        for i, row in enumerate(cm):
            lines.append(f"  {i+1}: " + "  ".join(f"{v:4d}" for v in row))
    else:
        lines.append(f"--- Taxonomie: {unclassified} Sätze nicht zuordenbar ---")

    if test_rows:
        # Schwierigkeitskategorien
        lines.append("\n--- Aufschlüsselung nach Schwierigkeitskategorie ---")
        _append_stratified(lines, test_rows, y_true_typ, y_pred_typ, y_true_tax, y_pred_tax, "schwierigkeit",
                           ["standard", "unbekannt", "nicht-empfohlen", "nicht-K"])

        # Hochschulen
        lines.append("\n--- Aufschlüsselung nach Hochschule ---")
        hochschulen = sorted(set(r.get("hochschule", "") for r in test_rows))
        _append_stratified(lines, test_rows, y_true_typ, y_pred_typ, y_true_tax, y_pred_tax, "hochschule",
                           hochschulen)

    return "\n".join(lines)


def _append_stratified(lines, test_rows, y_true_typ, y_pred_typ, y_true_tax, y_pred_tax, key, categories):
    k_tax_map = {}
    k_idx = 0
    for i, r in enumerate(test_rows):
        if r["typ"] == "K" and r["taxonomie_primary"]:
            k_tax_map[i] = k_idx
            k_idx += 1

    for cat in categories:
        cat_indices = [i for i, r in enumerate(test_rows) if r.get(key) == cat]
        if not cat_indices:
            continue

        cat_true_typ = [y_true_typ[i] for i in cat_indices]
        cat_pred_typ = [y_pred_typ[i] for i in cat_indices]
        typ_correct = sum(1 for t, p in zip(cat_true_typ, cat_pred_typ) if t == p)
        typ_acc = typ_correct / len(cat_indices)

        # F1 für Typ
        typ_f1 = f1_score(cat_true_typ, cat_pred_typ, average="weighted", zero_division=0)

        # Taxonomie für K-Sätze in dieser Kategorie
        cat_tax_true, cat_tax_pred = [], []
        for i in cat_indices:
            if i in k_tax_map:
                tax_idx = k_tax_map[i]
                cat_tax_true.append(y_true_tax[tax_idx])
                cat_tax_pred.append(y_pred_tax[tax_idx])

        valid_pairs = [(t, p) for t, p in zip(cat_tax_true, cat_tax_pred) if p != "0"]
        if valid_pairs:
            vt, vp = zip(*valid_pairs)
            tax_f1 = f1_score(vt, vp, average="weighted", zero_division=0)
            lines.append(f"  {cat:30s}  n={len(cat_indices):4d}  Typ-F1={typ_f1:.3f}  Tax-F1={tax_f1:.3f} ({len(valid_pairs)}/{len(cat_tax_true)} klass.)")
        elif cat_tax_true:
            lines.append(f"  {cat:30s}  n={len(cat_indices):4d}  Typ-F1={typ_f1:.3f}  Tax: nicht zuordenbar")
        else:
            lines.append(f"  {cat:30s}  n={len(cat_indices):4d}  Typ-F1={typ_f1:.3f}")


def main():
    print("Lade Modelle...")
    nlp = spacy.load("de_core_news_lg")
    analyzer = RuleBasedAnalyzer()

    emb_service = EmbeddingService()
    emb_service.load()

    sim_search = SimilaritySearch()
    sim_search.load()

    print("Lade Datensatz...")
    train, test = load_dataset()
    print(f"  Train: {len(train)}, Test: {len(test)}")
    hs_counts = Counter(r.get("hochschule", "") for r in test)
    for hs, n in hs_counts.most_common():
        print(f"    {hs}: {n}")

    print("Weise Schwierigkeitskategorien zu...")
    assign_difficulty(test, nlp, analyzer)
    diff_counts = Counter(r["schwierigkeit"] for r in test)
    for k, v in diff_counts.most_common():
        print(f"  {k}: {v}")

    results_text = []

    # 1. Regelbasiert
    print("\n[1/3] Evaluiere regelbasierten Ansatz...")
    r_true_typ, r_pred_typ, r_true_tax, r_pred_tax = evaluate_rule_based(test, nlp, analyzer)
    results_text.append(format_report("Regelbasierter Ansatz", r_true_typ, r_pred_typ, r_true_tax, r_pred_tax, test))

    # 2. Embedding
    print("[2/3] Evaluiere Embedding-Ansatz...")
    e_true_typ, e_pred_typ, e_true_tax, e_pred_tax = evaluate_embedding(test, emb_service)
    results_text.append(format_report("Embedding-Ansatz (SBERT + SVM)", e_true_typ, e_pred_typ, e_true_tax, e_pred_tax, test))

    # 3. Hybrid
    print("[3/3] Evaluiere hybriden Ansatz...")
    h_true_typ, h_pred_typ, h_true_tax, h_pred_tax, source_counts = evaluate_hybrid(test, nlp, analyzer, emb_service)
    results_text.append(format_report("Hybrider Ansatz (Regel + Embedding)", h_true_typ, h_pred_typ, h_true_tax, h_pred_tax, test))
    results_text.append(f"\n  Quellen-Verteilung Hybrid: {dict(source_counts)}")

    # 4. Precision@k
    print("\nBerechne Precision@k...")
    for k in [1, 3, 5]:
        p_at_k = evaluate_precision_at_k(test, emb_service, sim_search, k=k)
        results_text.append(f"  Precision@{k} = {p_at_k:.3f}")

    # Zusammenfassungstabelle
    results_text.append(f"\n{'='*60}")
    results_text.append(f"  ZUSAMMENFASSUNG")
    results_text.append(f"{'='*60}")

    def _weighted_f1(y_true, y_pred, exclude_zero=False):
        if exclude_zero:
            pairs = [(t, p) for t, p in zip(y_true, y_pred) if p != "0"]
            if not pairs:
                return 0.0
            t, p = zip(*pairs)
            return f1_score(t, p, average="weighted", zero_division=0)
        return f1_score(y_true, y_pred, average="weighted", zero_division=0)

    results_text.append(f"\n{'Ansatz':<35} {'Typ-F1':>8} {'Tax-F1':>8}")
    results_text.append(f"{'-'*55}")
    results_text.append(f"{'Regelbasiert':<35} {_weighted_f1(r_true_typ, r_pred_typ):>8.3f} {_weighted_f1(r_true_tax, r_pred_tax, True):>8.3f}")
    results_text.append(f"{'Embedding (SBERT+SVM)':<35} {_weighted_f1(e_true_typ, e_pred_typ):>8.3f} {_weighted_f1(e_true_tax, e_pred_tax, True):>8.3f}")
    results_text.append(f"{'Hybrid (Regel+Embedding)':<35} {_weighted_f1(h_true_typ, h_pred_typ):>8.3f} {_weighted_f1(h_true_tax, h_pred_tax, True):>8.3f}")

    # 5. McNemar-Tests (paarweise Klassifikatorvergleiche)
    print("\nBerechne McNemar-Tests...")
    results_text.append(f"\n{'='*60}")
    results_text.append(f"  McNEMAR-TESTS (Bonferroni-korrigiert, α=0.05/6≈0.0083)")
    results_text.append(f"{'='*60}")

    def mcnemar_test(y_true, pred_a, pred_b):
        correct_a = [t == p for t, p in zip(y_true, pred_a)]
        correct_b = [t == p for t, p in zip(y_true, pred_b)]
        n01 = sum(1 for a, b in zip(correct_a, correct_b) if a and not b)
        n10 = sum(1 for a, b in zip(correct_a, correct_b) if not a and b)
        n00 = sum(1 for a, b in zip(correct_a, correct_b) if not a and not b)
        n11 = sum(1 for a, b in zip(correct_a, correct_b) if a and b)
        if n01 + n10 == 0:
            return {"n01": n01, "n10": n10, "n11": n11, "n00": n00,
                    "chi2": 0.0, "p": 1.0}
        if n01 + n10 < 25:
            from scipy.stats import binomtest
            result = binomtest(min(n01, n10), n01 + n10, 0.5)
            return {"n01": n01, "n10": n10, "n11": n11, "n00": n00,
                    "chi2": float("nan"), "p": result.pvalue}
        chi2_val = (abs(n01 - n10) - 1) ** 2 / (n01 + n10)
        p_val = 1 - chi2.cdf(chi2_val, df=1)
        return {"n01": n01, "n10": n10, "n11": n11, "n00": n00,
                "chi2": chi2_val, "p": p_val}

    # y_true_tax ist identisch für alle drei Ansätze (gleiche K-Sätze)
    comparisons = [
        ("Regel vs. Embedding", "Typ", r_true_typ, r_pred_typ, e_pred_typ),
        ("Regel vs. Embedding", "Taxonomie", r_true_tax, r_pred_tax, e_pred_tax),
        ("Regel vs. Hybrid", "Typ", r_true_typ, r_pred_typ, h_pred_typ),
        ("Regel vs. Hybrid", "Taxonomie", r_true_tax, r_pred_tax, h_pred_tax),
        ("Embedding vs. Hybrid", "Typ", e_true_typ, e_pred_typ, h_pred_typ),
        ("Embedding vs. Hybrid", "Taxonomie", e_true_tax, e_pred_tax, h_pred_tax),
    ]

    alpha_bonferroni = 0.05 / 6
    mcnemar_results = []

    for name, task, y_true, pred_a, pred_b in comparisons:
        result = mcnemar_test(y_true, pred_a, pred_b)
        p_val = result["p"]
        chi2_val = result["chi2"]
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < alpha_bonferroni else "n.s."
        results_text.append(
            f"  {name:25s} {task:10s}  "
            f"n01={result['n01']:4d}  n10={result['n10']:4d}  "
            f"χ²={chi2_val:8.2f}  p={p_val:.2e}  {sig}"
        )
        mcnemar_results.append({
            "vergleich": name, "dimension": task,
            "n": len(y_true), "n01": result["n01"], "n10": result["n10"],
            "n11": result["n11"], "n00": result["n00"],
            "chi2": chi2_val, "p": p_val, "signifikant": sig != "n.s.",
        })

    mcnemar_path = RESULTS_DIR / "mcnemar_results.json"
    with open(mcnemar_path, "w", encoding="utf-8") as f:
        json.dump(mcnemar_results, f, indent=2, ensure_ascii=False)

    # Vorhersagen pro Sample speichern
    predictions = []
    for i, r in enumerate(test):
        row = {
            "satz": r["satz"],
            "hochschule": r.get("hochschule", ""),
            "true_typ": r["typ"],
            "true_tax": r.get("taxonomie_primary", ""),
            "regel_typ": r_pred_typ[i],
            "embedding_typ": e_pred_typ[i],
            "hybrid_typ": h_pred_typ[i],
        }
        predictions.append(row)

    pred_path = RESULTS_DIR / "predictions_per_sample.csv"
    with open(pred_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=predictions[0].keys())
        writer.writeheader()
        writer.writerows(predictions)

    full_report = "\n".join(results_text)
    print(full_report)

    report_path = RESULTS_DIR / "evaluation_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(full_report)
    print(f"\nBericht gespeichert: {report_path}")
    print(f"McNemar-Ergebnisse: {mcnemar_path}")
    print(f"Vorhersagen: {pred_path}")


if __name__ == "__main__":
    main()
