<script setup>
/**
 * @file Overview.vue
 * @description KPI cards with a smooth "liquid retract" transition for the color strips.
 */
import { ref, shallowRef, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";

import { fetchResidents } from "@/api/residentService";
import { getDocumentRequests } from "@/api/documentService";
import { getEquipmentRequests } from "@/api/equipmentService";
import { getAllBlotters } from "@/api/blotterService";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
);

const router = useRouter();

const isLoading = ref(true);
const bannerVisible = ref(false);
const timeInterval = ref(null);
const currentDate = ref("");
const greeting = ref("");

const stats = ref({
  residents: 0,
  pendingDocs: 0,
  pendingEquip: 0,
  activeBlotters: 0,
});

const auditLogs = ref([]);

const chartData = shallowRef({
  labels: [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ],
  datasets: [
    {
      label: "Documents",
      backgroundColor: "#3B82F6",
      data: Array(12).fill(0),
      borderRadius: 6,
      barPercentage: 0.6,
    },
    {
      label: "Equipment",
      backgroundColor: "#10B981",
      data: Array(12).fill(0),
      borderRadius: 6,
      barPercentage: 0.6,
    },
  ],
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "top",
      labels: {
        usePointStyle: true,
        boxWidth: 10,
        font: { weight: "600", family: "Inter" },
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      border: { display: false },
      grid: { color: "#f3f4f6" },
      ticks: { font: { family: "Inter" } },
    },
    x: { grid: { display: false }, ticks: { font: { family: "Inter" } } },
  },
};

const hasPendingActions = computed(
  () => stats.value.pendingDocs > 0 || stats.value.pendingEquip > 0,
);

const updateClock = () => {
  const now = new Date();
  currentDate.value = now.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
  const hour = now.getHours();
  if (hour < 12) greeting.value = "Good Morning";
  else if (hour < 18) greeting.value = "Good Afternoon";
  else greeting.value = "Good Evening";
};

const loadDashboardData = async () => {
  isLoading.value = true;
  try {
    const [residents, docs, equips, blotters] = await Promise.all([
      fetchResidents(),
      getDocumentRequests(),
      getEquipmentRequests(),
      getAllBlotters(),
    ]);

    stats.value.residents = residents.data
      ? residents.data.length
      : residents.length || 0;
    const docsData = docs.data || docs || [];
    const equipsData = equips.data || equips || [];
    const blottersData = blotters.data || blotters || [];

    stats.value.pendingDocs = docsData.filter(
      (d) => d.status?.toLowerCase() === "pending",
    ).length;
    stats.value.pendingEquip = equipsData.filter(
      (e) => e.status?.toLowerCase() === "pending",
    ).length;
    stats.value.activeBlotters = blottersData.filter((b) =>
      ["active", "pending"].includes(b.status?.toLowerCase()),
    ).length;

    let logs = [];
    docsData.forEach((d) =>
      logs.push({
        id: `doc-${d.id}`,
        action: "Document Request",
        detail: d.doctype_name || "New request.",
        date: new Date(d.created_at),
        type: "doc",
      }),
    );
    equipsData.forEach((e) =>
      logs.push({
        id: `eq-${e.id}`,
        action: "Equipment Request",
        detail: e.equipment_name || "Borrow request.",
        date: new Date(e.created_at),
        type: "equip",
      }),
    );
    logs.sort((a, b) => b.date - a.date);

    auditLogs.value = logs.slice(0, 15).map((log) => {
      const diffMins = Math.floor((new Date() - log.date) / 60000);
      const relativeTime =
        diffMins < 60
          ? `${diffMins}m ago`
          : diffMins < 1440
            ? `${Math.floor(diffMins / 60)}h ago`
            : `${Math.floor(diffMins / 1440)}d ago`;
      return {
        ...log,
        relativeTime,
        displayDate: log.date.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
    });

    const docCounts = Array(12).fill(0);
    const equipCounts = Array(12).fill(0);
    docsData.forEach((d) => {
      docCounts[new Date(d.created_at).getMonth()]++;
    });
    equipsData.forEach((e) => {
      equipCounts[new Date(e.created_at).getMonth()]++;
    });

    chartData.value = {
      labels: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ],
      datasets: [
        {
          label: "Documents",
          backgroundColor: "#3B82F6",
          data: docCounts,
          borderRadius: 6,
          barPercentage: 0.6,
        },
        {
          label: "Equipment",
          backgroundColor: "#10B981",
          data: equipCounts,
          borderRadius: 6,
          barPercentage: 0.6,
        },
      ],
    };

    if (stats.value.pendingDocs > 0 || stats.value.pendingEquip > 0) {
      setTimeout(() => {
        bannerVisible.value = true;
      }, 300);
    }
  } catch (err) {
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  updateClock();
  timeInterval.value = setInterval(updateClock, 60000);
  loadDashboardData();
});
onUnmounted(() => clearInterval(timeInterval.value));
</script>

<template>
  <div class="flex flex-col w-full gap-8 animate-fade-in font-inter">
    <!-- Header row -->
    <div v-if="!isLoading" class="flex items-center justify-between gap-6 px-1">
      <div class="flex flex-col gap-1">
        <h1
          class="text-[32px] font-bold text-gray-800 tracking-tight leading-tight"
        >
          {{ greeting }}, <span class="text-blue-600">Admin</span>
        </h1>
        <p
          class="text-[14px] font-semibold text-gray-400 tracking-wide uppercase"
        >
          System Overview &bull; {{ currentDate }}
        </p>
      </div>

      <div
        v-if="hasPendingActions"
        class="banner-wrap"
        :class="bannerVisible ? 'banner-visible' : 'banner-hidden'"
      >
        <div
          class="bg-amber-50 border-l-4 border-amber-500 px-5 py-3 rounded-r-xl shadow-sm flex items-center gap-4 group"
        >
          <svg
            class="w-5 h-5 text-amber-500 shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <div>
            <h3 class="text-amber-800 font-bold text-sm">Action Required</h3>
            <p class="text-amber-700 text-xs mt-0.5">
              <span v-if="stats.pendingDocs > 0" class="font-bold"
                >{{ stats.pendingDocs }} pending doc{{
                  stats.pendingDocs > 1 ? "s" : ""
                }}</span
              >
              <span v-if="stats.pendingDocs > 0 && stats.pendingEquip > 0">
                &amp;
              </span>
              <span v-if="stats.pendingEquip > 0" class="font-bold"
                >{{ stats.pendingEquip }} equipment request{{
                  stats.pendingEquip > 1 ? "s" : ""
                }}</span
              >
              need your attention.
            </p>
          </div>
          <div class="banner-buttons">
            <button
              v-if="stats.pendingDocs > 0"
              @click="router.push('/document-requests')"
              class="px-3 py-1.5 bg-white text-amber-700 font-semibold text-xs rounded-lg shadow-sm border border-amber-200 hover:bg-amber-100 transition whitespace-nowrap"
            >
              Review Docs
            </button>
            <button
              v-if="stats.pendingEquip > 0"
              @click="router.push('/equipment-requests')"
              class="px-3 py-1.5 bg-white text-amber-700 font-semibold text-xs rounded-lg shadow-sm border border-amber-200 hover:bg-amber-100 transition whitespace-nowrap"
            >
              Review Equipment
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div
      v-if="!isLoading"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
    >
      <!-- Residents -->
      <div @click="router.push('/residents-management')" class="kpi-card group">
        <div
          class="color-strip bg-gradient-to-r from-[#FFFFFF] to-[#CBFCFF]"
        ></div>
        <div class="relative z-10 flex flex-col h-full">
          <div class="flex items-center justify-between mb-4">
            <span class="kpi-label">Residents</span>
            <div class="kpi-icon text-cyan-500">
              <svg
                class="w-11 h-11"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
          </div>
          <span class="kpi-value">{{ stats.residents }}</span>
          <span class="kpi-title">Registered Residents</span>
          <span class="kpi-subtext">In the barangay database</span>
        </div>
      </div>

      <!-- Documents -->
      <div @click="router.push('/document-requests')" class="kpi-card group">
        <div
          class="color-strip bg-gradient-to-r from-[#FFFFFF] to-[#FCD6FF]"
        ></div>
        <div class="relative z-10 flex flex-col h-full">
          <div class="flex items-center justify-between mb-4">
            <span class="kpi-label">Documents</span>
            <div class="kpi-icon text-purple-400">
              <svg
                class="w-11 h-11"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
          </div>
          <span class="kpi-value">{{ stats.pendingDocs }}</span>
          <span class="kpi-title">Document Requests</span>
          <span class="kpi-subtext">Awaiting your approval</span>
        </div>
      </div>

      <!-- Equipment -->
      <div @click="router.push('/equipment-requests')" class="kpi-card group">
        <div
          class="color-strip bg-gradient-to-r from-[#FFFFFF] to-[#FFF5D3]"
        ></div>
        <div class="relative z-10 flex flex-col h-full">
          <div class="flex items-center justify-between mb-4">
            <span class="kpi-label">Equipment</span>
            <div class="kpi-icon text-yellow-500">
              <svg
                class="w-11 h-11"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
              </svg>
            </div>
          </div>
          <span class="kpi-value">{{ stats.pendingEquip }}</span>
          <span class="kpi-title">Equipment Borrowed</span>
          <span class="kpi-subtext">Active borrow requests</span>
        </div>
      </div>

      <!-- Blotters -->
      <div @click="router.push('/blotter-kp-logs')" class="kpi-card group">
        <div
          class="color-strip bg-gradient-to-r from-[#FFFFFF] to-[#B6FFC2]"
        ></div>
        <div class="relative z-10 flex flex-col h-full">
          <div class="flex items-center justify-between mb-4">
            <span class="kpi-label">Blotters</span>
            <div class="kpi-icon text-green-500">
              <svg
                class="w-11 h-11"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.5"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
          </div>
          <span class="kpi-value">{{ stats.activeBlotters }}</span>
          <span class="kpi-title">Blotter Cases</span>
          <span class="kpi-subtext">Active &amp; unresolved cases</span>
        </div>
      </div>
    </div>

    <!-- Charts + Audit -->
    <div v-if="!isLoading" class="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
      <div
        class="lg:col-span-2 bg-white rounded-[24px] p-8 shadow-sm border border-gray-100 flex flex-col"
      >
        <div class="mb-8 px-1">
          <h2 class="text-xl font-bold text-gray-800 tracking-tight">
            System Volume
          </h2>
          <p
            class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1"
          >
            Monthly Statistics
          </p>
        </div>
        <div class="flex-1 min-h-[320px] w-full px-1">
          <Bar :data="chartData" :options="chartOptions" />
        </div>
      </div>

      <div
        class="bg-white rounded-[24px] p-8 shadow-sm border border-gray-100 flex flex-col h-[500px]"
      >
        <div class="mb-8">
          <h2 class="text-xl font-bold text-gray-800 tracking-tight">
            Recent Activity
          </h2>
          <p
            class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1"
          >
            Audit Trail
          </p>
        </div>
        <div class="flex-1 overflow-y-auto custom-scrollbar px-4">
          <div class="ml-2 border-l-2 border-gray-50 space-y-6 pb-4">
            <div
              v-for="log in auditLogs"
              :key="log.id"
              class="flex flex-col relative pl-6"
            >
              <div
                class="absolute -left-[7.5px] top-1 w-3.5 h-3.5 rounded-full border-2 border-white shadow-sm"
                :class="log.type === 'doc' ? 'bg-blue-500' : 'bg-emerald-500'"
              ></div>
              <div class="flex justify-between items-start">
                <span class="text-sm font-bold text-gray-700">{{
                  log.action
                }}</span>
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
    </div>

    <!-- Loading -->
    <div
      v-if="isLoading"
      class="flex-1 flex flex-col items-center justify-center min-h-[400px]"
    >
      <div
        class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"
      ></div>
    </div>
  </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap");

.font-inter {
  font-family: "Inter", sans-serif;
}

/* ==================================
   BANNER
   ================================== */
.banner-wrap {
  transition:
    opacity 0.5s ease,
    transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.banner-hidden {
  opacity: 0;
  transform: translateX(40px);
  pointer-events: none;
}
.banner-visible {
  opacity: 1;
  transform: translateX(0);
  pointer-events: auto;
}

.banner-buttons {
  display: flex;
  gap: 8px;
  overflow: hidden;
  max-width: 0;
  opacity: 0;
  transition:
    max-width 0.4s cubic-bezier(0.16, 1, 0.3, 1),
    opacity 0.3s ease;
}
.group:hover .banner-buttons {
  max-width: 300px;
  opacity: 1;
}

/* ==================================
   KPI CARDS
   ================================== */
.kpi-card {
  @apply bg-white rounded-[20px] p-6 border border-gray-100 shadow-sm flex flex-col cursor-pointer relative overflow-hidden;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.kpi-card:hover {
  @apply shadow-lg border-transparent;
  transform: translateY(-4px);
}

.color-strip {
  @apply absolute right-0 top-0 h-full w-[15px] z-0;
  background-attachment: fixed;
  transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.kpi-card:hover .color-strip {
  @apply w-full;
}

.kpi-label {
  @apply text-[13px] font-black text-gray-400 uppercase tracking-widest;
}

.kpi-icon {
  @apply flex items-center justify-center transition-all duration-500;
}
.kpi-icon svg {
  transition: filter 0.2s ease;
}
.kpi-card:hover .kpi-icon {
  transform: scale(1.1);
}
.kpi-card:hover .kpi-icon svg {
  filter: brightness(0) invert(1) drop-shadow(0 2px 8px rgba(0, 0, 0, 0.5));
}

.kpi-value {
  @apply text-[42px] font-black text-gray-800 leading-none tracking-tighter;
}

.kpi-title {
  @apply text-[18px] font-bold text-gray-600 mt-2;
}

.kpi-subtext {
  @apply text-[12px] font-medium text-gray-400 mt-0 italic;
}

/* ==================================
   SCROLLBAR
   ================================== */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #f1f1f1;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #e2e8f0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}
</style>
