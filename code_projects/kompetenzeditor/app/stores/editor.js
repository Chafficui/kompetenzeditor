import { defineStore } from 'pinia'

export const useEditorStore = defineStore('editor', {
  state: () => ({
    currCompetenceID: 0,
    lastSavedCompetenceID: null,
  }),
})
