"""
Hybrid-Cascading-Pipeline: 6-Schritte-Analyse von Kompetenzformulierungen.

1. Satz-Segmentierung
2. spaCy POS-Tagging → Verben extrahieren
3. Regelbasierte Klassifikation (Verbliste)
4. Embedding-Klassifikation (SBERT + SVM) — nur bei Bedarf
5. Ähnlichkeitssuche (Cosine Top-k)
6. Set-Analyse (Taxonomie-Verteilung)
"""

import re
from dataclasses import dataclass, field

import numpy as np
import spacy

from embedding_service import EmbeddingService
from rule_based import RuleBasedAnalyzer, VerbResult
from similarity import SimilaritySearch


@dataclass
class VerbInfo:
    verb: str
    lemma: str
    kategorie: str
    stufen: list[int] = field(default_factory=list)


@dataclass
class SentenceResult:
    text: str
    typ: str
    taxonomie: int | None
    taxonomie_stufen: list[int] = field(default_factory=list)
    konfidenz: float = 0.0
    quelle: str = "regel"  # "regel" oder "embedding"
    verben: list[VerbInfo] = field(default_factory=list)
    aehnliche: list[dict] = field(default_factory=list)
    warnungen: list[str] = field(default_factory=list)


@dataclass
class SetAnalyse:
    verteilung: dict[str, int]
    abdeckung: int
    empfehlung: str


@dataclass
class AnalyzeResponse:
    sentences: list[SentenceResult]
    set_analyse: SetAnalyse | None = None


# Abkürzungen, die kein Satzende markieren
ABBREVIATIONS = {"bzw", "z.B", "u.a", "d.h", "o.ä", "etc", "ca", "vgl", "ggf", "evtl", "Dr", "Prof", "Nr"}


class AnalysisPipeline:
    def __init__(self):
        self.nlp = None
        self.rule_analyzer = RuleBasedAnalyzer()
        self.embedding_service = EmbeddingService()
        self.similarity_search = SimilaritySearch()

    def load(self):
        """Lädt alle Modelle."""
        print("Lade Modelle...")
        print("  Lade spaCy de_core_news_lg...")
        self.nlp = spacy.load("de_core_news_lg")
        self.embedding_service.load()
        self.similarity_search.load()
        print("Pipeline bereit.")

    def segment_sentences(self, text: str) -> list[str]:
        """Segmentiert Text in Sätze (einfache Regex-basierte Segmentierung)."""
        # Nutze spaCy für robuste Satzsegmentierung
        doc = self.nlp(text)
        sentences = []
        for sent in doc.sents:
            s = sent.text.strip()
            if s:
                sentences.append(s)
        return sentences if sentences else [text.strip()]

    def extract_verbs(self, sentence: str) -> tuple[list[dict], bool]:
        """
        Extrahiert Verben und prüft auf Subjekt "Studierende".
        Returns: (verb_infos, has_studierende_subject)
        """
        doc = self.nlp(sentence)
        verbs = []
        has_subject = False

        for token in doc:
            # Subjekt-Check
            if token.dep_ in ("sb", "nk") and "studierend" in token.lemma_.lower():
                has_subject = True

            # Verben extrahieren (VERB und AUX)
            if token.pos_ in ("VERB", "AUX"):
                verbs.append({
                    "text": token.text,
                    "lemma": token.lemma_.lower(),
                    "pos": token.pos_,
                    "dep": token.dep_,
                })

        return verbs, has_subject

    def analyze(self, text: str) -> AnalyzeResponse:
        """Führt die vollständige 6-Schritte-Analyse durch."""
        # Schritt 1: Segmentierung
        sentences = self.segment_sentences(text)

        # Embeddings für alle Sätze auf einmal berechnen (effizienter)
        all_embeddings = self.embedding_service.encode(sentences)

        results: list[SentenceResult] = []

        for i, sentence in enumerate(sentences):
            embedding = all_embeddings[i]
            result = self._analyze_sentence(sentence, embedding)
            results.append(result)

        # Schritt 6: Set-Analyse
        set_analyse = self._compute_set_analyse(results)

        return AnalyzeResponse(sentences=results, set_analyse=set_analyse)

    def _analyze_sentence(self, sentence: str, embedding: np.ndarray) -> SentenceResult:
        """Analysiert einen einzelnen Satz (Schritte 2-5)."""
        # Schritt 2: Verben extrahieren
        spacy_verbs, has_subject = self.extract_verbs(sentence)

        # Schritt 3: Regelbasierte Klassifikation
        verb_results: list[VerbResult] = []
        verb_infos: list[VerbInfo] = []

        for v in spacy_verbs:
            vr = self.rule_analyzer.check_verb(v["lemma"])
            verb_results.append(vr)
            verb_infos.append(VerbInfo(
                verb=v["text"],
                lemma=v["lemma"],
                kategorie=vr.kategorie,
                stufen=vr.stufen,
            ))

        rule_result = self.rule_analyzer.classify(verb_results, has_subject)

        # Warnungen sammeln
        warnungen = []
        for vi in verb_infos:
            if vi.kategorie == "nicht_empfohlen":
                warnungen.append(f"Verb '{vi.verb}' ist nicht empfohlen (zu unspezifisch).")
            elif vi.kategorie == "modal":
                warnungen.append(f"Modalverb '{vi.verb}' erkannt — Reformulierung empfohlen.")

        # Alle Stufen aus den Verben sammeln
        alle_stufen = []
        for vi in verb_infos:
            if vi.stufen:
                alle_stufen.extend(vi.stufen)

        # Schritt 4: Embedding-Fallback (wenn Regel nicht ausreicht)
        if rule_result is not None:
            typ = rule_result.typ
            taxonomie = rule_result.taxonomie
            konfidenz = rule_result.konfidenz
            quelle = "regel"
        else:
            # Embedding-basierte Klassifikation
            typ, typ_conf = self.embedding_service.classify_type(embedding)
            if typ == "K":
                taxonomie, tax_conf = self.embedding_service.classify_taxonomy(embedding)
                konfidenz = min(typ_conf, tax_conf)
                if not alle_stufen:
                    alle_stufen = [taxonomie]
            else:
                taxonomie = None
                konfidenz = typ_conf
            quelle = "embedding"

        # Deduplizieren und sortieren
        taxonomie_stufen = sorted(set(alle_stufen))

        # Primäre Stufe: höchste aus den gefundenen (falls vorhanden)
        if taxonomie is None and taxonomie_stufen:
            taxonomie = max(taxonomie_stufen)

        # Schritt 5: Ähnlichkeitssuche
        similar = self.similarity_search.find_similar(
            query_embedding=embedding,
            top_k=5,
            filter_typ="K",
            exclude_text=sentence,
        )
        aehnliche = [
            {
                "satz": s.satz,
                "similarity": round(s.similarity, 3),
                "taxonomie": s.taxonomie,
                "modulname": s.modulname,
            }
            for s in similar
        ]

        return SentenceResult(
            text=sentence,
            typ=typ,
            taxonomie=taxonomie,
            taxonomie_stufen=taxonomie_stufen,
            konfidenz=round(konfidenz, 3),
            quelle=quelle,
            verben=verb_infos,
            aehnliche=aehnliche,
            warnungen=warnungen,
        )

    def _compute_set_analyse(self, results: list[SentenceResult]) -> SetAnalyse | None:
        """Berechnet die Taxonomie-Verteilung über alle Sätze."""
        kompetenz_saetze = [r for r in results if r.typ == "K" and r.taxonomie_stufen]
        if not kompetenz_saetze:
            return None

        verteilung = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0}
        for r in kompetenz_saetze:
            for stufe in r.taxonomie_stufen:
                verteilung[str(stufe)] += 1

        abdeckung = sum(1 for v in verteilung.values() if v > 0)

        fehlende = [k for k, v in verteilung.items() if v == 0]
        stufen_namen = {"1": "Erinnern", "2": "Verstehen", "3": "Anwenden",
                        "4": "Analysieren", "5": "Bewerten", "6": "Erschaffen"}
        if fehlende:
            fehlende_namen = [f"{k} ({stufen_namen[k]})" for k in fehlende]
            empfehlung = f"Fehlende Stufen: {', '.join(fehlende_namen)}. " \
                         f"Erwägen Sie Formulierungen auf diesen kognitiven Niveaus."
        else:
            empfehlung = "Alle sechs Taxonomiestufen sind abgedeckt."

        return SetAnalyse(verteilung=verteilung, abdeckung=abdeckung, empfehlung=empfehlung)
