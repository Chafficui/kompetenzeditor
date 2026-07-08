<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      :mini-variant="miniVariant"
      :clipped="clipped"
      fixed
      app
    >
      <v-list>
        <v-list-item
          v-for="([icon, link, text], i) in drawerItems"
          :key="i"
          link
          :to="link"
          color="primary"
        >
          <v-list-item-icon>
            <v-icon>{{ icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>{{ text }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <template v-slot:append>
        <div class="py-2">
          <v-btn block depressed tile @click.stop="miniVariant = !miniVariant">
            <v-icon
              >mdi-{{
                `arrow-collapse-${miniVariant ? 'right' : 'left'}`
              }}</v-icon
            >
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>
    <v-app-bar :clipped-left="clipped" fixed flat app dark color="#004A7E">
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <NuxtLink
        to="/"
        style="text-decoration: none; color: rgba(0, 0, 0, 0.87)"
      >
        <v-toolbar-title class="white--text" v-text="title" />
      </NuxtLink>
      <v-chip color="red" class="ml-3" label dark>Beta</v-chip>
      <v-spacer />
    </v-app-bar>
    <v-main>
      <v-container fluid class="pa-0">
        <Nuxt />
      </v-container>
    </v-main>
    <v-footer fixed app>
      <span>&copy; {{ new Date().getFullYear() }}</span>
      <v-spacer></v-spacer>
    </v-footer>
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      clipped: true,
      drawer: true,
      compLinks: [],
      drawerItems: [
        ['mdi-home', '/', 'Meine Texte'],
        ['mdi-text-box-plus', '/editor', 'Texteditor'],
        ['mdi-cog', '/settings', 'Einstellungen'],
      ],
      miniVariant: false,
      title: 'Kompetenzeditor',
      currentComp: null,
    }
  },
}
</script>
<style>
html {
  min-width: 850px !important;
  overflow-y: auto;
}
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
::-webkit-scrollbar-track {
  background: rgba(158, 158, 158, 0.3);
}
::-webkit-scrollbar-thumb {
  background: rgba(158, 158, 158, 0.6);
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(158, 158, 158, 1);
}
</style>
