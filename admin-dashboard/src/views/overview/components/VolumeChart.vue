<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
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

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const props = defineProps({
  docsList: { type: Array, required: true },
  equipsList: { type: Array, required: true },
});

const selectedTimeScale = ref("monthly");
const barRef = ref(null);
const chartContainerRef = ref(null);
let resizeObserver = null;

// --- Custom Dropdown Logic ---
const isDropdownOpen = ref(false);
const dropdownRef = ref(null);

const dropdownOptions = [
  { value: "weekly", label: "Last 7 Days" },
  { value: "this_month", label: "This Month" },
  { value: "monthly", label: "This Year" },
  { value: "yearly", label: "Last 5 Years" },
];

const selectedDropdownLabel = computed(() => {
  return dropdownOptions.find((opt) => opt.value === selectedTimeScale.value)?.label;
});

const selectOption = (value) => {
  selectedTimeScale.value = value;
  isDropdownOpen.value = false;
};

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isDropdownOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);

  // Watch container size and force chart to resize with it
  if (chartContainerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      const chartInstance = barRef.value?.chart;
      if (chartInstance) {
        chartInstance.resize();
      }
    });
    resizeObserver.observe(chartContainerRef.value);
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
});
// ------------------------------

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "top",
      labels: {
        usePointStyle: true,
        boxWidth: 10,
        font: { weight: "600" },
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      border: { display: false },
      grid: { color: "#f3f4f6" },
      ticks: {
        font: { precision: 0 },
        stepSize: 1,
      },
    },
    x: { grid: { display: false } },
  },
};

const chartData = computed(() => {
  const now = new Date();
  let labels = [];
  let docCounts = [];
  let equipCounts = [];

  if (selectedTimeScale.value === "weekly") {
    labels = Array(7).fill("");
    docCounts = Array(7).fill(0);
    equipCounts = Array(7).fill(0);

    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(now.getDate() - i);
      labels[6 - i] = d.toLocaleDateString("en-US", { weekday: "short" });
    }

    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    const processItem = (itemDateStr, countsArray) => {
      const d = new Date(itemDateStr);
      if (isNaN(d)) return;
      const itemStart = new Date(d.getFullYear(), d.getMonth(), d.getDate());
      const diffTime = todayStart.getTime() - itemStart.getTime();
      const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
      if (diffDays >= 0 && diffDays < 7) countsArray[6 - diffDays]++;
    };

    props.docsList.forEach((d) => processItem(d.created_at || d.requested_at, docCounts));
    props.equipsList.forEach((e) => processItem(e.requested_at || e.created_at, equipCounts));
  } else if (selectedTimeScale.value === "this_month") {
    labels = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"];
    docCounts = Array(5).fill(0);
    equipCounts = Array(5).fill(0);

    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    const processItemMonth = (itemDateStr, countsArray) => {
      const d = new Date(itemDateStr);
      if (!isNaN(d) && d.getMonth() === currentMonth && d.getFullYear() === currentYear) {
        const weekIndex = Math.min(Math.floor((d.getDate() - 1) / 7), 4);
        countsArray[weekIndex]++;
      }
    };

    props.docsList.forEach((d) => processItemMonth(d.created_at || d.requested_at, docCounts));
    props.equipsList.forEach((e) => processItemMonth(e.requested_at || e.created_at, equipCounts));
  } else if (selectedTimeScale.value === "monthly") {
    labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    docCounts = Array(12).fill(0);
    equipCounts = Array(12).fill(0);
    const currentYear = now.getFullYear();

    props.docsList.forEach((d) => {
      const dDate = new Date(d.created_at || d.requested_at);
      if (!isNaN(dDate) && dDate.getFullYear() === currentYear) docCounts[dDate.getMonth()]++;
    });
    props.equipsList.forEach((e) => {
      const eDate = new Date(e.requested_at || e.created_at);
      if (!isNaN(eDate) && eDate.getFullYear() === currentYear) equipCounts[eDate.getMonth()]++;
    });
  } else if (selectedTimeScale.value === "yearly") {
    const currentYear = now.getFullYear();
    labels = [currentYear - 4, currentYear - 3, currentYear - 2, currentYear - 1, currentYear].map(String);
    docCounts = Array(5).fill(0);
    equipCounts = Array(5).fill(0);

    props.docsList.forEach((d) => {
      const dDate = new Date(d.created_at || d.requested_at);
      if (!isNaN(dDate)) {
        const yearDiff = currentYear - dDate.getFullYear();
        if (yearDiff >= 0 && yearDiff < 5) docCounts[4 - yearDiff]++;
      }
    });
    props.equipsList.forEach((e) => {
      const eDate = new Date(e.requested_at || e.created_at);
      if (!isNaN(eDate)) {
        const yearDiff = currentYear - eDate.getFullYear();
        if (yearDiff >= 0 && yearDiff < 5) equipCounts[4 - yearDiff]++;
      }
    });
  }

  return {
    labels,
    datasets: [
      {
        label: "Documents",
        backgroundColor: "#D946EF",
        data: docCounts,
        borderRadius: 6,
        barPercentage: 0.6,
      },
      {
        label: "Equipment",
        backgroundColor: "#F59E0B",
        data: equipCounts,
        borderRadius: 6,
        barPercentage: 0.6,
      },
    ],
  };
});
</script>

<template>
  <div
    class="lg:col-span-2 bg-white rounded-[24px] p-6 shadow-sm border border-gray-100 flex flex-col"
  >
    <div class="mb-6 px-1 flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-800 tracking-tight">Request Volume</h2>
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1">
          Transaction Trends
        </p>
      </div>

      <div class="relative" ref="dropdownRef">
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
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
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
            class="absolute right-0 z-50 mt-2 w-44 origin-top-right rounded-xl bg-white shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] ring-1 ring-black ring-opacity-5 overflow-hidden"
          >
            <div class="py-1">
              <button
                v-for="option in dropdownOptions"
                :key="option.value"
                @click="selectOption(option.value)"
                class="block w-full text-left px-4 py-2.5 text-[11px] font-bold uppercase tracking-widest transition-colors"
                :class="option.value === selectedTimeScale ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Container observed by ResizeObserver; fixed height keeps the chart practical -->
    <div ref="chartContainerRef" class="w-full" style="height: 260px; position: relative;">
      <Bar ref="barRef" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>