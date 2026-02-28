import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLanguageStore = defineStore('language', () => {
  const currentLang = ref('FIL')

  const toggleLang = () => {
    currentLang.value = currentLang.value === 'FIL' ? 'ENG' : 'FIL'
  }

  const setLang = (lang) => {
    currentLang.value = lang
  }

  return { currentLang, toggleLang, setLang }
})