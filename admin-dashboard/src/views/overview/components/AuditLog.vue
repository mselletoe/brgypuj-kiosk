<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  auditLogs: { type: Array, required: true },
});

const router = useRouter();
const displayedLogs = computed(() => props.auditLogs.slice(0, 10));

const navigateToLog = (log) => {
  if (log.type === "doc") router.push("/document-requests");
  else if (log.type === "equip") router.push("/equipment-requests");
  else if (log.type === "resident") router.push("/residents-management");
  else if (log.type === "blotter") router.push("/blotter-kp-logs");
};

const viewAllSettings = () => {
  router.push({ path: "/system-settings", query: { tab: "audit" } });
};
</script>

<template>
  <div
    class="w-full bg-white rounded-[24px] p-6 shadow-sm border border-gray-100 flex flex-col overflow-hidden"
  >
    <div class="mb-4 flex items-start justify-between shrink-0">
      <div>
        <h2 class="text-xl font-bold text-gray-800 tracking-tight">
          Recent Activity
        </h2>
        <p
          class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1"
        >
          Audit Log
        </p>
      </div>
      <button
        @click="viewAllSettings"
        class="text-[11px] font-bold text-blue-600 uppercase tracking-widest hover:text-blue-800 transition-colors bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg"
      >
        View All
      </button>
    </div>

    <!-- max-height reduced to ~7 items; overflow scrolls the rest -->
    <div
      class="flex-1 min-h-0 pr-1 overflow-y-auto audit-scroll"
      style="max-height: 320px"
    >
      <div class="ml-2 border-l-2 border-gray-50 space-y-3 pb-2">
        <div
          v-if="displayedLogs.length === 0"
          class="text-sm text-gray-400 text-center mt-10"
        >
          No recent activity logs found.
        </div>
        <div
          v-for="log in displayedLogs"
          :key="log.id"
          @click="navigateToLog(log)"
          class="flex flex-col relative pl-6 cursor-pointer hover:bg-gray-50 py-2 -ml-1 pr-2 rounded-lg transition-colors group"
        >
          <div
            class="absolute -left-[6.5px] top-3 w-3.5 h-3.5 rounded-full border-2 border-white shadow-sm"
            :class="{
              'bg-[#D946EF]': log.type === 'doc',
              'bg-[#F59E0B]': log.type === 'equip',
              'bg-[#3B82F6]': log.type === 'resident',
              'bg-[#10B981]': log.type === 'blotter',
              'bg-gray-400': !['doc', 'equip', 'resident', 'blotter'].includes(
                log.type,
              ),
            }"
          ></div>
          <div class="flex justify-between items-start">
            <span
              class="text-sm font-bold text-gray-700 group-hover:text-blue-600 transition-colors"
              >{{ log.action }}</span
            >
            <span class="text-[10px] font-bold text-gray-400 uppercase">{{
              log.relativeTime
            }}</span>
          </div>
          <p
            class="text-[13px] text-gray-500 font-medium mt-0.5 leading-relaxed"
          >
            {{ log.detail }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-scroll::-webkit-scrollbar {
  width: 4px;
}
.audit-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.audit-scroll::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 99px;
}
.audit-scroll::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}
</style>