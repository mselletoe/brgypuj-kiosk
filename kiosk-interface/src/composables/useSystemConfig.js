import { computed } from "vue";
import { useSystemConfigStore } from "@/stores/systemConfig";

export function useSystemConfig() {
  const store = useSystemConfigStore();

  if (!store.fetched && !store.loading) {
    store.fetchConfig();
  }

  const brgyName = computed(() => store.brgyName);
  const brgySubname = computed(() => store.brgySubname);
  const hasLogo = computed(() => store.hasLogo);
  const resolvedLogoUrl = computed(() => {
    if (store.loading) return null;
    return store.logoBlobUrl ?? null;
  });

  return { brgyName, brgySubname, resolvedLogoUrl, hasLogo };
}
