<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import { getAuditLogs } from "@/api/auditService";

const router  = useRouter();
const message = useMessage();

const auditLogs     = ref([]);
const isLoadingLogs = ref(false);
const searchQuery   = ref("");

const loadAuditLogs = async () => {
  isLoadingLogs.value = true;
  try {
    const rawLogs  = await getAuditLogs();
    const logsData = rawLogs.data || rawLogs || [];
    const mapped = logsData.map((log) => {
      const d = new Date(log.created_at);
      return {
        id:      log.id,
        action:  log.action,
        details: log.details,
        rawDate: d,
        date:    d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
        time:    d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
        type:    log.entity_type || "system",
      };
    });
    mapped.sort((a, b) => b.rawDate - a.rawDate);
    auditLogs.value = mapped;
  } catch (err) {
    console.error(err);
    message.error("Failed to load audit logs.");
  } finally {
    isLoadingLogs.value = false;
  }
};

const filteredLogs = computed(() => {
  if (!searchQuery.value) return auditLogs.value;
  const q = searchQuery.value.toLowerCase();
  return auditLogs.value.filter(
    (l) => l.action.toLowerCase().includes(q) || l.details?.toLowerCase().includes(q)
  );
});

const navigateToLog = (log) => {
  if      (log.type === "doc")      router.push("/document-requests");
  else if (log.type === "equip")    router.push("/equipment-requests");
  else if (log.type === "resident") router.push("/residents-management");
  else if (log.type === "blotter")  router.push("/blotter-kp-logs");
};

onMounted(() => {
  loadAuditLogs();
});
</script>

<template>
  <div class="flex flex-col w-full gap-4">

    <!-- Search -->
    <div class="flex justify-end">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search audit logs..."
        class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] text-[13px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition placeholder:text-gray-400"
      />
    </div>

    <!-- Loading -->
    <div v-if="isLoadingLogs" class="py-12 flex justify-center items-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto w-full">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="border-b border-gray-200">
            <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[25%]">Date & Time</th>
            <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[25%]">Action</th>
            <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[50%]">Details</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(log, index) in filteredLogs" :key="index"
            @click="navigateToLog(log)"
            class="border-b border-gray-100 last:border-none hover:bg-gray-50 transition-colors cursor-pointer group"
          >
            <td class="py-4 px-4 whitespace-nowrap flex flex-col">
              <span class="text-[13px] text-gray-800 font-medium group-hover:text-blue-600 transition-colors">{{ log.date }}</span>
              <span class="text-[11px] text-gray-400 mt-0.5">{{ log.time }}</span>
            </td>
            <td class="py-4 px-4 text-[13px] text-gray-800">
              <span class="inline-flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full" :class="{
                  'bg-[#D946EF]': log.type === 'doc',
                  'bg-[#F59E0B]': log.type === 'equip',
                  'bg-[#3B82F6]': log.type === 'resident',
                  'bg-[#10B981]': log.type === 'blotter',
                  'bg-gray-400':  !['doc','equip','resident','blotter'].includes(log.type),
                }"></span>
                {{ log.action }}
              </span>
            </td>
            <td class="py-4 px-4 text-[13px] text-gray-600">{{ log.details }}</td>
          </tr>
          <tr v-if="filteredLogs.length === 0">
            <td colspan="3" class="py-8 text-center text-gray-500 text-sm">No records found.</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>