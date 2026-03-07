<script setup>
/**
 * @file SystemSettings.vue
 * @description Main view for system-wide configuration.
 *   Tab components are split into separate files for maintainability.
 */

import { ref, onMounted, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { NTabs, NTabPane, useMessage } from "naive-ui";
import PageTitle from "@/components/shared/PageTitle.vue";

// Tab components
import General from "@/views/settings/system-settings/General.vue";
import AdminAccounts from "@/views/settings/system-settings/AdminAccounts.vue";
import Security from "@/views/settings/system-settings/Security.vue";
import Backup from "@/views/settings/system-settings/Backup.vue";
import SystemPreferences from "@/views/settings/system-settings/SystemPreferences.vue";
// import AuditLog from "@/views/settings/system-settings/AuditLog.vue";
// import SystemLogs from "@/views/settings/system-settings/SystemLogs.vue";

import { getAuditLogs } from "@/api/auditService";
import { getSystemLogs, getSystemLogSummary } from "@/api/systemLogsService";

const router = useRouter();
const route  = useRoute();
const message = useMessage();

const activeTab  = ref("general");
const searchQuery = ref("");

// ── Audit Logs ────────────────────────────────────────────────────────────────
const auditLogs      = ref([]);
const isLoadingLogs  = ref(false);

const loadAuditLogs = async () => {
  isLoadingLogs.value = true;
  try {
    const rawLogs = await getAuditLogs();
    const logsData = rawLogs.data || rawLogs || [];
    let mapped = logsData.map((log) => {
      const d = new Date(log.created_at);
      return {
        id: log.id,
        action: log.action,
        details: log.details,
        rawDate: d,
        date: d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
        time: d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
        type: log.entity_type || "system",
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
    (l) => l.action.toLowerCase().includes(q) || l.details.toLowerCase().includes(q)
  );
});

const navigateToLog = (log) => {
  if (log.type === "doc") router.push("/document-requests");
  else if (log.type === "equip") router.push("/equipment-requests");
  else if (log.type === "resident") router.push("/residents-management");
  else if (log.type === "blotter") router.push("/blotter-kp-logs");
};

// ── System Logs ───────────────────────────────────────────────────────────────
const systemLogs = ref([]);
const systemLogTotal = ref(0);
const systemLogPage = ref(1);
const systemLogPageSize = 20;
const isLoadingSystemLogs = ref(false);
const systemLogSearch = ref("");
const systemLogSummary = ref({ counts: { info: 0, warning: 0, error: 0, critical: 0 }, total_today: 0 });

const systemLogSource   = ref(null);
const systemLogLevel    = ref(null);
const systemLogCategory = ref(null);

const loadSystemLogs = async () => {
  isLoadingSystemLogs.value = true;
  try {
    const params = { page: systemLogPage.value, page_size: systemLogPageSize };
    if (systemLogSearch.value)   params.search   = systemLogSearch.value;
    if (systemLogSource.value)   params.source   = systemLogSource.value;
    if (systemLogLevel.value)    params.level    = systemLogLevel.value;
    if (systemLogCategory.value) params.category = systemLogCategory.value;

    const data = await getSystemLogs(params);
    systemLogs.value = (data.results || []).map((log) => {
      const d = new Date(log.created_at);
      return {
        ...log,
        date: d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
        time: d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
      };
    });
    systemLogTotal.value = data.total || 0;
  } catch (err) {
    console.error(err);
    message.error("Failed to load system logs.");
  } finally {
    isLoadingSystemLogs.value = false;
  }
};

const loadSystemLogSummary = async () => {
  systemLogSummary.value = await getSystemLogSummary();
};

const systemLogTotalPages = computed(() =>
  Math.ceil(systemLogTotal.value / systemLogPageSize)
);

const onSystemLogFilterChange = () => {
  systemLogPage.value = 1;
  loadSystemLogs();
};

let systemLogSearchTimer = null;
const onSystemLogSearch = () => {
  clearTimeout(systemLogSearchTimer);
  systemLogSearchTimer = setTimeout(() => {
    systemLogPage.value = 1;
    loadSystemLogs();
  }, 400);
};

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(() => {
  loadAuditLogs();
  loadSystemLogSummary();

  watch(
    () => route.query.tab,
    (newTab) => {
      if (newTab === "audit")        activeTab.value = "audit";
      if (newTab === "system-logs") {
        activeTab.value = "system-logs";
        loadSystemLogs();
      }
    },
    { immediate: true }
  );

  watch(activeTab, (val) => {
    if (val === "system-logs" && systemLogs.value.length === 0) loadSystemLogs();
  });
});
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">

    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="System Settings" />
        <p class="text-sm text-gray-500 mt-1">Manage system-wide configurations and preferences</p>
      </div>

      <!-- Contextual search inputs -->
      <div v-if="activeTab === 'audit'" class="flex items-center gap-3">
        <input
          v-model="searchQuery" type="text" placeholder="Search audit logs..."
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] text-[13px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition placeholder:text-gray-400"
        />
      </div>
      <div v-if="activeTab === 'system-logs'" class="flex items-center gap-3">
        <input
          v-model="systemLogSearch" @input="onSystemLogSearch" type="text" placeholder="Search system logs..."
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] text-[13px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition placeholder:text-gray-400"
        />
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs v-model:value="activeTab" type="line" animated class="flex-grow">
        <n-tab-pane name="general" tab="General" />
        <n-tab-pane name="admin" tab="Admin Accounts" />
        <n-tab-pane name="security" tab="Security" />
        <n-tab-pane name="backup" tab="Backup Data" />
        <n-tab-pane name="preferences" tab="Preferences" />
        <n-tab-pane name="audit" tab="Audit Log" />
        <n-tab-pane name="system-logs" tab="System Logs" />
      </n-tabs>
    </div>

    <!-- Tab Content -->
    <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">

      <General v-if="activeTab === 'general'" />
      <AdminAccounts v-if="activeTab === 'admin'" />
      <Security v-if="activeTab === 'security'" />
      <Backup v-if="activeTab === 'backup'" />
      <SystemPreferences v-if="activeTab === 'preferences'" />

      <!-- Audit Log (kept inline — uses shared state from parent) -->
      <div v-if="activeTab === 'audit'" class="flex flex-col w-full">
        <div v-if="isLoadingLogs" class="py-12 flex justify-center items-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
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

      <!-- System Logs (kept inline — uses shared state from parent) -->
      <div v-if="activeTab === 'system-logs'" class="flex flex-col w-full gap-5">
        <!-- Summary Cards -->
        <div class="grid grid-cols-4 gap-3">
          <div v-for="level in ['info','warning','error','critical']" :key="level"
            class="flex flex-col gap-1 rounded-lg border px-4 py-3"
            :class="{
              'border-blue-200 bg-blue-50':   level === 'info',
              'border-amber-200 bg-amber-50': level === 'warning',
              'border-red-200 bg-red-50':     level === 'error',
              'border-red-300 bg-red-100':    level === 'critical',
            }"
          >
            <span class="text-[11px] font-semibold uppercase tracking-wider text-gray-500">{{ level }}</span>
            <span class="text-[24px] font-bold leading-none"
              :class="{
                'text-blue-600':  level === 'info',
                'text-amber-600': level === 'warning',
                'text-red-600':   level === 'error',
                'text-red-700':   level === 'critical',
              }"
            >{{ systemLogSummary.counts[level] ?? 0 }}</span>
            <span class="text-[11px] text-gray-400">today</span>
          </div>
        </div>

        <!-- Filters -->
        <div class="flex items-center gap-3 flex-wrap">
          <n-select v-model:value="systemLogSource"   :options="[{ label:'All Sources', value:null },{ label:'Admin',value:'admin' },{ label:'Kiosk',value:'kiosk' },{ label:'System',value:'system' }]" placeholder="Source"   clearable size="small" style="width:140px" @update:value="onSystemLogFilterChange" />
          <n-select v-model:value="systemLogLevel"    :options="[{ label:'All Levels', value:null },{ label:'Info',value:'info' },{ label:'Warning',value:'warning' },{ label:'Error',value:'error' },{ label:'Critical',value:'critical' }]" placeholder="Level"    clearable size="small" style="width:140px" @update:value="onSystemLogFilterChange" />
          <n-select v-model:value="systemLogCategory" :options="[{ label:'All Categories', value:null },{ label:'Auth',value:'auth' },{ label:'Transaction',value:'transaction' },{ label:'Resident',value:'resident' },{ label:'Admin Action',value:'admin_action' },{ label:'Equipment',value:'equipment' },{ label:'Announcement',value:'announcement' },{ label:'Blotter',value:'blotter' },{ label:'System',value:'system' },{ label:'Security',value:'security' }]" placeholder="Category" clearable size="small" style="width:160px" @update:value="onSystemLogFilterChange" />
          <span class="text-[12px] text-gray-400 ml-auto">{{ systemLogTotal }} total record{{ systemLogTotal !== 1 ? 's' : '' }}</span>
        </div>

        <div v-if="isLoadingSystemLogs" class="py-12 flex justify-center items-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>

        <div v-else class="overflow-x-auto w-full">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-gray-200">
                <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[160px]">Date & Time</th>
                <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[80px]">Level</th>
                <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[90px]">Source</th>
                <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[110px]">Category</th>
                <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Action</th>
                <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[130px]">Actor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(log, index) in systemLogs" :key="index" class="border-b border-gray-100 last:border-none hover:bg-gray-50 transition-colors">
                <td class="py-4 px-4 whitespace-nowrap">
                  <span class="block text-[13px] text-gray-800 font-medium">{{ log.date }}</span>
                  <span class="block text-[11px] text-gray-400 mt-0.5">{{ log.time }}</span>
                </td>
                <td class="py-4 px-4">
                  <span class="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize"
                    :class="{
                      'bg-blue-50 text-blue-600 border border-blue-200':         log.level === 'info',
                      'bg-amber-50 text-amber-600 border border-amber-200':       log.level === 'warning',
                      'bg-red-50 text-red-600 border border-red-200':             log.level === 'error',
                      'bg-red-100 text-red-700 border border-red-300 font-bold':  log.level === 'critical',
                    }"
                  >{{ log.level }}</span>
                </td>
                <td class="py-4 px-4">
                  <span class="inline-flex items-center gap-1.5 text-[13px] text-gray-700 capitalize">
                    <span class="w-2 h-2 rounded-full flex-shrink-0"
                      :class="{ 'bg-indigo-500': log.source==='admin', 'bg-teal-500': log.source==='kiosk', 'bg-gray-400': log.source==='system' }"
                    ></span>
                    {{ log.source }}
                  </span>
                </td>
                <td class="py-4 px-4"><span class="text-[12px] text-gray-500 capitalize">{{ log.category?.replace('_',' ') }}</span></td>
                <td class="py-4 px-4 text-[13px] text-gray-800 max-w-[320px]"><span class="line-clamp-2">{{ log.action }}</span></td>
                <td class="py-4 px-4">
                  <span class="text-[13px] text-gray-700">{{ log.actor_name || '—' }}</span>
                  <span v-if="log.actor_role" class="block text-[11px] text-gray-400 capitalize">{{ log.actor_role }}</span>
                </td>
              </tr>
              <tr v-if="systemLogs.length === 0">
                <td colspan="6" class="py-8 text-center text-gray-500 text-sm">No system logs found.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="systemLogTotalPages > 1" class="flex items-center justify-end gap-2 pt-2">
          <button @click="systemLogPage--; loadSystemLogs()" :disabled="systemLogPage === 1"
            class="px-3 py-1.5 text-[13px] rounded-md border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
            Previous
          </button>
          <span class="text-[13px] text-gray-500">Page {{ systemLogPage }} of {{ systemLogTotalPages }}</span>
          <button @click="systemLogPage++; loadSystemLogs()" :disabled="systemLogPage >= systemLogTotalPages"
            class="px-3 py-1.5 text-[13px] rounded-md border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
            Next
          </button>
        </div>
      </div>

    </div>
  </div>
</template>