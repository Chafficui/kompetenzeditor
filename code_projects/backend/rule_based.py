"""
Regelbasierte Analyse: Verblistenabgleich und Cascading-Entscheidung.
"""

import json
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


@dataclass
class VerbResult:
    lemma: str
    stufen: list[int]
    kategorie: str  # "empfohlen", "nicht_empfohlen", "modal", "mehrdeutig", "unbekannt"


@dataclass
class RuleResult:
    typ: str  # K, I, S
    taxonomie: int | None
    konfidenz: float
    quelle: str  # "regel"
    verben: list[VerbResult]


class RuleBasedAnalyzer:
    def __init__(self):
        with open(DATA_DIR / "verbliste.json", encoding="utf-8") as f:
            data = json.load(f)

        # Eindeutige Zuordnung: verb → [stufen]
        self.verb_to_stufen: dict[str, list[int]] = {}
        for stufe_str, verben in data["empfohlen"].items():
            stufe = int(stufe_str)
            for verb in verben:
                if verb not in self.verb_to_stufen:
                    self.verb_to_stufen[verb] = []
                self.verb_to_stufen[verb].append(stufe)

        # Mehrdeutige Verben (explizit)
        for verb, stufen in data.get("mehrdeutig", {}).items():
            self.verb_to_stufen[verb] = stufen

        self.nicht_empfohlen: set[str] = set(data.get("nicht_empfohlen", []))
        self.modal: set[str] = set(data.get("modal", []))

    def check_verb(self, lemma: str) -> VerbResult:
        """Prüft ein einzelnes Verb-Lemma gegen die Listen."""
        lemma_lower = lemma.lower()

        if lemma_lower in self.modal:
            return VerbResult(lemma=lemma, stufen=[], kategorie="modal")

        if lemma_lower in self.nicht_empfohlen:
            return VerbResult(lemma=lemma, stufen=[], kategorie="nicht_empfohlen")

        if lemma_lower in self.verb_to_stufen:
            stufen = self.verb_to_stufen[lemma_lower]
            if len(stufen) == 1:
                return VerbResult(lemma=lemma, stufen=stufen, kategorie="empfohlen")
            else:
                return VerbResult(lemma=lemma, stufen=stufen, kategorie="mehrdeutig")

        return VerbResult(lemma=lemma, stufen=[], kategorie="unbekannt")

    def classify(self, verb_results: list[VerbResult], has_subject: bool) -> RuleResult | None:
        """
        Versucht regelbasierte Klassifikation.
        Gibt None zurück, wenn Embedding-Fallback nötig ist.
        """
        if not verb_results:
            # Kein Verb gefunden → wahrscheinlich kein Kompetenzsatz
            return RuleResult(typ="S", taxonomie=None, konfidenz=0.7, quelle="regel", verben=verb_results)

        # Sammle eindeutige empfohlene Verben
        eindeutige = [v for v in verb_results if v.kategorie == "empfohlen"]
        nicht_empf = [v for v in verb_results if v.kategorie == "nicht_empfohlen"]
        mehrdeutige = [v for v in verb_results if v.kategorie == "mehrdeutig"]
        unbekannte = [v for v in verb_results if v.kategorie == "unbekannt"]

        # Fall 1: Mindestens ein eindeutig empfohlenes Verb → Regel reicht
        if eindeutige:
            # Höchste Stufe wählen (bei mehreren Verben)
            max_stufe = max(v.stufen[0] for v in eindeutige)
            return RuleResult(
                typ="K",
                taxonomie=max_stufe,
                konfidenz=0.95,
                quelle="regel",
                verben=verb_results,
            )

        # Fall 2: Nur nicht-empfohlene Verben → Kompetenz, aber schlecht formuliert
        if nicht_empf and not mehrdeutige and not unbekannte:
            return RuleResult(
                typ="K",
                taxonomie=None,  # Kann nicht zugeordnet werden
                konfidenz=0.8,
                quelle="regel",
                verben=verb_results,
            )

        # Fall 3: Mehrdeutige oder unbekannte Verben → Embedding-Fallback
        # Gibt None zurück → Pipeline fällt auf Embedding zurück
        return None
