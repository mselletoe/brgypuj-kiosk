<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  show: Boolean,
  allData: Object, // We pass the loaded dashboard data here
});

const emit = defineEmits(["close"]);
const searchQuery = ref("");
const router = useRouter();

const results = computed(() => {
  const q = searchQuery.value.toLowerCase();
  if (q.length < 2) return [];

  const found = [];

  // Search Residents
  props.allData.residentsList?.forEach((r) => {
    if (
      r.first_name?.toLowerCase().includes(q) ||
      r.last_name?.toLowerCase().includes(q)
    ) {
      found.push({
        type: "Resident",
        name: `${r.first_name} ${r.last_name}`,
        path: "/residents-management",
      });
    }
  });

  // Search Documents
  props.allData.docsList?.forEach((d) => {
    if (
      d.doctype_name?.toLowerCase().includes(q) ||
      d.tracking_number?.toLowerCase().includes(q)
    ) {
      found.push({
        type: "Document",
        name: d.doctype_name,
        detail: d.tracking_number,
        path: "/document-requests",
      });
    }
  });

  return found.slice(0, 10); // Limit to top 10 for speed
});

const navigate = (path) => {
  router.push(path);
  emit("close");
};
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z- flex items-start justify-center pt-24 px-4 bg-gray-900/40 backdrop-blur-sm"
    @click.self="emit('close')"
  >
    <div
      class="bg-white w-full max-w-2xl rounded-2xl shadow-2xl border border-gray-100 overflow-hidden animate-in fade-in zoom-in duration-200"
    >
      <div class="p-4 border-b border-gray-100 flex items-center gap-3">
        <svg
          class="w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          v-model="searchQuery"
          v-focus
          placeholder="Search for residents, documents, or equipment..."
          class="flex-1 outline-none text-lg text-gray-700"
          @keydown.esc="emit('close')"
        />
      </div>

      <div class="max-h-[400px] overflow-y-auto p-2">
        <div
          v-if="results.length === 0 && searchQuery.length > 1"
          class="p-8 text-center text-gray-400"
        >
          No results found for "{{ searchQuery }}"
        </div>

        <div
          v-for="res in results"
          :key="res.name"
          @click="navigate(res.path)"
          class="flex items-center justify-between p-3 hover:bg-blue-50 rounded-xl cursor-pointer group transition-colors"
        >
          <div class="flex flex-col">
            <span
              class="text-xs font-black text-blue-600 uppercase tracking-widest"
              >{{ res.type }}</span
            >
            <span class="text-gray-800 font-bold">{{ res.name }}</span>
            <span v-if="res.detail" class="text-xs text-gray-400">{{
              res.detail
            }}</span>
          </div>
          <svg
            class="w-5 h-5 text-gray-300 group-hover:text-blue-500 transition-colors"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>
