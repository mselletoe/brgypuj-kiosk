/**
 * @file composables/useSystemConfig.js
 */
import { computed } from 'vue'
import { useSystemConfigStore } from '@/stores/systemConfig'
import fallbackLogo from '@/assets/images/Pob1Logo.svg'

export function useSystemConfig() {
  const store = useSystemConfigStore()

  if (!store.fetched && !store.loading) {
    store.fetchConfig()
  }

  const brgyName        = computed(() => store.brgyName)
  const brgySubname     = computed(() => store.brgySubname)
  const hasLogo         = computed(() => store.hasLogo)
  // Use the in-memory blob URL; fall back to the bundled SVG if no logo is set
  const resolvedLogoUrl = computed(() => store.logoBlobUrl ?? fallbackLogo)

  return { brgyName, brgySubname, resolvedLogoUrl, hasLogo }
}