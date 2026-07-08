<template>
  <div class="editor-layout">
    <!-- Main Editor Area -->
    <div class="editor-main">
      <!-- Toolbar -->
      <div class="editor-toolbar">
        <input
          v-model="compName"
          class="title-input"
          placeholder="Name / Modul eingeben…"
        />
        <div class="toolbar-actions">
          <v-btn
            variant="tonal"
            color="primary"
            rounded="lg"
            size="small"
            prepend-icon="mdi-content-save-outline"
            @click="onSave"
          >
            Speichern
          </v-btn>
        </div>
      </div>

      <!-- Editor Content -->
      <div class="editor-area">
        <div
          class="tiptap-editor"
          @click="focusEditor"
          @mouseover="onVerbHover"
          @mouseout="onVerbLeave"
        >
          <editor-content :editor="editor" />
        </div>

        <!-- Custom Verb Tooltip -->
        <div
          v-show="tooltip.visible"
          class="verb-tooltip"
          :class="tooltip.type"
          :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
        >
          {{ tooltip.text }}
        </div>
      </div>

      <!-- Score Bar -->
      <div class="score-bar">
        <div class="score-section score-main">
          <v-progress-circular
            :rotate="270"
            :size="60"
            :width="6"
            :model-value="score"
            :color="scoreColor"
          >
            <span class="score-label">{{ score }}%</span>
          </v-progress-circular>
          <div class="score-summary">
            <span class="score-title">Qualitätsscore</span>
            <span class="score-detail">{{ nlpSentences.length }} Sätze analysiert</span>
          </div>
        </div>

        <div class="score-section score-verbs">
          <div class="verb-stat good">
            <span class="verb-stat-count">{{ goodVerbsCount }}</span>
            <span class="verb-stat-label">empfohlene Verben</span>
          </div>
          <div class="verb-stat bad">
            <span class="verb-stat-count">{{ badVerbsCount }}</span>
            <span class="verb-stat-label">nicht empfohlene</span>
          </div>
        </div>

        <!-- Taxonomy levels with names and counts -->
        <div v-if="setAnalyse" class="score-section score-taxonomy">
          <span class="taxonomy-title">Kompetenzstufen</span>
          <div class="taxonomy-levels">
            <div
              v-for="stufe in 6"
              :key="stufe"
              class="taxonomy-level"
              :class="{ 'level-active': setAnalyse.verteilung[String(stufe)] > 0 }"
              :style="setAnalyse.verteilung[String(stufe)] > 0
                ? { background: stufenFarben[stufe].bg, borderColor: stufenFarben[stufe].border }
                : {}"
            >
              <span class="level-count" :style="setAnalyse.verteilung[String(stufe)] > 0 ? { color: stufenFarben[stufe].text } : {}">{{ setAnalyse.verteilung[String(stufe)] || 0 }}</span>
              <span class="level-name" :style="setAnalyse.verteilung[String(stufe)] > 0 ? { color: stufenFarben[stufe].text } : {}">{{ stufenNamen[stufe] }}</span>
            </div>
          </div>
        </div>

        <v-btn
          variant="text"
          color="grey"
          icon
          size="small"
          @click="suggestionsDrawer = !suggestionsDrawer"
        >
          <v-icon>mdi-{{ suggestionsDrawer ? 'chevron-right' : 'lightbulb-outline' }}</v-icon>
        </v-btn>
      </div>
    </div>

    <!-- Suggestions Drawer -->
    <Transition name="slide">
      <div v-show="suggestionsDrawer" class="suggestions-panel">
        <div class="suggestions-header">
          <h3 class="text-subtitle-2 font-weight-bold">Empfehlungen</h3>
          <v-btn icon variant="text" size="x-small" @click="suggestionsDrawer = false">
            <v-icon size="18">mdi-close</v-icon>
          </v-btn>
        </div>

        <div class="suggestions-content">
          <!-- Sentence-level analysis with confidence -->
          <div v-if="sentenceDetails.length > 0" class="suggestion-section">
            <div class="section-label section-analyse">Satzanalyse</div>
            <div
              v-for="(sent, i) in sentenceDetails"
              :key="'sent-'+i"
              class="sentence-card"
              :class="{ 'sent-nicht-k': sent.typ !== 'K' }"
            >
              <div class="sentence-text">{{ sent.text.length > 80 ? sent.text.slice(0, 77) + '…' : sent.text }}</div>
              <div class="sentence-meta">
                <span class="meta-chip" :class="'chip-typ-' + sent.typ.toLowerCase()">{{ sent.typ === 'K' ? 'Kompetenz' : sent.typ === 'I' ? 'Inhalt' : 'Sonstiges' }}</span>
                <span
                  v-if="sent.typ === 'K' && sent.taxonomie"
                  class="meta-chip"
                  :style="stufenFarben[sent.taxonomie] ? { background: stufenFarben[sent.taxonomie].bg, color: stufenFarben[sent.taxonomie].text } : {}"
                >Stufe {{ sent.taxonomie }}</span>
                <span class="meta-chip chip-quelle">{{ sent.quelle === 'regel' ? 'Regel' : 'SBERT' }}</span>
                <span
                  class="meta-chip chip-konfidenz"
                  :class="sent.konfidenz >= 0.8 ? 'conf-high' : sent.konfidenz >= 0.5 ? 'conf-mid' : 'conf-low'"
                  :title="'Konfidenz: ' + Math.round(sent.konfidenz * 100) + '%'"
                >{{ Math.round(sent.konfidenz * 100) }}%</span>
              </div>
            </div>
          </div>

          <!-- Warnings (bad verbs, modals) -->
          <div v-if="badVerbRule || modalVerbRule" class="suggestion-section">
            <div class="section-label section-bad">Warnungen</div>
            <div v-for="(item, i) in allTextBadVerbs" :key="'bad-'+i" class="suggestion-card bad">
              <div class="suggestion-verb">{{ item }}</div>
              <p class="suggestion-tip">Nicht empfohlen — zu unspezifisch und schwer messbar.</p>
            </div>
            <div v-for="(item, i) in modalVerbsOC" :key="'modal-'+i" class="suggestion-card modal">
              <div class="suggestion-verb">können</div>
              <p class="suggestion-tip">Modalverb — versuchen Sie den Satz ohne "können" umzuformulieren.</p>
            </div>
          </div>

          <!-- Similar formulations (recommendations) -->
          <div v-if="topSimilar.length > 0" class="suggestion-section">
            <div class="section-label section-similar">Referenzformulierungen</div>
            <div class="filter-chips">
              <button
                v-for="stufe in 6"
                :key="'filter-'+stufe"
                class="filter-chip"
                :class="{ active: filterStufe === stufe }"
                :style="filterStufe === stufe ? { background: stufenFarben[stufe].bg, color: stufenFarben[stufe].text, borderColor: stufenFarben[stufe].border } : {}"
                @click="filterStufe = filterStufe === stufe ? null : stufe"
              >{{ stufe }}</button>
              <button v-if="filterStufe" class="filter-chip filter-clear" @click="filterStufe = null">✕</button>
            </div>
            <div v-for="(sim, i) in filteredSimilar" :key="'sim-'+i" class="suggestion-card similar">
              <div class="suggestion-sentence">"{{ sim.satz }}"</div>
              <div class="similar-meta">
                <span
                  class="meta-tag"
                  :style="sim.taxonomie && stufenFarben[sim.taxonomie]
                    ? { background: stufenFarben[sim.taxonomie].bg, color: stufenFarben[sim.taxonomie].text }
                    : {}"
                >Stufe {{ sim.taxonomie }} · {{ stufenNamen[sim.taxonomie] || '' }}</span>
                <span class="meta-module">{{ sim.modulname }}</span>
              </div>
            </div>
            <div v-if="filteredSimilar.length === 0" class="suggestion-tip" style="padding: 8px 0; color: #94a3b8;">
              Keine Empfehlungen für Stufe {{ filterStufe }}.
            </div>
          </div>

          <!-- Set-Analyse hint (only if gaps) -->
          <div v-if="setAnalyse && setAnalyse.abdeckung < 6" class="suggestion-section">
            <div class="section-label section-set">Abdeckung</div>
            <div class="suggestion-card set-hint">
              <p class="suggestion-tip">{{ setAnalyse.empfehlung }}</p>
            </div>
          </div>

          <!-- Empty state -->
          <div v-if="!badVerbRule && !modalVerbRule && topSimilar.length === 0" class="suggestions-empty">
            <v-icon size="36" color="grey-lighten-1">mdi-lightbulb-outline</v-icon>
            <p class="text-body-2 text-grey mt-2">
              Empfehlungen erscheinen hier nach der Analyse.
            </p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Save Dialog -->
    <v-dialog v-model="dialogAction" width="440" persistent>
      <v-card rounded="xl">
        <v-card-title class="text-h6 pt-5 px-6">
          Kompetenzbeschreibung speichern
        </v-card-title>
        <v-card-text class="px-6">
          <p class="text-body-2 text-grey-darken-1 mb-4">
            Geben Sie einen Namen für Ihre Kompetenzbeschreibung ein.
          </p>
          <v-text-field
            v-model="compName"
            label="Name / Modul"
            variant="outlined"
            rounded="lg"
            hide-details
            density="comfortable"
          />
        </v-card-text>
        <v-card-actions class="pa-6 pt-2">
          <v-spacer />
          <v-btn variant="text" color="grey" rounded="lg" @click="dialogAction = false">
            Abbrechen
          </v-btn>
          <v-btn variant="flat" color="primary" rounded="lg" @click="saveComp()">
            Speichern
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </div>
</template>

<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { VerbHighlight, setVerbHighlights } from '~/extensions/verbHighlight'

// Composables
const editorStore = useEditorStore()
const { getKompetenzbeschreibung, saveKompetenzbeschreibung } = useDatabase()
const { analyzeText, processAnalysisResult } = useAnalysis()

const stufenNamen = { 1: 'Erinnern', 2: 'Verstehen', 3: 'Anwenden', 4: 'Analysieren', 5: 'Bewerten', 6: 'Erschaffen' }
const stufenFarben = {
  1: { bg: '#e0f2fe', text: '#0369a1', border: '#7dd3fc' },
  2: { bg: '#d1fae5', text: '#047857', border: '#6ee7b7' },
  3: { bg: '#fef9c3', text: '#a16207', border: '#fde047' },
  4: { bg: '#ffedd5', text: '#c2410c', border: '#fdba74' },
  5: { bg: '#fce7f3', text: '#be185d', border: '#f9a8d4' },
  6: { bg: '#ede9fe', text: '#6d28d9', border: '#c4b5fd' },
}

// Analysis state
const nlpSentences = ref([])
const goodVerbsCount = ref(0)
const badVerbsCount = ref(0)
const allTextGoodVerbs = ref([])
const allTextBadVerbs = ref([])
const neutralVerbs = ref([])
const noVerbsSents = ref([])
const modalVerbsOC = ref([])
const score = ref(0)
const badSentsScore = ref(0)
const noVerbsSentsScore = ref(0)

// NEW: Extended analysis state
const sentenceDetails = ref([])
const setAnalyse = ref(null)

// Top similar sentences (dedupliziert, max 5 über alle Sätze)
const topSimilar = computed(() => {
  const seen = new Set()
  const results = []
  for (const sent of sentenceDetails.value) {
    for (const sim of sent.aehnliche) {
      if (!seen.has(sim.satz) && results.length < 5) {
        seen.add(sim.satz)
        results.push(sim)
      }
    }
  }
  return results
})

// Taxonomy filter for recommendations
const filterStufe = ref(null)
const filteredSimilar = computed(() => {
  if (!filterStufe.value) return topSimilar.value
  return topSimilar.value.filter(s => String(s.taxonomie).split(';').map(Number).includes(filterStufe.value))
})

// Suggestion panel state
const badVerbRule = ref(false)
const modalVerbRule = ref(false)
const suggestionsDrawer = ref(true)

// Dialog state
const dialogAction = ref(false)

// Tooltip state
const tooltip = reactive({ visible: false, text: '', x: 0, y: 0, type: '' })

function onVerbHover(e) {
  const el = e.target.closest('[data-tooltip]')
  if (!el) return
  const rect = el.getBoundingClientRect()
  const editorArea = el.closest('.editor-area').getBoundingClientRect()
  tooltip.text = el.getAttribute('data-tooltip')
  tooltip.x = rect.left - editorArea.left
  tooltip.y = rect.top - editorArea.top - 36
  const stufeMatch = [...el.classList].find(c => c.startsWith('verb-stufe-'))
  if (stufeMatch) {
    tooltip.type = `tip-${stufeMatch.replace('verb-', '')}`
  } else if (el.classList.contains('verb-bad')) {
    tooltip.type = 'tip-bad'
  } else if (el.classList.contains('verb-modal')) {
    tooltip.type = 'tip-modal'
  } else {
    tooltip.type = 'tip-neutral'
  }
  tooltip.visible = true
}

function onVerbLeave(e) {
  if (!e.target.closest('[data-tooltip]')) return
  tooltip.visible = false
}

// Editor state
const compName = ref('Unbenannt')
const compID = ref(editorStore.currCompetenceID || 0)
let analysisTimer = null

const scoreColor = computed(() => {
  if (score.value >= 75) return 'green'
  if (score.value >= 40) return 'amber-darken-1'
  return 'red'
})

// Tiptap editor
const editor = useEditor({
  extensions: [StarterKit, VerbHighlight],
  content: '',
  onUpdate() {
    clearTimeout(analysisTimer)
    analysisTimer = setTimeout(() => { analyze() }, 1000)
  },
  onCreate() {
    loadCompetence()
  },
})

function focusEditor() {
  if (editor.value) editor.value.commands.focus()
}

async function analyze() {
  if (!editor.value) return
  const text = editor.value.getText()
  if (!text || text.trim() === '') {
    resetAnalysis()
    return
  }

  try {
    const result = await analyzeText(text)
    if (!result) return

    const processed = processAnalysisResult(result, text)

    nlpSentences.value = processed.sentences
    goodVerbsCount.value = processed.goodVerbsCount
    badVerbsCount.value = processed.badVerbsCount
    allTextGoodVerbs.value = processed.allTextGoodVerbs
    allTextBadVerbs.value = processed.allTextBadVerbs
    neutralVerbs.value = processed.neutralVerbs
    noVerbsSents.value = processed.noVerbsSents
    modalVerbsOC.value = processed.modalVerbsOC
    score.value = processed.score
    badSentsScore.value = processed.badSentsScore
    noVerbsSentsScore.value = processed.noVerbsSentsScore
    sentenceDetails.value = processed.sentenceDetails
    setAnalyse.value = processed.setAnalyse

    showSuggestions()

    const pmHighlights = textToProseMirrorHighlights(editor.value, processed.highlights)
    setVerbHighlights(editor.value, pmHighlights)
  } catch (err) {
    console.error('Analysis error:', err)
  }
}

function textToProseMirrorHighlights(editorInstance, highlights) {
  if (!editorInstance || highlights.length === 0) return []

  const posMap = []
  editorInstance.state.doc.descendants((node, pos) => {
    if (node.isText) {
      for (let i = 0; i < node.text.length; i++) {
        posMap.push(pos + i)
      }
    } else if (node.isBlock && node.type.name !== 'doc' && posMap.length > 0) {
      posMap.push(-1)
    }
  })

  const pmHighlights = []
  for (const h of highlights) {
    if (h.from >= 0 && h.to <= posMap.length && h.from < h.to) {
      const fromPos = posMap[h.from]
      const toPos = posMap[h.to - 1]
      if (fromPos >= 0 && toPos >= 0) {
        const entry = { from: fromPos, to: toPos + 1, class: h.class }
        if (h.title) entry.title = h.title
        pmHighlights.push(entry)
      }
    }
  }

  return pmHighlights
}

function resetAnalysis() {
  nlpSentences.value = []
  goodVerbsCount.value = 0
  badVerbsCount.value = 0
  allTextGoodVerbs.value = []
  allTextBadVerbs.value = []
  neutralVerbs.value = []
  noVerbsSents.value = []
  modalVerbsOC.value = []
  score.value = 0
  badSentsScore.value = 0
  noVerbsSentsScore.value = 0
  sentenceDetails.value = []
  setAnalyse.value = null
  badVerbRule.value = false
  modalVerbRule.value = false
  if (editor.value) setVerbHighlights(editor.value, [])
}

function showSuggestions() {
  badVerbRule.value = badVerbsCount.value > 0
  modalVerbRule.value = modalVerbsOC.value.length > 0
}

function onSave() {
  if (compName.value === 'Unbenannt') {
    dialogAction.value = true
  } else {
    saveComp()
  }
}

async function saveComp() {
  dialogAction.value = false
  const today = new Date()
  const date = today.getDate() + '.' + (today.getMonth() + 1) + '.' + today.getFullYear()
  const text = editor.value ? editor.value.getText() : ''

  const data = {
    name: compName.value,
    text,
    saetze: nlpSentences.value.length,
    wertung: score.value,
    datum: date,
    datumUnix: Math.floor(today.getTime() / 1000),
  }

  try {
    const resID = await saveKompetenzbeschreibung(compID.value, data)
    if (compID.value === 0) {
      compID.value = resID
      editorStore.currCompetenceID = resID
    }
    editorStore.lastSavedCompetenceID = compID.value
  } catch (err) {
    console.error('Save error:', err)
  }
}

async function loadCompetence() {
  if (compID.value > 0 && editor.value) {
    try {
      const record = await getKompetenzbeschreibung(compID.value)
      if (record) {
        compName.value = record.name
        editor.value.commands.setContent(`<p>${record.text}</p>`)
        await nextTick()
        await analyze()
      }
    } catch (err) {
      console.error('Load error:', err)
    }
  }
}

onBeforeUnmount(() => {
  if (editor.value) editor.value.destroy()
})
</script>

<style scoped>
.editor-layout {
  display: flex;
  height: calc(100vh - 48px);
  overflow: hidden;
}

.editor-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.title-input {
  flex: 1;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  border: none;
  outline: none;
  background: transparent;
  padding: 6px 0;
}

.title-input::placeholder {
  color: #94a3b8;
  font-weight: 400;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.editor-area {
  position: relative;
  flex: 1;
  overflow: hidden;
  background: white;
  margin: 16px 24px;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.score-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 18px 24px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.04);
}

.score-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-main {
  flex-shrink: 0;
}

.score-label {
  font-size: 14px;
  font-weight: 800;
}

.score-summary {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.score-title {
  font-size: 13px;
  font-weight: 700;
  color: #1e293b;
}

.score-detail {
  font-size: 12px;
  color: #64748b;
}

.score-verbs {
  gap: 16px;
  padding: 0 20px;
  border-left: 1px solid #e2e8f0;
  border-right: 1px solid #e2e8f0;
}

.verb-stat {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.verb-stat-count {
  font-size: 18px;
  font-weight: 800;
  line-height: 1;
}

.verb-stat.good .verb-stat-count { color: #16a34a; }
.verb-stat.bad .verb-stat-count { color: #dc2626; }

.verb-stat-label {
  font-size: 12px;
  color: #64748b;
}

/* Taxonomy levels */
.score-taxonomy {
  flex: 1;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.taxonomy-title {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.taxonomy-levels {
  display: flex;
  gap: 3px;
}

.taxonomy-level {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  border-radius: 6px;
  background: #f1f5f9;
  border: 1px solid transparent;
  min-width: 56px;
  transition: all 0.2s ease;
}

.taxonomy-level .level-count {
  font-size: 14px;
  font-weight: 800;
  color: #94a3b8;
  line-height: 1;
}

.taxonomy-level .level-name {
  font-size: 9px;
  color: #94a3b8;
  font-weight: 500;
  line-height: 1;
  white-space: nowrap;
}

/* Suggestions Panel */
.suggestions-panel {
  width: 340px;
  flex-shrink: 0;
  background: white;
  border-left: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.suggestions-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.suggestions-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.suggestion-section {
  margin-bottom: 20px;
}

.section-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 4px 8px;
  border-radius: 6px;
  margin-bottom: 8px;
  display: inline-block;
}

.section-bad { background: #fee2e2; color: #dc2626; }
.section-set { background: #f0fdf4; color: #15803d; }
.section-similar { background: #faf5ff; color: #7e22ce; }
.section-analyse { background: #f0f9ff; color: #0369a1; }

/* Sentence analysis cards */
.sentence-card {
  padding: 8px 10px;
  border-radius: 8px;
  margin-bottom: 4px;
  background: #fafafa;
  border: 1px solid #f1f5f9;
}

.sentence-card.sent-nicht-k {
  opacity: 0.65;
}

.sentence-text {
  font-size: 11px;
  color: #475569;
  line-height: 1.3;
  margin-bottom: 4px;
}

.sentence-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.meta-chip {
  font-size: 9px;
  font-weight: 600;
  padding: 1px 5px;
  border-radius: 3px;
  background: #f1f5f9;
  color: #475569;
  white-space: nowrap;
}

.chip-typ-k { background: #d1fae5; color: #047857; }
.chip-typ-i { background: #e0f2fe; color: #0369a1; }
.chip-typ-s { background: #f1f5f9; color: #64748b; }
.chip-quelle { background: #f5f3ff; color: #6d28d9; }

.chip-konfidenz { font-weight: 800; }
.chip-konfidenz.conf-high { background: #d1fae5; color: #047857; }
.chip-konfidenz.conf-mid { background: #fef9c3; color: #a16207; }
.chip-konfidenz.conf-low { background: #fee2e2; color: #dc2626; }

.suggestion-card {
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 8px;
  border: 1px solid #e2e8f0;
}

.suggestion-card.bad { border-left: 3px solid #ef4444; }
.suggestion-card.modal { border-left: 3px solid #3b82f6; }
.suggestion-card.similar { border-left: 3px solid #a855f7; }
.suggestion-card.set-hint { border-left: 3px solid #22c55e; }

.suggestion-verb {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
  color: #1e293b;
}

.suggestion-sentence {
  font-size: 13px;
  font-style: italic;
  color: #475569;
  margin-bottom: 8px;
  line-height: 1.4;
}

.suggestion-tip {
  font-size: 12px;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.suggestions-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

/* Similar sentences meta */
.similar-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  font-size: 11px;
}

.meta-tag {
  background: #f1f5f9;
  color: #475569;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 10px;
}

.meta-module {
  color: #64748b;
}

/* Transitions */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}

.slide-enter-from,
.slide-leave-to {
  width: 0;
  opacity: 0;
}

/* Responsive */
@media (max-width: 960px) {
  .suggestions-panel {
    position: fixed;
    right: 0;
    top: 48px;
    height: calc(100vh - 48px);
    z-index: 100;
    box-shadow: -4px 0 24px rgba(0, 0, 0, 0.1);
  }

  .score-metrics {
    gap: 8px;
  }

  .metric {
    padding: 4px 8px;
  }
}

/* Verb Tooltip */
.verb-tooltip {
  position: absolute;
  z-index: 50;
  pointer-events: none;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.4;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
  animation: tooltip-in 0.15s ease;
}

.verb-tooltip.tip-bad {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.verb-tooltip.tip-modal {
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.verb-tooltip.tip-neutral {
  background: #f8fafc;
  color: #334155;
  border: 1px solid #e2e8f0;
}

.verb-tooltip.tip-stufe-1 {
  background: var(--color-stufe-1-bg);
  color: var(--color-stufe-1);
  border: 1px solid var(--color-stufe-1-border);
}

.verb-tooltip.tip-stufe-2 {
  background: var(--color-stufe-2-bg);
  color: var(--color-stufe-2);
  border: 1px solid var(--color-stufe-2-border);
}

.verb-tooltip.tip-stufe-3 {
  background: var(--color-stufe-3-bg);
  color: var(--color-stufe-3);
  border: 1px solid var(--color-stufe-3-border);
}

.verb-tooltip.tip-stufe-4 {
  background: var(--color-stufe-4-bg);
  color: var(--color-stufe-4);
  border: 1px solid var(--color-stufe-4-border);
}

.verb-tooltip.tip-stufe-5 {
  background: var(--color-stufe-5-bg);
  color: var(--color-stufe-5);
  border: 1px solid var(--color-stufe-5-border);
}

.verb-tooltip.tip-stufe-6 {
  background: var(--color-stufe-6-bg);
  color: var(--color-stufe-6);
  border: 1px solid var(--color-stufe-6-border);
}

@keyframes tooltip-in {
  from { opacity: 0; transform: translateY(0); }
  to { opacity: 1; transform: translateY(-4px); }
}

/* Filter chips for recommendations */
.filter-chips {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.filter-chip {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-chip:hover {
  background: #e2e8f0;
}

.filter-chip.active {
  border-style: solid;
}

.filter-clear {
  font-size: 10px;
  padding: 2px 6px;
  color: #94a3b8;
}
</style>
