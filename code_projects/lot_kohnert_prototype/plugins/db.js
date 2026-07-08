import Dexie from 'dexie'

export const db = new Dexie('kompetenzDB')
db.version(1).stores({
  verben: '++id, stufe, verb',
  schlechteVerben: '++id, verb',
  modalVerben: '++id, verb',
  einleitungen: '++id, *person, *adjektiv, *teilnahme, *modul', // MultiEntry Index
  kompetenzbeschreibungen:
    '++id, name, text, saetze, wertung, datum, datumUnix',
})
db.on('populate', function () {
  db.einleitungen.bulkAdd([
    {
      person: 'Studierende, Student, Studentin, Hörer, Hochschüler',
      adjektiv:
        'erfolgreich, positiv, optimal, bestmöglich, effizient, wirksam, angemessen',
      teilnahme: 'Teilnahme, Engagement, Aktivität, Beteiligung',
      modul:
        'Betriebswirtschaftslehre 1, Digitaltechnik und Rechnersysteme, Mathematische Grundlagen der Informatik, Programmierung 1, Programmiermethoden und -werkzeuge, Technische Grundlagen der Informatik ',
    },
  ])
  db.verben.bulkAdd([
    { stufe: 'erinnern', verb: 'erinnern' },
    { stufe: 'erinnern', verb: 'erkennen' },
    { stufe: 'erinnern', verb: 'identifizieren' },
    { stufe: 'erinnern', verb: 'wiederaufrufen' },
    { stufe: 'erinnern', verb: 'zurückrufen' },
    { stufe: 'erinnern', verb: 'wiederherstellen' },
    { stufe: 'erinnern', verb: 'reproduzieren' },
    { stufe: 'erinnern', verb: 'auflisten' },
    { stufe: 'erinnern', verb: 'wiederholen' },
    { stufe: 'erinnern', verb: 'darlegen' },
    { stufe: 'verstehen', verb: 'interpretieren' },
    { stufe: 'verstehen', verb: 'klären' },
    { stufe: 'verstehen', verb: 'paraphrasieren' },
    { stufe: 'verstehen', verb: 'darstellen' },
    { stufe: 'verstehen', verb: 'übersetzen' },
    { stufe: 'verstehen', verb: 'erläutern' },
    { stufe: 'verstehen', verb: 'illustrieren' },
    { stufe: 'verstehen', verb: 'veranschaulichen' },
    { stufe: 'verstehen', verb: 'realisieren' },
    { stufe: 'verstehen', verb: 'klassifizieren' },
    { stufe: 'verstehen', verb: 'kategorisieren' },
    { stufe: 'verstehen', verb: 'subsumieren' },
    { stufe: 'verstehen', verb: 'zusammenfassen' },
    { stufe: 'verstehen', verb: 'abstrahieren' },
    { stufe: 'verstehen', verb: 'generalisieren' },
    { stufe: 'verstehen', verb: 'folgern' },
    { stufe: 'verstehen', verb: 'schließen' },
    { stufe: 'verstehen', verb: 'interpolieren' },
    { stufe: 'verstehen', verb: 'extrapolieren' },
    { stufe: 'verstehen', verb: 'voraussagen' },
    { stufe: 'verstehen', verb: 'vergleichen' },
    { stufe: 'verstehen', verb: 'kontrastieren' },
    { stufe: 'verstehen', verb: 'abbilden' },
    { stufe: 'verstehen', verb: 'anpassen' },
    { stufe: 'verstehen', verb: 'erklären' },
    { stufe: 'verstehen', verb: 'modellieren' },
    { stufe: 'verstehen', verb: 'erkennen' },
    { stufe: 'verstehen', verb: 'diskutieren' },
    { stufe: 'verstehen', verb: 'beschreiben' },
    { stufe: 'anwenden', verb: 'anwenden' },
    { stufe: 'anwenden', verb: 'ausführen' },
    { stufe: 'anwenden', verb: 'benutzen' },
    { stufe: 'anwenden', verb: 'implementieren' },
    { stufe: 'anwenden', verb: 'durchführen' },
    { stufe: 'anwenden', verb: 'übertragen' },
    { stufe: 'anwenden', verb: 'handhaben' },
    { stufe: 'anwenden', verb: 'umsetzen' },
    { stufe: 'anwenden', verb: 'lösen' },
    { stufe: 'anwenden', verb: 'demonstrieren' },
    { stufe: 'anwenden', verb: 'ableiten' },
    { stufe: 'anwenden', verb: 'planen' },
    { stufe: 'anwenden', verb: 'steuern' },
    { stufe: 'analysieren', verb: 'analysieren' },
    { stufe: 'analysieren', verb: 'differenzieren' },
    { stufe: 'analysieren', verb: 'unterscheiden' },
    { stufe: 'analysieren', verb: 'kennzeichnen' },
    { stufe: 'analysieren', verb: 'charakterisieren' },
    { stufe: 'analysieren', verb: 'auslesen' },
    { stufe: 'analysieren', verb: 'auswählen' },
    { stufe: 'analysieren', verb: 'erfassen' },
    { stufe: 'analysieren', verb: 'organisieren' },
    { stufe: 'analysieren', verb: 'auffinden' },
    { stufe: 'analysieren', verb: 'Zusammenhänge' },
    { stufe: 'analysieren', verb: 'erkennen' },
    { stufe: 'analysieren', verb: 'hervorheben' },
    { stufe: 'analysieren', verb: 'unterstreichen' },
    { stufe: 'analysieren', verb: 'strukturieren' },
    { stufe: 'analysieren', verb: 'beifügen' },
    { stufe: 'analysieren', verb: 'aufteilen' },
    { stufe: 'evaluieren', verb: 'überprüfen' },
    { stufe: 'evaluieren', verb: 'abstimmen' },
    { stufe: 'evaluieren', verb: 'ermitteln' },
    { stufe: 'evaluieren', verb: 'überwachen' },
    { stufe: 'evaluieren', verb: 'testen' },
    { stufe: 'evaluieren', verb: 'beurteilen' },
    { stufe: 'evaluieren', verb: 'evaluieren' },
    { stufe: 'evaluieren', verb: 'auswerten' },
    { stufe: 'evaluieren', verb: 'schätzen' },
    { stufe: 'evaluieren', verb: 'kontrollieren' },
    { stufe: 'evaluieren', verb: 'reflektieren' },
    { stufe: 'kreieren', verb: 'generieren' },
    { stufe: 'kreieren', verb: 'kreieren' },
    { stufe: 'kreieren', verb: 'zusammenstellen' },
    { stufe: 'kreieren', verb: 'zusammenführen' },
    { stufe: 'kreieren', verb: 'entwerfen' },
    { stufe: 'kreieren', verb: 'produzieren' },
    { stufe: 'kreieren', verb: 'konstruieren' },
    { stufe: 'kreieren', verb: 'gestalten' },
    { stufe: 'kreieren', verb: 'entwickeln' },
  ])
  db.kompetenzbeschreibungen.bulkAdd([
    {
      name: 'Arbeits- und Führungstechniken',
      text: 'Die Studierenden kennen die wesentlichen Arbeits- und Führungstechniken in betrieblicher Arbeit/Projektarbeit und können Erfahrungen im Umgang mit diesen theoriegeleitet reflektieren. Sie verstehen Mechanismen, welche die Kommunikation in Teams beeinflussen, kennen Methoden und Möglichkeiten des Selbstmanagements und sind geschult im Umgang mit Konfliktsituationen.',
      saetze: 2,
      wertung: 0,
      datum: '31.03.2022',
      datumUnix: 1648740624,
    },
    {
      name: 'Research Project',
      text: 'Die Studierenden wenden Strategien der wissenschaftlichen Recherche und Einschätzung der Qualität wissenschaftlicher Ergebnisse im Rahmen eines konkreten Forschungszieles an. Die Studierenden können für eine gegebene Problemstellung wissenschaftlich nachvollziehbar Forschungsfragen oder Hypothesen ableiten. Die Studierenden können ihr Forschungsprojekt selbständig definieren. Die Studierende können ihren eigenen Arbeitsprozess und Zwischenergebnisse reflektierend in Worte fassen und daraus korrigierende Schlüsse ziehen im Hinblick auf die Erreichung des Forschungszieles. Die Studierenden können aus den etablierten Methoden eines Forschungsgebietes diejenigen begründet auswählen und anwenden, welche zur Erreichung der konkreten Forschungs(teil)- ziele geeignet sind. Die Studierenden können Ergebnisse eigener und fremder Forschungsarbeiten objektiv beschreiben, interpretieren und kritisch hinterfragen.',
      saetze: 6,
      wertung: 62.5,
      datum: '01.01.2022',
      datumUnix: 1641072734,
    },
  ])
  db.schlechteVerben.bulkAdd([
    {
      verb: 'wissen',
    },
    {
      verb: 'kennen',
    },
    {
      verb: 'erlangen',
    },
    {
      verb: 'beherrschen',
    },
    {
      verb: 'erwerben',
    },
    {
      verb: 'verstehen',
    },
  ])
  db.modalVerben.bulkAdd([
    {
      verb: 'können',
    },
  ])
})

db.open()
