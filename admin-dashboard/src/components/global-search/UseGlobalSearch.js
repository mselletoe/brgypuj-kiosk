import { ref, computed, watch } from "vue";
import axios from "axios";

const TYPE_LABELS = {
  members: "Residents",
  documents: "Document Requests",
  equipment: "Equipment",
  equipment_requests: "Equipment Requests",
  blotter: "Blotter Records",
};

const TYPE_ICONS = {
  members: "👤",
  documents: "📄",
  equipment: "🎒",
  equipment_requests: "📋",
  blotter: "⚖️",
};

export function useGlobalSearch() {
  const query = ref("");
  const isOpen = ref(false);
  const isLoading = ref(false);
  const rawResults = ref({});
  const recentSearches = ref(
    JSON.parse(localStorage.getItem("gs_recent") || "[]"),
  );

  let debounceTimer = null;

  watch(query, (val) => {
    clearTimeout(debounceTimer);
    rawResults.value = {};

    if (!val.trim()) {
      isLoading.value = false;
      return;
    }

    isLoading.value = true;
    debounceTimer = setTimeout(async () => {
      try {
        const { data } = await axios.get("/admin/search", {
          params: { q: val.trim() },
        });
        rawResults.value = data;
      } catch (e) {
        console.error("Search error:", e);
        rawResults.value = {};
      } finally {
        isLoading.value = false;
      }
    }, 300);
  });

  const results = computed(() =>
    Object.entries(rawResults.value)
      .map(([type, items]) => ({
        type,
        label: TYPE_LABELS[type] ?? type,
        icon: TYPE_ICONS[type] ?? "🔍",
        items,
      }))
      .filter((group) => Array.isArray(group.items) && group.items.length > 0),
  );

  const hasResults = computed(() => results.value.length > 0);
  const totalCount = computed(() =>
    results.value.reduce((sum, g) => sum + g.items.length, 0),
  );

  function open() {
    isOpen.value = true;
  }
  function close() {
    isOpen.value = false;
    query.value = "";
    rawResults.value = {};
  }

  function addToRecent(label) {
    const updated = [
      label,
      ...recentSearches.value.filter((r) => r !== label),
    ].slice(0, 5);
    recentSearches.value = updated;
    localStorage.setItem("gs_recent", JSON.stringify(updated));
  }

  function clearRecent() {
    recentSearches.value = [];
    localStorage.removeItem("gs_recent");
  }

  function onKeydown(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      isOpen.value ? close() : open();
    }
    if (e.key === "Escape") close();
  }

  return {
    query,
    isOpen,
    isLoading,
    results,
    hasResults,
    totalCount,
    recentSearches,
    open,
    close,
    addToRecent,
    clearRecent,
    onKeydown,
  };
}
