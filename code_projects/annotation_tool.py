#!/usr/bin/env python3
"""
Interaktives Annotations-Tool für den Gold-Standard.
Geführter Entscheidungsbaum nach Annotationsleitfaden + Verb-Highlighting.

Usage:
  python3 annotation_tool.py [--port 8888]
"""

import argparse
import csv
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

DATA_FILE = Path(__file__).parent.parent / "data" / "goldstandard_sample.csv"
FIELDNAMES = [
    "studiengang", "modul_id", "modulname", "satz_nr", "satz",
    "llm_typ", "llm_taxonomie", "llm_konfidenz",
    "typ", "taxonomie", "kommentar"
]

HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Gold-Standard Annotation</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
       background: #0f172a; color: #e2e8f0; min-height: 100vh; }
.container { max-width: 960px; margin: 0 auto; padding: 20px; }

/* Progress */
.progress-bar { background: #1e293b; border-radius: 8px; height: 8px; margin-bottom: 10px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6); transition: width 0.3s; }
.progress-text { text-align: center; font-size: 13px; color: #94a3b8; margin-bottom: 16px; }
.progress-text b { color: #e2e8f0; }

/* Stats */
.stats-bar { display: flex; gap: 16px; justify-content: center; margin-bottom: 16px; flex-wrap: wrap; }
.stat { font-size: 12px; color: #64748b; } .stat b { color: #94a3b8; }

/* Filter */
.filter-bar { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.filter-btn { padding: 6px 14px; border-radius: 6px; border: 1px solid #334155;
              background: transparent; color: #94a3b8; font-size: 12px; cursor: pointer; }
.filter-btn.active { background: #1e3a5f; border-color: #3b82f6; color: #e2e8f0; }

/* Card */
.card { background: #1e293b; border-radius: 16px; padding: 28px 32px; margin-bottom: 20px;
        border: 1px solid #334155; }
.meta { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.tag { background: #334155; border-radius: 6px; padding: 4px 10px; font-size: 12px; color: #94a3b8; }
.tag.warn { background: #7f1d1d; color: #fca5a5; }

/* Sentence with verb highlights */
.sentence { font-size: 20px; line-height: 1.7; color: #f1f5f9; margin-bottom: 4px; }
.v1 { background: #1e3a5f; border-bottom: 2px solid #60a5fa; padding: 1px 3px; border-radius: 3px; }
.v2 { background: #1a3a2a; border-bottom: 2px solid #4ade80; padding: 1px 3px; border-radius: 3px; }
.v3 { background: #3b1f4a; border-bottom: 2px solid #c084fc; padding: 1px 3px; border-radius: 3px; }
.v4 { background: #3a2e1a; border-bottom: 2px solid #fbbf24; padding: 1px 3px; border-radius: 3px; }
.v5 { background: #3a1a1a; border-bottom: 2px solid #f87171; padding: 1px 3px; border-radius: 3px; }
.v6 { background: #1a2e3a; border-bottom: 2px solid #22d3ee; padding: 1px 3px; border-radius: 3px; }
.v-ambig { border-bottom: 2px dashed #94a3b8; padding: 1px 3px; }
.v-neg { background: #2a1a1a; border-bottom: 2px solid #ef4444; padding: 1px 3px; border-radius: 3px; text-decoration: line-through; text-decoration-color: #ef444480; }

/* Legend */
.legend { display: flex; gap: 12px; flex-wrap: wrap; margin: 8px 0 20px; }
.legend-item { font-size: 11px; color: #94a3b8; display: flex; align-items: center; gap: 4px; }
.legend-dot { width: 10px; height: 10px; border-radius: 2px; }

/* Decision tree */
.decision { margin-top: 20px; }
.decision-step { background: #0f172a; border: 1px solid #334155; border-radius: 12px;
                 padding: 20px; margin-bottom: 16px; }
.decision-step.active { border-color: #3b82f6; }
.decision-step.done { opacity: 0.5; }
.step-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.step-num { background: #3b82f6; color: white; width: 28px; height: 28px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.step-num.done-num { background: #22c55e; }
.step-title { font-size: 15px; font-weight: 600; color: #e2e8f0; }
.step-rule { font-size: 13px; color: #94a3b8; line-height: 1.5; margin-bottom: 14px;
             background: #1e293b; padding: 10px 14px; border-radius: 8px; border-left: 3px solid #3b82f6; }
.step-rule em { color: #fbbf24; font-style: normal; }

/* Buttons */
.btn-row { display: flex; gap: 10px; flex-wrap: wrap; }
.btn { padding: 12px 20px; border-radius: 10px; border: 2px solid #334155;
       background: #1e293b; color: #e2e8f0; font-size: 14px; cursor: pointer;
       transition: all 0.15s; text-align: left; line-height: 1.4; }
.btn:hover { border-color: #3b82f6; background: #1e3a5f; }
.btn.selected { border-color: #3b82f6; background: #1e3a5f; box-shadow: 0 0 0 1px #3b82f6; }
.btn.agreed { border-color: #22c55e; }
.btn.disagreed { border-color: #ef4444; }
.btn .key { display: inline-block; background: #475569; border-radius: 4px;
            padding: 1px 6px; font-size: 11px; margin-right: 4px; font-family: monospace; vertical-align: middle; }
.btn-wide { flex: 1; min-width: 200px; }

/* Taxonomy buttons */
.tax-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.btn-tax { padding: 10px 14px; }
.btn-tax .tax-level { font-weight: 700; font-size: 16px; }
.btn-tax .tax-name { font-weight: 600; }
.btn-tax .tax-verbs { font-size: 11px; color: #64748b; margin-top: 3px; }

/* Context hint */
.context-hint { background: #1a2e1a; border: 1px solid #22c55e40; border-radius: 8px;
                padding: 10px 14px; margin-top: 12px; font-size: 13px; color: #86efac; }
.context-hint.warn { background: #2a1a1a; border-color: #ef444440; color: #fca5a5; }

/* Comparison */
.comparison { background: #0f172a; border-radius: 10px; padding: 14px; margin-top: 16px;
              border: 1px solid #334155; font-size: 13px; }
.comparison h4 { color: #64748b; margin-bottom: 6px; }
.match { color: #22c55e; } .mismatch { color: #ef4444; }

/* Comment */
.comment-row { margin-top: 12px; }
.comment-input { width: 100%; background: #0f172a; border: 1px solid #334155; border-radius: 8px;
                 padding: 10px 14px; color: #e2e8f0; font-size: 14px; outline: none; }
.comment-input:focus { border-color: #3b82f6; }

/* Nav */
.nav { display: flex; gap: 12px; justify-content: space-between; align-items: center; margin-top: 20px; }
.nav-btn { padding: 12px 28px; border-radius: 10px; border: none;
           font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.nav-prev { background: #334155; color: #e2e8f0; }
.nav-prev:hover { background: #475569; }
.nav-next { background: #3b82f6; color: white; }
.nav-next:hover { background: #2563eb; }
.nav-skip { background: transparent; color: #64748b; border: 1px solid #334155; }
.nav-skip:hover { color: #94a3b8; border-color: #475569; }
.keyboard-hint { text-align: center; font-size: 11px; color: #475569; margin-top: 8px; }

/* Done */
.done { text-align: center; padding: 60px 20px; }
.done h2 { font-size: 28px; margin-bottom: 16px; color: #22c55e; }
.done p { color: #94a3b8; margin-bottom: 8px; }
.download-btn { display: inline-block; margin-top: 24px; padding: 14px 32px;
                background: #3b82f6; color: white; border-radius: 10px; cursor: pointer; border: none; font-size: 16px; font-weight: 600; }
</style>
</head>
<body>
<div class="container" id="app">
  <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
  <div class="progress-text" id="progressText"></div>
  <div class="stats-bar" id="statsBar"></div>
  <div class="filter-bar" id="filterBar"></div>
  <div id="mainContent"></div>
</div>

<script>
// === VERB DATABASE ===
const VERB_DB = {
  1: { name: 'Erinnern', color: 'v1', verbs: [
    'erinnern','identifizieren','wiederaufrufen','zurückrufen','wiederherstellen',
    'reproduzieren','auflisten','wiederholen','darlegen','wiedergeben','nennen',
    'benennen','aufzählen','angeben','definieren','remember','identify','list','name','recall',
  ]},
  2: { name: 'Verstehen', color: 'v2', verbs: [
    'interpretieren','klären','paraphrasieren','darstellen','übersetzen','erläutern',
    'illustrieren','veranschaulichen','klassifizieren','kategorisieren','subsumieren',
    'zusammenfassen','abstrahieren','generalisieren','folgern','schließen','interpolieren',
    'extrapolieren','voraussagen','vergleichen','kontrastieren','abbilden','erklären',
    'modellieren','diskutieren','beschreiben','nachvollziehen','einordnen','zuordnen',
    'understand','explain','describe','summarize','compare','discuss','interpret','classify',
  ]},
  3: { name: 'Anwenden', color: 'v3', verbs: [
    'anwenden','ausführen','benutzen','implementieren','durchführen','übertragen',
    'handhaben','umsetzen','lösen','demonstrieren','ableiten','steuern',
    'berechnen','einsetzen','nutzen','verwenden','programmieren','konfigurieren',
    'formulieren','bestimmen','ermitteln',
    'apply','execute','implement','use','solve','calculate','demonstrate','carry out',
  ]},
  4: { name: 'Analysieren', color: 'v4', verbs: [
    'analysieren','differenzieren','unterscheiden','kennzeichnen','charakterisieren',
    'auslesen','erfassen','organisieren','auffinden','hervorheben','unterstreichen',
    'strukturieren','aufteilen','untersuchen','gegenüberstellen','zergliedern',
    'analyze','differentiate','distinguish','examine','organize','structure',
  ]},
  5: { name: 'Bewerten', color: 'v5', verbs: [
    'überprüfen','abstimmen','überwachen','testen','beurteilen','evaluieren',
    'auswerten','kontrollieren','reflektieren','bewerten','einschätzen',
    'abwägen','kritisieren','begründen','rechtfertigen','hinterfragen',
    'evaluate','judge','assess','review','critique','justify','reflect',
  ]},
  6: { name: 'Erschaffen', color: 'v6', verbs: [
    'generieren','kreieren','zusammenstellen','zusammenführen','entwerfen',
    'produzieren','konstruieren','gestalten','entwickeln','konzipieren','erstellen',
    'verfassen','designen','modellieren','synthetisieren','planen',
    'create','design','develop','construct','produce','compose','plan',
  ]},
};

const AMBIG_VERBS = {
  'erkennen': 'Mehrdeutig: Stufe 1 (wiedererkennen), 4 (Muster erkennen) oder 5 (Grenzen erkennen) — Kontext entscheidet!',
  'kennen': 'Regel 7: Allein = Stufe 1. Mit "und können X" → Stufe des X-Verbs.',
  'können': 'Regel 7: "können" + Infinitiv → Stufe des Infinitivverbs.',
  'wissen': 'Meist Stufe 1 (Erinnern), außer Kontext zeigt höhere kognitive Leistung.',
  'verstehen': 'Regel 8: Standard = Stufe 2. "Verstehen und erklären" = Stufe 2.',
  'beherrschen': 'Kontextabhängig: "Methoden beherrschen" ≈ Stufe 3 (Anwenden).',
  'verfügen': 'Unterspezifiziert: "verfügen über Kenntnisse" = Stufe 1.',
  'anpassen': 'Kontextabhängig: Stufe 2 (verstehend anpassen) oder 3 (praktisch anpassen).',
  'realisieren': 'Kontextabhängig: Stufe 2 (begreifen) oder 6 (umsetzen/erschaffen).',
};

const NEG_VERBS = ['vermeiden','unterlassen','vergessen','ignorieren'];
const FRAME_PATTERNS = ['sind in der Lage','ist in der Lage','sind fähig','sind befähigt',
  'have the ability','are able to','in der Lage'];

function highlightSentence(text) {
  // Build a lookup: word → {level, color} or 'ambig' or 'neg'
  const words = text.split(/(\s+|[,;:.!?()\[\]„""'])/);
  let html = '';
  let hints = [];

  for (const word of words) {
    const lower = word.toLowerCase().replace(/[.,;:!?()„""']/g, '');
    if (!lower || lower.length < 3) { html += esc(word); continue; }

    // Check negative verbs
    if (NEG_VERBS.some(v => lower === v || lower.startsWith(v.slice(0,-2)))) {
      html += `<span class="v-neg" title="Negatives Verb">${esc(word)}</span>`;
      continue;
    }

    // Check ambiguous verbs (before taxonomy to take priority)
    let ambigKey = Object.keys(AMBIG_VERBS).find(v =>
      lower === v || lower.startsWith(v.slice(0, -2)) ||
      (v.endsWith('en') && lower.startsWith(v.slice(0, -2)))
    );
    if (ambigKey && !Object.values(VERB_DB).some(l => l.verbs.includes(lower))) {
      html += `<span class="v-ambig" title="${AMBIG_VERBS[ambigKey]}">${esc(word)}</span>`;
      hints.push(AMBIG_VERBS[ambigKey]);
      continue;
    }

    // Check taxonomy verbs
    let matched = false;
    for (const [level, info] of Object.entries(VERB_DB)) {
      const found = info.verbs.some(v => {
        if (lower === v) return true;
        // Stem matching: remove -en/-n ending
        const stem = v.replace(/e?n$/, '');
        if (stem.length >= 4 && lower.startsWith(stem)) return true;
        return false;
      });
      if (found) {
        html += `<span class="${info.color}" title="Stufe ${level}: ${info.name}">${esc(word)}</span>`;
        matched = true;
        // Also check if this verb is in ambiguous list
        if (ambigKey) hints.push(AMBIG_VERBS[ambigKey]);
        break;
      }
    }
    if (!matched) html += esc(word);
  }

  return { html, hints };
}

function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Check for frame patterns ("sind in der Lage" etc.)
function detectFrame(text) {
  const lower = text.toLowerCase();
  for (const p of FRAME_PATTERNS) {
    if (lower.includes(p)) return p;
  }
  return null;
}

// Detect if students are the subject
function detectSubject(text) {
  const lower = text.toLowerCase();
  if (/^(die\s+)?(studierenden|teilnehmenden|teilnehmer|students)\s/i.test(text)) return 'students';
  if (/^(das\s+modul|die\s+veranstaltung|die\s+vorlesung|the\s+module|the\s+course)\s/i.test(text)) return 'module';
  if (/^(es\s+werden|es\s+wird|grundlagen\s+werden|inhalte\s+werden)/i.test(text)) return 'passive';
  if (/^[a-zäöü]/.test(text)) return 'infinitive'; // lowercase start = bullet point / infinitive
  return 'unknown';
}

// === APP STATE ===
let data = [];
let currentIndex = 0;
let filter = 'todo';
let filteredIndices = [];

async function loadData() {
  data = await (await fetch('/api/data')).json();
  updateFilter();
  render();
}

function getFiltered() {
  const all = data.map((_, i) => i);
  if (filter === 'all') return all;
  if (filter === 'todo') return all.filter(i => !data[i].typ);
  if (filter === 'done') return all.filter(i => !!data[i].typ);
  if (filter === 'low_conf') return all.filter(i => parseFloat(data[i].llm_konfidenz) < 0.7);
  if (filter === 'disagreed') return all.filter(i =>
    data[i].typ && (data[i].typ !== data[i].llm_typ || data[i].taxonomie !== data[i].llm_taxonomie));
  return all;
}

function updateFilter() {
  filteredIndices = getFiltered();
  if (currentIndex >= filteredIndices.length) currentIndex = Math.max(0, filteredIndices.length - 1);
}

function stats() {
  let done = 0, agreed = 0, disagreed = 0;
  for (const d of data) {
    if (d.typ) {
      done++;
      if (d.typ === d.llm_typ && (d.typ !== 'K' || d.taxonomie === d.llm_taxonomie)) agreed++;
      else disagreed++;
    }
  }
  return { total: data.length, done, todo: data.length - done, agreed, disagreed };
}

function render() {
  const s = stats();

  // Stats
  document.getElementById('statsBar').innerHTML =
    `<div class="stat">Gesamt: <b>${s.total}</b></div>
     <div class="stat">Erledigt: <b>${s.done}</b></div>
     <div class="stat">Offen: <b>${s.todo}</b></div>
     <div class="stat" style="color:#22c55e">Übereinstimmung: <b>${s.agreed}</b></div>
     <div class="stat" style="color:#ef4444">Korrigiert: <b>${s.disagreed}</b></div>`;

  // Filters
  const counts = {
    todo: data.filter(d => !d.typ).length,
    all: data.length,
    done: data.filter(d => !!d.typ).length,
    low_conf: data.filter(d => parseFloat(d.llm_konfidenz) < 0.7).length,
    disagreed: data.filter(d => d.typ && (d.typ !== d.llm_typ || d.taxonomie !== d.llm_taxonomie)).length,
  };
  const labels = { todo:'Offen', all:'Alle', done:'Erledigt', low_conf:'Niedrige Konfidenz', disagreed:'Korrigiert' };
  document.getElementById('filterBar').innerHTML = Object.entries(labels).map(([k,v]) =>
    `<button class="filter-btn ${filter===k?'active':''}" onclick="setFilter('${k}')">${v} (${counts[k]})</button>`
  ).join('');

  // Progress
  document.getElementById('progressFill').style.width = `${s.done/s.total*100}%`;
  document.getElementById('progressText').innerHTML =
    `<b>${s.done}</b> von <b>${s.total}</b> annotiert — Position ${currentIndex+1}/${filteredIndices.length}`;

  if (filteredIndices.length === 0) {
    document.getElementById('mainContent').innerHTML = filter === 'todo'
      ? `<div class="done"><h2>Alle Sätze annotiert!</h2>
         <p>Übereinstimmung mit LLM: ${s.agreed}/${s.done} (${(s.agreed/s.done*100).toFixed(1)}%)</p>
         <button class="download-btn" onclick="location.href='/api/download'">CSV herunterladen</button></div>`
      : `<div class="done"><h2>Keine Sätze in diesem Filter</h2></div>`;
    return;
  }

  const dataIdx = filteredIndices[currentIndex];
  renderSentence(data[dataIdx], dataIdx);
}

function renderSentence(d, dataIdx) {
  const { html: sentHtml, hints } = highlightSentence(d.satz);
  const subject = detectSubject(d.satz);
  const frame = detectFrame(d.satz);
  const isLowConf = parseFloat(d.llm_konfidenz) < 0.7;

  let h = `<div class="card">
    <div class="meta">
      <span class="tag">${esc(d.studiengang)}</span>
      <span class="tag">${esc(d.modul_id)} ${esc(d.modulname)}</span>
      <span class="tag">Satz ${d.satz_nr}</span>
      <span class="tag ${isLowConf ? 'warn' : ''}">LLM: ${d.llm_typ}${d.llm_taxonomie ? '/'+d.llm_taxonomie : ''} (${d.llm_konfidenz})</span>
    </div>
    <div class="sentence">${sentHtml}</div>
    <div class="legend">
      <div class="legend-item"><div class="legend-dot" style="background:#60a5fa"></div>1 Erinnern</div>
      <div class="legend-item"><div class="legend-dot" style="background:#4ade80"></div>2 Verstehen</div>
      <div class="legend-item"><div class="legend-dot" style="background:#c084fc"></div>3 Anwenden</div>
      <div class="legend-item"><div class="legend-dot" style="background:#fbbf24"></div>4 Analysieren</div>
      <div class="legend-item"><div class="legend-dot" style="background:#f87171"></div>5 Bewerten</div>
      <div class="legend-item"><div class="legend-dot" style="background:#22d3ee"></div>6 Erschaffen</div>
      <div class="legend-item"><div class="legend-dot" style="background:transparent;border:1px dashed #94a3b8"></div>Mehrdeutig</div>
    </div>`;

  // Show verb hints if any
  if (hints.length > 0) {
    const unique = [...new Set(hints)];
    h += `<div class="context-hint warn">${unique.map(h => '⚠ ' + esc(h)).join('<br>')}</div>`;
  }

  // Show frame detection hint
  if (frame) {
    h += `<div class="context-hint">Regel 9: „${esc(frame)}" ist taxonomisch neutral — die Stufe wird durch das nachfolgende Verb bestimmt.</div>`;
  }

  h += `</div>`; // end card

  // === DECISION TREE ===
  h += `<div class="decision">`;

  // --- STEP 1: Classification ---
  const typDone = !!d.typ;
  h += `<div class="decision-step ${!typDone ? 'active' : 'done'}">
    <div class="step-header">
      <div class="step-num ${typDone ? 'done-num' : ''}">1</div>
      <div class="step-title">Klassifikation</div>
    </div>
    <div class="step-rule">
      <b>Regel 1 — Handlungsverb-Test:</b> Enthält der Satz ein <em>beobachtbares/messbares Handlungsverb</em> der Studierenden?<br>
      <b>Regel 3 — Subjekt-Test:</b> Sind <em>Studierende</em> das Subjekt? (Nicht das Modul, nicht passiv)`;

  if (subject === 'module') h += `<br>⚠ Erkannt: <em>Modul/Veranstaltung als Subjekt</em> → eher I`;
  if (subject === 'passive') h += `<br>⚠ Erkannt: <em>Passivkonstruktion</em> → eher I`;
  if (subject === 'infinitive') h += `<br>ℹ Erkannt: <em>Infinitivkonstruktion</em> (Regel 4) → K wenn messbare Handlung`;

  h += `</div><div class="btn-row">`;

  for (const [t, label, desc] of [
    ['K', 'Kompetenzformulierung', 'Handlungsverb + Studierende als Subjekt'],
    ['I', 'Inhaltsbeschreibung', 'Beschreibt Inhalte/Themen, kein Handlungsergebnis'],
    ['S', 'Sonstiges', 'Einleitung, Fragment, Organisatorisches'],
  ]) {
    let cls = 'btn btn-wide';
    if (d.typ === t) {
      cls += ' selected';
      cls += (d.llm_typ === t) ? ' agreed' : ' disagreed';
    }
    h += `<button class="${cls}" onclick="setTyp(${dataIdx},'${t}')">
      <span class="key">${t}</span> <b>${label}</b><br>
      <span style="font-size:12px;color:#94a3b8">${desc}</span>
    </button>`;
  }
  h += `</div></div>`;

  // --- STEP 2: Taxonomy (only if K) ---
  if (d.typ === 'K') {
    const taxDone = !!d.taxonomie;
    h += `<div class="decision-step ${!taxDone ? 'active' : 'done'}">
      <div class="step-header">
        <div class="step-num ${taxDone ? 'done-num' : ''}">2</div>
        <div class="step-title">Taxonomiestufe nach Anderson & Krathwohl</div>
      </div>
      <div class="step-rule">
        <b>Regel 5:</b> Primäres Handlungsverb bestimmt die Stufe. Bei mehreren → <em>höchste Stufe</em>.<br>
        <b>Regel 6 (Stanny):</b> Viele Verben sind mehrdeutig — <em>Kontext entscheidet</em>.<br>
        <b>Regel 10:</b> Stufe 6 nur bei <em>genuiner Neuschöpfung</em>, nicht für „Zusammenfassung erstellen" (→2).
      </div>
      <div class="tax-grid">`;

    for (const [level, info] of Object.entries(VERB_DB)) {
      let cls = 'btn btn-tax';
      if (d.taxonomie === level) {
        cls += ' selected';
        cls += (d.llm_taxonomie === level) ? ' agreed' : ' disagreed';
      }
      h += `<button class="${cls}" onclick="setTax(${dataIdx},'${level}')">
        <div><span class="key">${level}</span> <span class="tax-level" style="color:var(--c)">${info.name}</span></div>
        <div class="tax-verbs">${info.verbs.filter(v => !/[A-Z]/.test(v[0])).slice(0,8).join(', ')}</div>
      </button>`;
    }
    h += `</div></div>`;
  }

  // --- COMPARISON (after both steps) ---
  if (d.typ && (d.typ !== 'K' || d.taxonomie)) {
    const typOk = d.typ === d.llm_typ;
    const taxOk = d.typ !== 'K' || d.taxonomie === d.llm_taxonomie;
    h += `<div class="comparison">
      <h4>Vergleich mit LLM-Vorannotation</h4>
      <span>Typ: <b class="${typOk?'match':'mismatch'}">${d.llm_typ}</b> ${typOk ? '✓ übereinstimmend' : '✗ → korrigiert zu '+d.typ}</span>`;
    if (d.typ === 'K' || d.llm_typ === 'K') {
      h += ` &nbsp;|&nbsp; Taxonomie: <b class="${taxOk?'match':'mismatch'}">${d.llm_taxonomie||'–'}</b> ${taxOk ? '✓' : '✗ → '+d.taxonomie}`;
    }
    h += `</div>`;
  }

  // Comment
  h += `<div class="comment-row">
    <input class="comment-input" id="commentInput" placeholder="Kommentar (optional, z.B. bei Zweifelsfällen)..."
           value="${esc(d.kommentar||'')}"
           onchange="setComment(${dataIdx},this.value)">
  </div>`;

  h += `</div>`; // end decision

  // Nav
  h += `<div class="nav">
    <button class="nav-btn nav-prev" onclick="goPrev()" ${currentIndex===0?'disabled':''}>← Zurück</button>
    <button class="nav-btn nav-skip" onclick="goNext()">Überspringen</button>
    <button class="nav-btn nav-next" onclick="goNext()">Weiter →</button>
  </div>
  <div class="keyboard-hint">K/I/S = Typ &nbsp; 1-6 = Stufe &nbsp; ←/→ = Navigation &nbsp; Enter = Weiter &nbsp; C = Kommentar</div>`;

  document.getElementById('mainContent').innerHTML = h;
}

function setFilter(f) { filter = f; currentIndex = 0; updateFilter(); render(); }

async function setTyp(idx, typ) {
  data[idx].typ = typ;
  if (typ !== 'K') data[idx].taxonomie = '';
  await save(idx);
  render();
  if (typ !== 'K') setTimeout(goNext, 400);
}

async function setTax(idx, level) {
  data[idx].taxonomie = level;
  await save(idx);
  render();
  setTimeout(goNext, 500);
}

async function setComment(idx, c) { data[idx].kommentar = c; await save(idx); }

async function save(idx) {
  await fetch('/api/save', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({index: idx, row: data[idx]})
  });
}

function goNext() {
  if (currentIndex < filteredIndices.length - 1) { currentIndex++; render(); window.scrollTo(0,0); }
  else { updateFilter(); if (filteredIndices.length === 0) render(); else { currentIndex = 0; render(); } }
}
function goPrev() {
  if (currentIndex > 0) { currentIndex--; render(); window.scrollTo(0,0); }
}

document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT') return;
  const idx = filteredIndices[currentIndex];
  if (idx === undefined) return;
  if (e.key === 'k' || e.key === 'K') setTyp(idx, 'K');
  else if (e.key === 'i' || e.key === 'I') setTyp(idx, 'I');
  else if (e.key === 's' || e.key === 'S') setTyp(idx, 'S');
  else if (e.key >= '1' && e.key <= '6' && data[idx].typ === 'K') setTax(idx, e.key);
  else if (e.key === 'ArrowRight' || e.key === 'Enter') { e.preventDefault(); goNext(); }
  else if (e.key === 'ArrowLeft') goPrev();
  else if (e.key === 'c' || e.key === 'C') document.getElementById('commentInput')?.focus();
});

loadData();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    rows = []

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/', '/index.html'):
            self._respond(200, 'text/html', HTML.encode('utf-8'))
        elif path == '/api/data':
            self._respond(200, 'application/json',
                          json.dumps(self.rows, ensure_ascii=False).encode('utf-8'))
        elif path == '/api/download':
            import io
            buf = io.StringIO()
            csv.DictWriter(buf, fieldnames=FIELDNAMES).writeheader()
            csv.DictWriter(buf, fieldnames=FIELDNAMES).writerows(self.rows)
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="goldstandard_annotiert.csv"')
            self.end_headers()
            self.wfile.write(buf.getvalue().encode('utf-8'))
        else:
            self._respond(404, 'text/plain', b'Not found')

    def do_POST(self):
        if urlparse(self.path).path == '/api/save':
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
            idx, row = body['index'], body['row']
            if 0 <= idx < len(self.rows):
                for k in ('typ', 'taxonomie', 'kommentar'):
                    self.rows[idx][k] = row.get(k, '')
                with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
                    w = csv.DictWriter(f, fieldnames=FIELDNAMES)
                    w.writeheader()
                    w.writerows(self.rows)
            self._respond(200, 'application/json', b'{"ok":true}')
        else:
            self._respond(404, 'text/plain', b'Not found')

    def _respond(self, code, content_type, body):
        self.send_response(code)
        self.send_header('Content-Type', f'{content_type}; charset=utf-8')
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8888)
    args = parser.parse_args()

    with open(DATA_FILE, encoding='utf-8') as f:
        Handler.rows = list(csv.DictReader(f))

    done = sum(1 for r in Handler.rows if r.get('typ'))
    print(f"Annotations-Tool gestartet")
    print(f"  {len(Handler.rows)} Sätze ({done} bereits annotiert)")
    print(f"  http://localhost:{args.port}")
    print(f"  Strg+C zum Beenden\n")
    print(f"  Tasten: K/I/S = Typ, 1-6 = Stufe, ←/→ = Navigation, C = Kommentar")

    webbrowser.open(f'http://localhost:{args.port}')
    try:
        HTTPServer(('localhost', args.port), Handler).serve_forever()
    except KeyboardInterrupt:
        print(f"\nGespeichert: {DATA_FILE}")


if __name__ == '__main__':
    main()
