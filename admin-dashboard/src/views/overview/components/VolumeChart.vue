<script setup>
import { ref, computed } from "vue";
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

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
);

const props = defineProps({
  docsList: { type: Array, required: true },
  equipsList: { type: Array, required: true },
});

const selectedTimeScale = ref("monthly");

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

    const todayStart = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
    );

    const processItem = (itemDateStr, countsArray) => {
      const d = new Date(itemDateStr);
      if (isNaN(d)) return;
      const itemStart = new Date(d.getFullYear(), d.getMonth(), d.getDate());
      const diffTime = todayStart.getTime() - itemStart.getTime();
      const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays >= 0 && diffDays < 7) {
        countsArray[6 - diffDays]++;
      }
    };

    props.docsList.forEach((d) =>
      processItem(d.created_at || d.requested_at, docCounts),
    );
    props.equipsList.forEach((e) =>
      processItem(e.requested_at || e.created_at, equipCounts),
    );
  } else if (selectedTimeScale.value === "this_month") {
    labels = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"];
    docCounts = Array(5).fill(0);
    equipCounts = Array(5).fill(0);

    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    const processItemMonth = (itemDateStr, countsArray) => {
      const d = new Date(itemDateStr);
      if (
        !isNaN(d) &&
        d.getMonth() === currentMonth &&
        d.getFullYear() === currentYear
      ) {
        const weekIndex = Math.min(Math.floor((d.getDate() - 1) / 7), 4);
        countsArray[weekIndex]++;
      }
    };

    props.docsList.forEach((d) =>
      processItemMonth(d.created_at || d.requested_at, docCounts),
    );
    props.equipsList.forEach((e) =>
      processItemMonth(e.requested_at || e.created_at, equipCounts),
    );
  } else if (selectedTimeScale.value === "monthly") {
    labels = [
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
    ];
    docCounts = Array(12).fill(0);
    equipCounts = Array(12).fill(0);
    const currentYear = now.getFullYear();

    props.docsList.forEach((d) => {
      const dDate = new Date(d.created_at || d.requested_at);
      if (!isNaN(dDate) && dDate.getFullYear() === currentYear) {
        docCounts[dDate.getMonth()]++;
      }
    });

    props.equipsList.forEach((e) => {
      const eDate = new Date(e.requested_at || e.created_at);
      if (!isNaN(eDate) && eDate.getFullYear() === currentYear) {
        equipCounts[eDate.getMonth()]++;
      }
    });
  } else if (selectedTimeScale.value === "yearly") {
    const currentYear = now.getFullYear();
    labels = [
      currentYear - 4,
      currentYear - 3,
      currentYear - 2,
      currentYear - 1,
      currentYear,
    ].map(String);
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
    labels: labels,
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
    class="lg:col-span-2 bg-white rounded-[24px] p-8 shadow-sm border border-gray-100 flex flex-col h-full"
  >
    <div class="mb-8 px-1 flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-800 tracking-tight">
          Request Volume
        </h2>
        <p
          class="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1"
        >
          Transaction Trends
        </p>
      </div>

      <select
        v-model="selectedTimeScale"
        class="text-[11px] font-bold text-gray-500 uppercase tracking-widest bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer transition-colors hover:bg-gray-100 hover:text-gray-700 w-auto"
      >
        <option value="weekly">Last 7 Days</option>
        <option value="this_month">This Month</option>
        <option value="monthly">This Year</option>
        <option value="yearly">Last 5 Years</option>
      </select>
    </div>

    <div class="flex-1 w-full px-1 relative">
      <div class="absolute inset-0">
        <Bar :data="chartData" :options="chartOptions" />
      </div>
    </div>
  </div>
</template>
