import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default defineNuxtPlugin((nuxtApp) => {
  const vuetify = createVuetify({
    components,
    directives,
    theme: {
      defaultTheme: 'light',
      themes: {
        light: {
          colors: {
            primary: '#1a56db',
            secondary: '#64748b',
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6',
            background: '#f0f4f8',
            surface: '#ffffff',
          },
        },
      },
    },
    defaults: {
      VBtn: {
        style: 'text-transform: none; letter-spacing: 0;',
      },
      VCard: {
        elevation: 0,
      },
    },
  })
  nuxtApp.vueApp.use(vuetify)
})
