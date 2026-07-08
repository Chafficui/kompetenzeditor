<template>
  <div class="settings-container">
    <h1 class="text-h5 font-weight-bold text-grey-darken-3 mb-6">Einstellungen</h1>

    <div class="status-section">
      <h2 class="text-subtitle-1 font-weight-bold mb-3">Backend-Status</h2>
      <div class="status-cards">
        <div class="status-card" :class="backendClass">
          <div class="status-icon">
            <v-icon :color="backendOk ? 'green' : 'red'" size="20">
              mdi-{{ backendOk ? 'check-circle' : 'close-circle' }}
            </v-icon>
          </div>
          <div class="status-info">
            <span class="status-label">Backend API</span>
            <span class="status-value">{{ backendText }}</span>
          </div>
        </div>
        <div class="status-card" :class="modelsClass">
          <div class="status-icon">
            <v-icon :color="modelsOk ? 'green' : modelsOk === false ? 'red' : 'grey'" size="20">
              mdi-{{ modelsOk ? 'check-circle' : modelsOk === false ? 'close-circle' : 'circle-outline' }}
            </v-icon>
          </div>
          <div class="status-info">
            <span class="status-label">Modelle (spaCy, SBERT, SVM)</span>
            <span class="status-value">{{ modelsText }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const backendOk = ref(null)
const backendText = ref('Wird geprüft...')
const modelsOk = ref(null)
const modelsText = ref('Wird geprüft...')

const backendClass = computed(() =>
  backendOk.value === null ? '' : backendOk.value ? 'status-ok' : 'status-err'
)
const modelsClass = computed(() =>
  modelsOk.value === null ? '' : modelsOk.value ? 'status-ok' : 'status-err'
)

async function checkHealth() {
  try {
    const res = await $fetch('/api/health', { method: 'GET' })
    backendOk.value = true
    backendText.value = 'Erreichbar'
    modelsOk.value = res.models_loaded
    modelsText.value = res.models_loaded ? 'Geladen' : 'Nicht geladen'
  } catch {
    backendOk.value = false
    backendText.value = 'Nicht erreichbar'
    modelsOk.value = false
    modelsText.value = 'Unbekannt'
  }
}

onMounted(() => {
  checkHealth()
})
</script>

<style scoped>
.settings-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 32px 24px;
}

.status-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  transition: border-color 0.3s ease, background 0.3s ease;
}

.status-card.status-ok {
  border-color: #a7f3d0;
  background: #f0fdf4;
}

.status-card.status-err {
  border-color: #fecaca;
  background: #fef2f2;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-label {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.status-value {
  font-size: 12px;
  color: #64748b;
}
</style>
