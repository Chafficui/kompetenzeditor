/**
 * Composable für die hybride Analyse über das neue FastAPI-Backend.
 * Ersetzt die alte spaCy-Direktanbindung durch den /analyze-Endpoint,
 * der Regelbasiert + Embedding-Klassifikation + Ähnlichkeitssuche liefert.
 */
export function useAnalysis() {
  async function analyzeText(text) {
    const cleaned = text.replace(/(<([^>]+)>)/gi, '').trim()
    if (!cleaned) return null

    const result = await $fetch('/api/analyze', {
      method: 'POST',
      body: { text: cleaned },
    })

    return result
  }

  /**
   * Konvertiert das Backend-Ergebnis in das Format, das der Editor erwartet
   * (Highlights, Scores, Vorschläge).
   */
  function processAnalysisResult(result, text) {
    if (!result || !result.sentences) {
      return {
        sentences: [],
        highlights: [],
        goodVerbsCount: 0,
        badVerbsCount: 0,
        allTextGoodVerbs: [],
        allTextBadVerbs: [],
        neutralVerbs: [],
        noVerbsSents: [],
        modalVerbsOC: [],
        score: 0,
        badSentsScore: 0,
        noVerbsSentsScore: 0,
        setAnalyse: null,
        sentenceDetails: [],
      }
    }

    const sentences = result.sentences
    const highlights = []
    let goodVerbsCount = 0
    let badVerbsCount = 0
    const allTextGoodVerbs = []
    const allTextBadVerbs = []
    const neutralVerbs = []
    const noVerbsSents = []
    const modalVerbsOC = []

    // Taxonomie-Stufen-Namen für Tooltips
    const stufenNamen = { 1: 'Erinnern', 2: 'Verstehen', 3: 'Anwenden', 4: 'Analysieren', 5: 'Bewerten', 6: 'Erschaffen' }

    // Pro Satz: Verben auswerten und Highlights bauen
    for (const sent of sentences) {
      for (const verb of sent.verben) {
        const positions = findWordPositions(text, verb.verb)
        let highlightClass = 'verb-neutral'
        let title = ''

        if (verb.kategorie === 'empfohlen') {
          goodVerbsCount++
          if (!allTextGoodVerbs.includes(verb.lemma)) allTextGoodVerbs.push(verb.lemma)
          if (verb.stufen.length === 1) {
            const stufe = verb.stufen[0]
            highlightClass = `verb-stufe-${stufe}`
            title = `${verb.lemma} — Stufe ${stufe} (${stufenNamen[stufe]})`
          } else {
            const primaryStufe = sent.taxonomie || verb.stufen[0]
            highlightClass = `verb-stufe-${primaryStufe}`
            const stufenText = verb.stufen.map(s => `${s} (${stufenNamen[s]})`).join(', ')
            title = `${verb.lemma} — Stufen: ${stufenText}`
          }
        } else if (verb.kategorie === 'nicht_empfohlen') {
          highlightClass = 'verb-bad'
          badVerbsCount++
          if (!allTextBadVerbs.includes(verb.lemma)) allTextBadVerbs.push(verb.lemma)
          title = `${verb.lemma} — nicht empfohlen (zu unspezifisch)`
        } else if (verb.kategorie === 'modal') {
          highlightClass = 'verb-modal'
          modalVerbsOC.push(verb.verb)
          title = `${verb.lemma} — Modalverb`
        } else if (verb.kategorie === 'mehrdeutig') {
          goodVerbsCount++
          if (!allTextGoodVerbs.includes(verb.lemma)) allTextGoodVerbs.push(verb.lemma)
          const primaryStufe = sent.taxonomie || verb.stufen[0]
          highlightClass = `verb-stufe-${primaryStufe}`
          const stufenText = verb.stufen.map(s => `${s} (${stufenNamen[s]})`).join(', ')
          title = `${verb.lemma} — mehrdeutig (Stufen: ${stufenText})`
          if (sent.taxonomie) {
            title += `, Zuordnung: Stufe ${sent.taxonomie} (${stufenNamen[sent.taxonomie]})`
          }
        } else {
          if (!neutralVerbs.includes(verb.lemma)) neutralVerbs.push(verb.lemma)
          if (sent.quelle === 'embedding' && sent.taxonomie) {
            highlightClass = `verb-stufe-${sent.taxonomie}`
            title = `${verb.lemma} — Embedding: Stufe ${sent.taxonomie} (${stufenNamen[sent.taxonomie]})`
          } else {
            title = `${verb.lemma} — nicht in Verbliste`
          }
        }

        for (const pos of positions) {
          highlights.push({ from: pos, to: pos + verb.verb.length, class: highlightClass, title })
        }
      }

      // Sätze ohne empfohlene Verben = "entbehrlich"
      const hasGoodVerb = sent.verben.some(v => v.kategorie === 'empfohlen' || v.kategorie === 'mehrdeutig')
      const hasBadVerb = sent.verben.some(v => v.kategorie === 'nicht_empfohlen')
      if (!hasGoodVerb && !hasBadVerb) {
        noVerbsSents.push(sent.text)
      }
    }

    // Score: gewichtete Kombination aus Formulierungsqualität (70%) und Taxonomie-Abdeckung (30%)
    // Begründung: HRK nexus fordert beobachtbare Verben (→ Verbqualität),
    // Anderson & Krathwohl fordern Abdeckung kognitiver Stufen (→ Coverage)
    const totalSents = sentences.length
    const badSentCount = sentences.filter(s =>
      s.verben.some(v => v.kategorie === 'nicht_empfohlen')
    ).length
    const noVerbSentCount = noVerbsSents.length

    let score = 0
    let badSentsScore = 0
    let noVerbsSentsScore = 0
    if (totalSents > 0) {
      badSentsScore = Math.round((badSentCount / totalSents) * 100)
      noVerbsSentsScore = Math.round((noVerbSentCount / totalSents) * 100)

      // Formulierungsqualität pro Satz (0..1)
      let qualitySum = 0
      for (const sent of sentences) {
        const hasEmpfohlen = sent.verben.some(v => v.kategorie === 'empfohlen')
        const hasMehrdeutig = sent.verben.some(v => v.kategorie === 'mehrdeutig')
        const hasBad = sent.verben.some(v => v.kategorie === 'nicht_empfohlen')
        const isK = sent.typ === 'K'

        if (isK && hasEmpfohlen && !hasBad) qualitySum += 1.0
        else if (isK && hasMehrdeutig && !hasBad) qualitySum += 0.7
        else if (isK && hasBad) qualitySum += 0.2
        else if (isK) qualitySum += 0.5
        // non-K sentences contribute 0
      }
      const verbQuality = qualitySum / totalSents

      // Taxonomie-Abdeckung (0..1)
      const stufen = new Set()
      for (const sent of sentences) {
        const ts = sent.taxonomie_stufen || (sent.taxonomie ? [sent.taxonomie] : [])
        for (const s of ts) stufen.add(s)
      }
      const coverage = stufen.size / 6

      score = Math.max(0, Math.round((0.7 * verbQuality + 0.3 * coverage) * 100))
    }

    // Satz-Details für die erweiterte Anzeige
    const sentenceDetails = sentences.map(s => ({
      text: s.text,
      typ: s.typ,
      taxonomie: s.taxonomie,
      taxonomie_stufen: s.taxonomie_stufen || (s.taxonomie ? [s.taxonomie] : []),
      konfidenz: s.konfidenz,
      quelle: s.quelle,
      aehnliche: s.aehnliche || [],
      warnungen: s.warnungen || [],
    }))

    return {
      sentences: sentences.map(s => s.text),
      highlights,
      goodVerbsCount,
      badVerbsCount,
      allTextGoodVerbs,
      allTextBadVerbs,
      neutralVerbs,
      noVerbsSents,
      modalVerbsOC,
      score,
      badSentsScore,
      noVerbsSentsScore,
      setAnalyse: result.set_analyse,
      sentenceDetails,
    }
  }

  function findWordPositions(text, word) {
    const positions = []
    const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const regex = new RegExp(`(?<=^|[\\s.,;:!?()\\[\\]{}\"'\\-/])${escaped}(?=$|[\\s.,;:!?()\\[\\]{}\"'\\-/])`, 'g')
    let match
    while ((match = regex.exec(text)) !== null) {
      positions.push(match.index)
    }
    return positions
  }

  return { analyzeText, processAnalysisResult }
}
