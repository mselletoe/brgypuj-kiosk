<script setup>
/**
 * @file Overview.vue
 * @description Parent wrapper for Dashboard Overview components.
 */
import { ref, shallowRef, onMounted } from "vue";
import OverviewHeader from "./components/OverviewHeader.vue";
import KpiCards from "./components/KpiCards.vue";
import VolumeChart from "./components/VolumeChart.vue";
import BreakdownChart from "./components/BreakdownChart.vue";
import AuditLog from "./components/AuditLog.vue";

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
    stats.value.activeBlotters = blottersData.filter((b) =>
      ["active", "pending"].includes(b.status?.toLowerCase()),
    ).length;

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
  <div class="flex flex-col w-full gap-8 animate-fade-in">
    <template v-if="!isLoading">
      <OverviewHeader :stats="stats" />

      <div class="flex flex-col xl:flex-row gap-6">
        <div class="flex-1 flex flex-col gap-6 w-full">
          <KpiCards :stats="stats" />

          <div
            class="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-[350px]"
          >
            <VolumeChart :docsList="rawDocsList" :equipsList="rawEquipsList" />
            <BreakdownChart
              :docsList="rawDocsList"
              :equipsList="rawEquipsList"
            />
          </div>
        </div>

        <AuditLog :auditLogs="auditLogs" />
      </div>
    </template>

    <div
      v-else
      class="flex-1 flex flex-col items-center justify-center min-h-[400px]"
    >
      <div
        class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"
      ></div>
    </div>
  </div>
</template>

<style scoped>
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
