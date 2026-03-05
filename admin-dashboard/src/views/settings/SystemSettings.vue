<script setup>
/**
 * @file SystemSettings.vue
 * @description Main view for managing system-wide configurations, Audit Logs, and System Logs.
 */

import { ref, onMounted, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { NTabs, NTabPane, NButton, NAvatar, NSelect, useMessage } from "naive-ui";
import PageTitle from "@/components/shared/PageTitle.vue";

import { getAuditLogs } from "@/api/auditService";
import { getSystemLogs, getSystemLogSummary } from "@/api/systemLogsService";

const router = useRouter();
const route = useRoute();
const message = useMessage();

const searchQuery = ref("");
const activeTab = ref("general");
const brgyName = ref("Brgy. Poblacion Uno");

// ── Audit Logs ────────────────────────────────────────────────────────────────
const auditLogs = ref([]);
const isLoadingLogs = ref(false);

const loadAuditLogs = async () => {
  isLoadingLogs.value = true;
  try {
    const rawLogs = await getAuditLogs();
    const logsData = rawLogs.data || rawLogs || [];

    let mappedLogs = logsData.map((log) => {
      const logDate = new Date(log.created_at);
      return {
        id: log.id,
        action: log.action,
        details: log.details,
        rawDate: logDate,
        date: logDate.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
        time: logDate.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
        type: log.entity_type || "system",
      };
    });

    mappedLogs.sort((a, b) => b.rawDate - a.rawDate);
    auditLogs.value = mappedLogs;
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
    (log) =>
      log.action.toLowerCase().includes(q) ||
      log.details.toLowerCase().includes(q)
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

// Filters
const systemLogSource = ref(null);
const systemLogLevel = ref(null);
const systemLogCategory = ref(null);

const sourceOptions = [
  { label: "All Sources", value: null },
  { label: "Admin", value: "admin" },
  { label: "Kiosk", value: "kiosk" },
  { label: "System", value: "system" },
];

const levelOptions = [
  { label: "All Levels", value: null },
  { label: "Info", value: "info" },
  { label: "Warning", value: "warning" },
  { label: "Error", value: "error" },
  { label: "Critical", value: "critical" },
];

const categoryOptions = [
  { label: "All Categories", value: null },
  { label: "Auth", value: "auth" },
  { label: "Transaction", value: "transaction" },
  { label: "Resident", value: "resident" },
  { label: "Admin Action", value: "admin_action" },
  { label: "Equipment", value: "equipment" },
  { label: "Announcement", value: "announcement" },
  { label: "Blotter", value: "blotter" },
  { label: "System", value: "system" },
  { label: "Security", value: "security" },
];

const loadSystemLogs = async () => {
  isLoadingSystemLogs.value = true;
  try {
    const params = {
      page: systemLogPage.value,
      page_size: systemLogPageSize,
    };
    if (systemLogSearch.value) params.search = systemLogSearch.value;
    if (systemLogSource.value) params.source = systemLogSource.value;
    if (systemLogLevel.value) params.level = systemLogLevel.value;
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

// Level styles
const levelBadgeClass = (level) => {
  const map = {
    info: "bg-blue-50 text-blue-600 border border-blue-200",
    warning: "bg-amber-50 text-amber-600 border border-amber-200",
    error: "bg-red-50 text-red-600 border border-red-200",
    critical: "bg-red-100 text-red-700 border border-red-300 font-bold",
  };
  return map[level] || "bg-gray-100 text-gray-500 border border-gray-200";
};

const sourceDotClass = (source) => {
  const map = {
    admin: "bg-indigo-500",
    kiosk: "bg-teal-500",
    system: "bg-gray-400",
  };
  return map[source] || "bg-gray-300";
};

const summaryCardClass = (level) => {
  const map = {
    info: "border-blue-200 bg-blue-50",
    warning: "border-amber-200 bg-amber-50",
    error: "border-red-200 bg-red-50",
    critical: "border-red-300 bg-red-100",
  };
  return map[level] || "";
};

const summaryCountClass = (level) => {
  const map = {
    info: "text-blue-600",
    warning: "text-amber-600",
    error: "text-red-600",
    critical: "text-red-700",
  };
  return map[level] || "text-gray-600";
};

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(() => {
  loadAuditLogs();
  loadSystemLogSummary();

  watch(
    () => route.query.tab,
    (newTab) => {
      if (newTab === "audit") activeTab.value = "audit";
      if (newTab === "system-logs") {
        activeTab.value = "system-logs";
        loadSystemLogs();
      }
    },
    { immediate: true }
  );

  watch(activeTab, (val) => {
    if (val === "system-logs" && systemLogs.value.length === 0) {
      loadSystemLogs();
    }
  });
});

const handleUploadPhoto = () => message.success("Ready to upload a new photo.");
const handleRemovePhoto = () => message.error("Photo has been removed.");
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="System Settings" />
        <p class="text-sm text-gray-500 mt-1">
          Manage system-wide configurations and preferences
        </p>
      </div>

      <!-- Audit log search -->
      <div v-if="activeTab === 'audit'" class="flex items-center gap-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search audit logs..."
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />
      </div>

      <!-- System log search -->
      <div v-if="activeTab === 'system-logs'" class="flex items-center gap-3">
        <input
          v-model="systemLogSearch"
          @input="onSystemLogSearch"
          type="text"
          placeholder="Search system logs..."
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs v-model:value="activeTab" type="line" animated class="flex-grow">
        <n-tab-pane name="general" tab="General" />
        <n-tab-pane name="admin" tab="Admin" />
        <n-tab-pane name="backup" tab="Backup Data" />
        <n-tab-pane name="audit" tab="Audit Log" />
        <n-tab-pane name="system-logs" tab="System Logs" />
      </n-tabs>
    </div>

    <!-- Tab Content -->
    <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">

      <!-- General Tab -->
      <div v-if="activeTab === 'general'" class="flex flex-row justify-between w-full gap-16">
        <div class="flex flex-col w-1/2 gap-6">
          <span class="font-['Inter'] font-semibold text-[16px] text-[#373737]">Barangay Information</span>
          <div class="flex flex-col gap-2">
            <label class="font-['Inter'] font-medium text-[13px] text-[#757575]">Brgy. Name</label>
            <input
              v-model="brgyName"
              disabled
              class="bg-[#F8F8F8] border border-[#D9D9D9] font-['Inter'] font-medium text-[15px] text-gray-800 rounded-md px-3 py-2 outline-none cursor-default pointer-events-none w-full"
            />
          </div>
        </div>
        <div class="flex flex-col gap-6 items-end mr-12">
          <div class="flex flex-col w-[320px]">
            <span class="font-['Inter'] font-semibold text-[16px] text-[#373737] mb-6">Barangay Logo</span>
            <div class="flex flex-col items-center justify-center w-[320px] h-[320px] p-8 border border-gray-200 rounded-md bg-white">
              <n-avatar round :size="150"
                style="background: linear-gradient(135deg, #0066d4, #011784); color: white; font-size: 48px; font-weight: bold;"
                class="mb-6 ring-4 ring-blue-50 shadow-sm">
                PU
              </n-avatar>
              <span class="font-['Inter'] font-medium text-[13px] text-[#757575] mb-1">JPG, PNG. Max 2MB</span>
              <div class="flex flex-row gap-4 mt-1">
                <n-button ghost color="#0957FF" class="font-['Inter'] font-medium text-[15px] rounded-md" @click="handleUploadPhoto">Upload photo</n-button>
                <n-button ghost color="#FF2B3A" class="font-['Inter'] font-medium text-[15px] rounded-md" @click="handleRemovePhoto">Remove Photo</n-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Admin Tab -->
      <div v-if="activeTab === 'admin'" class="flex flex-col">
        <span class="text-sm text-gray-500">Admin settings content pending implementation.</span>
      </div>

      <!-- Backup Tab -->
      <div v-if="activeTab === 'backup'" class="flex flex-col">
        <span class="text-sm text-gray-500">Backup configuration content pending implementation.</span>
      </div>

      <!-- Audit Log Tab (unchanged) -->
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
                v-for="(log, index) in filteredLogs"
                :key="index"
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
                      'bg-gray-400': !['doc','equip','resident','blotter'].includes(log.type),
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

      <!-- System Logs Tab -->
      <div v-if="activeTab === 'system-logs'" class="flex flex-col w-full gap-5">

        <!-- Summary Cards -->
        <div class="grid grid-cols-4 gap-3">
          <div
            v-for="level in ['info', 'warning', 'error', 'critical']"
            :key="level"
            class="flex flex-col gap-1 rounded-lg border px-4 py-3"
            :class="summaryCardClass(level)"
          >
            <span class="text-[11px] font-semibold uppercase tracking-wider text-gray-500">{{ level }}</span>
            <span class="text-[24px] font-bold leading-none" :class="summaryCountClass(level)">
              {{ systemLogSummary.counts[level] ?? 0 }}
            </span>
            <span class="text-[11px] text-gray-400">today</span>
          </div>
        </div>

        <!-- Filters -->
        <div class="flex items-center gap-3 flex-wrap">
          <n-select
            v-model:value="systemLogSource"
            :options="sourceOptions"
            placeholder="Source"
            clearable
            size="small"
            style="width: 140px"
            @update:value="onSystemLogFilterChange"
          />
          <n-select
            v-model:value="systemLogLevel"
            :options="levelOptions"
            placeholder="Level"
            clearable
            size="small"
            style="width: 140px"
            @update:value="onSystemLogFilterChange"
          />
          <n-select
            v-model:value="systemLogCategory"
            :options="categoryOptions"
            placeholder="Category"
            clearable
            size="small"
            style="width: 160px"
            @update:value="onSystemLogFilterChange"
          />
          <span class="text-[12px] text-gray-400 ml-auto">
            {{ systemLogTotal }} total record{{ systemLogTotal !== 1 ? 's' : '' }}
          </span>
        </div>

        <!-- Loading -->
        <div v-if="isLoadingSystemLogs" class="py-12 flex justify-center items-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>

        <!-- Table -->
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
              <tr
                v-for="(log, index) in systemLogs"
                :key="index"
                class="border-b border-gray-100 last:border-none hover:bg-gray-50 transition-colors"
              >
                <!-- Date & Time -->
                <td class="py-4 px-4 whitespace-nowrap">
                  <span class="block text-[13px] text-gray-800 font-medium">{{ log.date }}</span>
                  <span class="block text-[11px] text-gray-400 mt-0.5">{{ log.time }}</span>
                </td>

                <!-- Level Badge -->
                <td class="py-4 px-4">
                  <span class="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize" :class="levelBadgeClass(log.level)">
                    {{ log.level }}
                  </span>
                </td>

                <!-- Source -->
                <td class="py-4 px-4">
                  <span class="inline-flex items-center gap-1.5 text-[13px] text-gray-700 capitalize">
                    <span class="w-2 h-2 rounded-full flex-shrink-0" :class="sourceDotClass(log.source)"></span>
                    {{ log.source }}
                  </span>
                </td>

                <!-- Category -->
                <td class="py-4 px-4">
                  <span class="text-[12px] text-gray-500 capitalize">{{ log.category?.replace('_', ' ') }}</span>
                </td>

                <!-- Action -->
                <td class="py-4 px-4 text-[13px] text-gray-800 max-w-[320px]">
                  <span class="line-clamp-2">{{ log.action }}</span>
                </td>

                <!-- Actor -->
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

        <!-- Pagination -->
        <div v-if="systemLogTotalPages > 1" class="flex items-center justify-end gap-2 pt-2">
          <button
            @click="systemLogPage--; loadSystemLogs()"
            :disabled="systemLogPage === 1"
            class="px-3 py-1.5 text-[13px] rounded-md border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>
          <span class="text-[13px] text-gray-500">
            Page {{ systemLogPage }} of {{ systemLogTotalPages }}
          </span>
          <button
            @click="systemLogPage++; loadSystemLogs()"
            :disabled="systemLogPage >= systemLogTotalPages"
            class="px-3 py-1.5 text-[13px] rounded-md border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Next
          </button>
        </div>

      </div>
      <!-- End System Logs Tab -->

    </div>
  </div>
</template>