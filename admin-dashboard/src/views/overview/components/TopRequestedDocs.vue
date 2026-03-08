<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  docsList: { type: Array, required: true },
});

const router = useRouter();

const topDocs = computed(() => {
  const counts = {};
  props.docsList.forEach((d) => {
    const name = d.doctype_name || "Other";
    counts[name] = (counts[name] || 0) + 1;
  });

  const sorted = Object.entries(counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 4);

  const max = sorted[0]?.count || 1;
  return sorted.map((item) => ({ ...item, pct: (item.count / max) * 100 }));
});
</script>

<template>
  <div
    class="bg-white rounded-[24px] p-6 shadow-sm border border-gray-100 flex flex-col h-full"
  >
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-gray-800 tracking-tight">
          Top Requested Documents
        </h2>
        <p
          class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1"
        >
          By document type
        </p>
      </div>
      <button
        @click="router.push('/document-requests')"
        class="text-[11px] font-bold text-blue-600 uppercase tracking-widest hover:text-blue-800 transition-colors bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg"
      >
        View All
      </button>
    </div>

    <div class="flex flex-col gap-4 flex-1">
      <div
        v-if="topDocs.length === 0"
        class="text-sm text-gray-400 text-center mt-6"
      >
        No document data available.
      </div>

      <div
        v-for="(doc, i) in topDocs"
        :key="doc.name"
        class="flex flex-col gap-1 doc-row"
        :style="{ animationDelay: `${0.1 + i * 0.08}s` }"
      >
        <div class="flex items-center justify-between">
          <span class="text-sm font-semibold text-gray-700">{{
            doc.name
          }}</span>
          <span class="text-sm font-black text-gray-800">{{ doc.count }}</span>
        </div>
        <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full bar-fill bg-blue-500"
            :style="{
              '--target-width': doc.pct + '%',
              animationDelay: `${0.2 + i * 0.08}s`,
            }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.doc-row {
  opacity: 0;
  animation: rowFadeIn 0.4s ease forwards;
}
@keyframes rowFadeIn {
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
.bar-fill {
  width: 0;
  animation: barGrow 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes barGrow {
  from {
    width: 0;
  }
  to {
    width: var(--target-width);
  }
}
</style>
