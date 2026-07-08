<template>
  <v-app>
    <v-app-bar flat color="white" border="b" density="compact">
      <template v-slot:prepend>
        <v-app-bar-nav-icon
          variant="text"
          color="primary"
          @click="drawer = !drawer"
        />
      </template>

      <v-app-bar-title>
        <NuxtLink to="/" class="app-title">
          <span class="font-weight-bold text-primary">Kompetenz</span><span class="text-grey-darken-1">editor</span>
        </NuxtLink>
      </v-app-bar-title>

      <template v-slot:append>
        <v-chip color="primary" variant="tonal" size="small" label>
          Beta
        </v-chip>
      </template>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" :rail="rail" color="white" border="r">
      <v-list density="compact" nav class="mt-2">
        <v-list-item
          v-for="([icon, link, text], i) in drawerItems"
          :key="i"
          :to="link"
          :prepend-icon="icon"
          :title="text"
          rounded="lg"
          color="primary"
          class="mb-1"
        />
      </v-list>

      <template v-slot:append>
        <div class="pa-2">
          <v-btn
            block
            variant="text"
            size="small"
            color="grey"
            @click.stop="rail = !rail"
          >
            <v-icon>mdi-{{ rail ? 'chevron-right' : 'chevron-left' }}</v-icon>
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main class="bg-grey-lighten-4">
      <NuxtPage />
    </v-main>
  </v-app>
</template>

<script setup>
const drawer = ref(true)
const rail = ref(true)
const drawerItems = [
  ['mdi-file-document-multiple-outline', '/', 'Meine Texte'],
  ['mdi-pencil-outline', '/editor', 'Editor'],
  ['mdi-cog-outline', '/settings', 'Einstellungen'],
]
</script>

<style scoped>
.app-title {
  text-decoration: none;
  font-size: 1.1rem;
  letter-spacing: -0.3px;
}
</style>
