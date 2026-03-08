<script setup>
import { ref, shallowRef, onMounted } from "vue";
import OverviewHeader from "./components/OverviewHeader.vue";
import KpiCards from "./components/KpiCards.vue";
import VolumeChart from "./components/VolumeChart.vue";
import BreakdownChart from "./components/BreakdownChart.vue";
import TopRequestedDocs from "./components/TopRequestedDocs.vue";
import TopRequestedEquip from "./components/TopRequestedEquip.vue";
import AuditLog from "./components/AuditLog.vue";
import QuickActions from "./components/QuickActions.vue";

import { fetchResidents } from "@/api/residentService";
import { getDocumentRequests } from "@/api/documentService";
import { getEquipmentRequests } from "@/api/equipmentService";
import { getAllBlotters } from "@/api/blotterService";
import { getAuditLogs } from "@/api/auditService";

const isLoading = ref(true);
const stats = ref({
  residents: 0,
  pendingDocs: 0,
  pendingEquip: 0,
  activeBlotters: 0,
});
const auditLogs = ref([]);
const rawDocsList = shallowRef([]);
const rawEquipsList = shallowRef([]);

const loadDashboardData = async () => {
  isLoading.value = true;
  try {
    const [residents, docs, equips, blotters, fetchedLogs] = await Promise.all([
      fetchResidents(),
      getDocumentRequests(),
      getEquipmentRequests(),
      getAllBlotters(),
      getAuditLogs(),
    ]);

    stats.value.residents = residents.data
      ? residents.data.length
      : residents.length || 0;
    const docsData = docs.data || docs || [];
    const equipsData = equips.data || equips || [];
    rawDocsList.value = docsData;
    rawEquipsList.value = equipsData;
    const blottersData = blotters.data || blotters || [];

    stats.value.pendingDocs = docsData.filter(
      (d) => d.status?.toLowerCase() === "pending",
    ).length;
    stats.value.pendingEquip = equipsData.filter(
      (e) => e.status?.toLowerCase() === "pending",
    ).length;
    stats.value.activeBlotters = blottersData.length;

    const rawLogs = fetchedLogs.data || fetchedLogs || [];
    let mappedLogs = rawLogs.map((log) => ({
      id: log.id,
      action: log.action,
      detail: log.details,
      date: new Date(log.created_at),
      type: log.entity_type || "system",
    }));
    mappedLogs.sort((a, b) => b.date - a.date);
    auditLogs.value = mappedLogs.slice(0, 15).map((log) => {
      const diffMins = Math.floor((new Date() - log.date) / 60000);
      const relativeTime =
        diffMins < 60
          ? `${diffMins}m ago`
          : diffMins < 1440
            ? `${Math.floor(diffMins / 60)}h ago`
            : `${Math.floor(diffMins / 1440)}d ago`;
      return { ...log, relativeTime };
    });
  } catch (err) {
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadDashboardData();
});
</script>

<template>
  <div
    class="flex flex-col w-full h-full gap-8 animate-fade-in overflow-x-clip"
  >
    <template v-if="!isLoading">
      <!-- Header -->
      <div class="section-row" style="animation-delay: 0s">
        <OverviewHeader :stats="stats" />
      </div>

      <!--
        Same outer structure as your original:
        flex-col xl:flex-row, left = flex-1, right sidebar = direct child.
        KPI cards are INSIDE the left column, same as original.
      -->
      <div class="flex flex-col xl:flex-row gap-6">
        <!-- LEFT column -->
        <div class="flex-1 flex flex-col gap-6">
          <!-- KPI Cards -->
          <div class="section-row" style="animation-delay: 0.08s">
            <KpiCards :stats="stats" />
          </div>

          <!-- Original charts row -->
          <div
            class="section-row grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[350px]"
            style="animation-delay: 0.16s"
          >
            <VolumeChart :docsList="rawDocsList" :equipsList="rawEquipsList" />
            <BreakdownChart
              :docsList="rawDocsList"
              :equipsList="rawEquipsList"
            />
          </div>

          <!-- New charts row — 2 equal columns -->
          <div
            class="section-row grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-[280px]"
            style="animation-delay: 0.24s"
          >
            <TopRequestedDocs :docsList="rawDocsList" />
            <TopRequestedEquip :equipsList="rawEquipsList" />
          </div>
        </div>

        <!-- RIGHT sidebar — direct flex child, same as original -->
        <div
          class="section-row-right w-full xl:w-1/4 shrink-0 flex flex-col gap-6"
          style="animation-delay: 0.2s"
        >
          <!-- AuditLog has its own fixed height (h-[480px] xl:h-[600px]) -->
          <AuditLog :auditLogs="auditLogs" />
          <QuickActions />
        </div>
      </div>
    </template>

    <div
      v-else
      class="flex flex-col items-center justify-center w-full h-[70vh] gap-4"
    >
      <div
        class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"
      ></div>
      <p class="text-gray-500 font-medium">Loading dashboard overview...</p>
    </div>
  </div>
</template>

<style scoped>
.section-row {
  opacity: 0;
  animation: sectionUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.section-row-right {
  opacity: 0;
  animation: sectionRight 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes sectionUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@keyframes sectionRight {
  from {
    opacity: 0;
    transform: translateX(24px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
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
