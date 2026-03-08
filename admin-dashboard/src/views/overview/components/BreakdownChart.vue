<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
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

// --- Custom Dropdown Logic ---
const isDropdownOpen = ref(false);
const dropdownRef = ref(null);

const dropdownOptions = [
  { value: "documents", label: "By Document Type" },
  { value: "equipment", label: "By Equipment Type" },
];

const selectedDropdownLabel = computed(() => {
  return dropdownOptions.find((opt) => opt.value === selectedDoughnutView.value)
    ?.label;
});

const selectOption = (value) => {
  selectedDoughnutView.value = value;
  isDropdownOpen.value = false;
};

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isDropdownOpen.value = false;
  }
};

onMounted(() => document.addEventListener("click", handleClickOutside));
onBeforeUnmount(() =>
  document.removeEventListener("click", handleClickOutside),
);
// ------------------------------

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

      <div class="relative mt-3" ref="dropdownRef">
        <button
          @click="isDropdownOpen = !isDropdownOpen"
          class="flex items-center gap-2 text-[11px] font-bold text-gray-500 uppercase tracking-widest bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer transition-colors hover:bg-gray-100 hover:text-gray-700 w-auto"
        >
          {{ selectedDropdownLabel }}
          <svg
            class="w-3.5 h-3.5 transition-transform duration-200"
            :class="isDropdownOpen ? 'rotate-180' : ''"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            ></path>
          </svg>
        </button>

        <Transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-95"
        >
          <div
            v-if="isDropdownOpen"
            class="absolute z-50 left-1/2 -translate-x-1/2 mt-2 w-48 rounded-xl bg-white shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] ring-1 ring-black ring-opacity-5 focus:outline-none overflow-hidden"
          >
            <div class="py-1">
              <button
                v-for="option in dropdownOptions"
                :key="option.value"
                @click="selectOption(option.value)"
                class="block w-full text-left px-4 py-2.5 text-[11px] font-bold uppercase tracking-widest transition-colors"
                :class="
                  option.value === selectedDoughnutView
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                "
              >
                {{ option.label }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <div class="flex-1 w-full relative mt-2">
      <div class="absolute inset-0 pb-4">
        <Doughnut :data="doughnutChartData" :options="doughnutChartOptions" />
      </div>
    </div>
  </div>
</template>
