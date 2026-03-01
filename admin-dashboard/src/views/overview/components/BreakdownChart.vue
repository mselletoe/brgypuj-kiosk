<script setup>
import { ref, computed } from "vue";
import { Doughnut } from "vue-chartjs";
import { Chart as ChartJS, Tooltip, Legend, ArcElement } from "chart.js";

ChartJS.register(Tooltip, Legend, ArcElement);

const props = defineProps({
  docsList: { type: Array, required: true },
  equipsList: { type: Array, required: true },
});

const selectedDoughnutView = ref("documents");
const chartColors = [
  "#8B5CF6",
  "#EC4899",
  "#3B82F6",
  "#10B981",
  "#F59E0B",
  "#14B8A6",
  "#F43F5E",
];

const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: "75%",
  plugins: {
    legend: {
      position: "bottom",
      labels: {
        usePointStyle: true,
        boxWidth: 8,
        padding: 20,
        font: { size: 12 },
      },
    },
  },
};

const rawDocCounts = computed(() => {
  const docTypesCount = {};
  props.docsList.forEach((d) => {
    const docName = d.doctype_name || "Other";
    docTypesCount[docName] = (docTypesCount[docName] || 0) + 1;
  });
  return {
    labels: Object.keys(docTypesCount),
    data: Object.values(docTypesCount),
  };
});

const rawEquipCounts = computed(() => {
  const equipTypesCount = {};
  props.equipsList.forEach((e) => {
    if (e.items && e.items.length > 0) {
      e.items.forEach((item) => {
        const itemName = item.item_name || "Unknown Item";
        equipTypesCount[itemName] =
          (equipTypesCount[itemName] || 0) + item.quantity;
      });
    }
  });
  return {
    labels: Object.keys(equipTypesCount),
    data: Object.values(equipTypesCount),
  };
});

const doughnutChartData = computed(() => {
  const isDoc = selectedDoughnutView.value === "documents";
  const targetData = isDoc ? rawDocCounts.value : rawEquipCounts.value;

  // Swapped back to Array.of() to clear the expression error!
  let finalLabels = Array.of("No Data");
  let finalData = Array.of(1);
  let finalColors = Array.of("#f3f4f6");

  if (targetData.labels && targetData.labels.length > 0) {
    finalLabels = targetData.labels;
    finalData = targetData.data;
    finalColors = chartColors.slice(0, targetData.labels.length);
  }

  return {
    labels: finalLabels,
    datasets: Array.of({
      data: finalData,
      backgroundColor: finalColors,
      borderWidth: 0,
      hoverOffset: 6,
    }),
  };
});
</script>

<template>
  <div
    class="lg:col-span-1 bg-white rounded-[24px] p-8 shadow-sm border border-gray-100 flex flex-col h-full"
  >
    <div class="mb-6 px-1 flex flex-col items-center text-center">
      <h2 class="text-xl font-bold text-gray-800 tracking-tight">
        Requests Breakdown
      </h2>
      <select
        v-model="selectedDoughnutView"
        class="mt-3 text-[11px] font-bold text-gray-500 uppercase tracking-widest bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer transition-colors hover:bg-gray-100 hover:text-gray-700 w-auto"
      >
        <option value="documents">By Document Type</option>
        <option value="equipment">By Equipment Type</option>
      </select>
    </div>
    <div class="flex-1 w-full relative mt-2">
      <div class="absolute inset-0 pb-4">
        <Doughnut :data="doughnutChartData" :options="doughnutChartOptions" />
      </div>
    </div>
  </div>
</template>
