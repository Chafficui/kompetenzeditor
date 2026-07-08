<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="text-h5 font-weight-bold text-grey-darken-3">Meine Texte</h1>
      <v-btn
        color="primary"
        variant="flat"
        rounded="lg"
        prepend-icon="mdi-plus"
        @click="setCurrCompID(0)"
      >
        Neu erstellen
      </v-btn>
    </div>

    <v-row>
      <v-col
        v-for="(item, index) in compLinks"
        :key="index"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card rounded="xl" elevation="0" class="comp-card" border>
          <v-card-text class="pb-2">
            <div class="d-flex align-center justify-space-between mb-2">
              <v-chip size="x-small" variant="tonal" color="grey" label>
                <v-icon start size="10">mdi-calendar</v-icon>
                {{ item.date }}
              </v-chip>
              <v-chip size="x-small" variant="tonal" color="grey" label>
                #{{ item.nmbr }}
              </v-chip>
            </div>

            <h3 class="text-subtitle-1 font-weight-bold text-truncate mb-3">
              {{ item.title }}
            </h3>

            <div class="d-flex ga-2">
              <div class="metric-badge">
                <span class="metric-label">Sätze</span>
                <span class="metric-value">{{ item.sentences }}</span>
              </div>
              <div class="metric-badge" :class="scoreClass(item.score)">
                <span class="metric-label">Wertung</span>
                <span class="metric-value">{{ item.score }}%</span>
              </div>
            </div>
          </v-card-text>

          <v-divider />

          <v-card-actions class="pa-3">
            <v-btn
              variant="tonal"
              color="primary"
              rounded="lg"
              block
              size="small"
              @click="setCurrCompID(item.id)"
            >
              <v-icon start size="16">mdi-pencil-outline</v-icon>
              Öffnen
            </v-btn>
            <v-btn
              variant="text"
              color="error"
              icon
              size="small"
              rounded="lg"
              @click="deleteComp(item.id, index)"
            >
              <v-icon size="18">mdi-trash-can-outline</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <div v-if="compLinks.length === 0" class="empty-state">
      <v-icon size="64" color="grey-lighten-1">mdi-file-document-outline</v-icon>
      <p class="text-body-1 text-grey mt-4">Noch keine Texte vorhanden.</p>
      <v-btn
        color="primary"
        variant="tonal"
        rounded="lg"
        class="mt-2"
        @click="setCurrCompID(0)"
      >
        Erste Kompetenzbeschreibung erstellen
      </v-btn>
    </div>
  </div>
</template>

<script setup>
const editorStore = useEditorStore()
const { getAllKompetenzbeschreibungen, deleteKompetenzbeschreibung } = useDatabase()

const compLinks = ref([])

function scoreClass(score) {
  if (score >= 75) return 'metric-good'
  if (score >= 40) return 'metric-warn'
  return 'metric-bad'
}

async function fillCompLinkList() {
  const comps = await getAllKompetenzbeschreibungen()
  compLinks.value = comps.map((item) => ({
    nmbr: item.id,
    title: item.name,
    id: item.id,
    date: item.datum,
    sentences: item.saetze,
    score: Number(item.wertung).toFixed(1),
  })).reverse()
}

function setCurrCompID(id) {
  editorStore.currCompetenceID = id
  navigateTo('/editor')
}

async function deleteComp(id, i) {
  compLinks.value.splice(i, 1)
  try {
    await deleteKompetenzbeschreibung(id)
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  fillCompLinkList()
})
</script>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.comp-card {
  transition: box-shadow 0.2s ease, transform 0.15s ease;
}

.comp-card:hover {
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08) !important;
  transform: translateY(-2px);
}

.metric-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  background: #f1f5f9;
  font-size: 12px;
}

.metric-badge .metric-label {
  color: #64748b;
  font-weight: 500;
}

.metric-badge .metric-value {
  color: #1e293b;
  font-weight: 700;
}

.metric-good {
  background: #d1fae5 !important;
}
.metric-good .metric-value {
  color: #059669 !important;
}

.metric-warn {
  background: #fef3c7 !important;
}
.metric-warn .metric-value {
  color: #d97706 !important;
}

.metric-bad {
  background: #fee2e2 !important;
}
.metric-bad .metric-value {
  color: #dc2626 !important;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}
</style>
