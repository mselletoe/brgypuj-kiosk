<script setup>
/**
 * @file Finance.vue
 * @description Financial statement export tab for System Settings.
 * Accessible by all admin roles (Admin & Superadmin).
 * Drop into: @/views/settings/system-settings/FinancialStatement.vue
 */

import { ref, computed } from "vue";
import { NDatePicker, useMessage } from "naive-ui";
import { exportFinancialStatement } from "@/api/financeService";

const message = useMessage();

// ── State ─────────────────────────────────────────────────────────────────────
const dateRange    = ref(null);   // [startMs, endMs] — Naive UI daterange format
const service      = ref(null);   // null | "documents" | "id_services" | "equipment"
const isExporting  = ref(false);
const lastExported = ref(null);
const exportError  = ref(null);

// ── Service options ───────────────────────────────────────────────────────────
const serviceOptions = [
  { label: "All Services",        value: null,          dot: "bg-blue-500"   },
  { label: "Document Services",   value: "documents",   dot: "bg-purple-500" },
  { label: "I.D Services",        value: "id_services", dot: "bg-teal-500"   },
  { label: "Equipment Borrowing", value: "equipment",   dot: "bg-amber-500"  },
];

// ── Computed ──────────────────────────────────────────────────────────────────
const canExport = computed(() =>
  dateRange.value?.[0] && dateRange.value?.[1]
);

const serviceLabel = computed(() =>
  serviceOptions.find(o => o.value === service.value)?.label ?? "All Services"
);

const previewFrom = computed(() =>
  dateRange.value?.[0]
    ? new Date(dateRange.value[0]).toLocaleDateString("en-PH", { year: "numeric", month: "long", day: "numeric" })
    : "—"
);

const previewTo = computed(() =>
  dateRange.value?.[1]
    ? new Date(dateRange.value[1]).toLocaleDateString("en-PH", { year: "numeric", month: "long", day: "numeric" })
    : "—"
);

// ── Date presets ──────────────────────────────────────────────────────────────
const presets = [
  { label: "This Month",   key: "this_month"   },
  { label: "Last Month",   key: "last_month"   },
  { label: "This Quarter", key: "this_quarter" },
  { label: "This Year",    key: "this_year"    },
];

function applyPreset(key) {
  const now = new Date();
  const y   = now.getFullYear();
  const m   = now.getMonth();
  const ms  = (d) => d.getTime();

  const map = {
    this_month:   [new Date(y, m, 1),                        new Date(y, m + 1, 0)              ],
    last_month:   [new Date(y, m - 1, 1),                    new Date(y, m, 0)                  ],
    this_quarter: [new Date(y, Math.floor(m / 3) * 3, 1),    new Date(y, Math.floor(m / 3) * 3 + 3, 0)],
    this_year:    [new Date(y, 0, 1),                        new Date(y, 11, 31)                ],
  };

  const [start, end] = map[key];
  dateRange.value = [ms(start), ms(end)];
}

// ── Export ────────────────────────────────────────────────────────────────────
async function handleExport() {
  if (!canExport.value || isExporting.value) return;

  isExporting.value = true;
  exportError.value = null;

  try {
    const toISO = (ms) => {
      const d = new Date(ms);
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    };

    await exportFinancialStatement({
      dateFrom: toISO(dateRange.value[0]),
      dateTo:   toISO(dateRange.value[1]),
      service:  service.value,
    });

    lastExported.value = new Date().toLocaleString("en-PH");
    message.success("Financial statement downloaded successfully.");
  } catch (err) {
    console.error(err);
    exportError.value = "Export failed. Please try again.";
    message.error("Export failed. Please try again.");
  } finally {
    isExporting.value = false;
  }
}
</script>

<template>
  <div class="flex flex-col w-full gap-6">

    <!-- Description -->
    <p class="text-sm text-gray-500">
      Generate and download a PDF financial statement to share with the barangay treasurer.
      Only transactions with <span class="font-medium text-gray-700">payment status = Paid</span> count toward the collected total.
    </p>

    <div class="grid grid-cols-2 gap-6 items-start">

      <!-- ── LEFT: Controls ────────────────────────────────────────── -->
      <div class="flex flex-col gap-5">

        <!-- Service selector -->
        <div>
          <p class="text-[12px] font-semibold text-gray-700 uppercase tracking-wider mb-3">
            Service Coverage
          </p>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="opt in serviceOptions"
              :key="String(opt.value)"
              @click="service = opt.value"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg border text-[13px] font-medium transition-all text-left"
              :class="service === opt.value
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 bg-white text-gray-600 hover:border-blue-300 hover:bg-blue-50/50'"
            >
              <span class="w-2 h-2 rounded-full flex-shrink-0" :class="opt.dot" />
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- Date range -->
        <div>
          <p class="text-[12px] font-semibold text-gray-700 uppercase tracking-wider mb-3">
            Date Range
          </p>

          <!-- Quick presets -->
          <div class="flex flex-wrap gap-1.5 mb-3">
            <button
              v-for="p in presets"
              :key="p.key"
              @click="applyPreset(p.key)"
              class="px-3 py-1 text-[12px] font-medium rounded-full border border-gray-200 bg-gray-50 text-gray-600 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-600 transition-all"
            >
              {{ p.label }}
            </button>
          </div>

          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
            class="w-full"
          />
        </div>

        <!-- Export button -->
        <button
          @click="handleExport"
          :disabled="!canExport || isExporting"
          class="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-[13px] font-semibold transition-all"
          :class="canExport && !isExporting
            ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm cursor-pointer'
            : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
        >
          <!-- Spinner -->
          <svg v-if="isExporting" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          <!-- Download icon -->
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1M12 12v6m0 0l-3-3m3 3l3-3M12 4v8" />
          </svg>
          {{ isExporting ? "Generating PDF…" : "Export Financial Statement" }}
        </button>

        <!-- Success feedback -->
        <p v-if="lastExported" class="flex items-center gap-1.5 text-[12px] text-green-600 font-medium">
          <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          Last exported: {{ lastExported }}
        </p>

        <!-- Error feedback -->
        <p v-if="exportError" class="text-[12px] text-red-500">{{ exportError }}</p>

      </div>

      <!-- ── RIGHT: Preview card ────────────────────────────────────── -->
      <div class="rounded-lg border border-gray-200 overflow-hidden">

        <!-- Card header -->
        <div class="bg-[#1a3a5c] px-5 py-3">
          <p class="text-[13px] font-bold text-white">Export Preview</p>
          <p class="text-[11px] text-blue-200 mt-0.5">What will be included in the PDF</p>
        </div>

        <!-- Preview rows -->
        <div class="divide-y divide-gray-100 bg-white">
          <div class="flex justify-between items-center px-5 py-3">
            <span class="text-[12px] text-gray-500">Service Coverage</span>
            <span class="text-[13px] font-semibold text-blue-600">{{ serviceLabel }}</span>
          </div>
          <div class="flex justify-between items-center px-5 py-3">
            <span class="text-[12px] text-gray-500">Period From</span>
            <span class="text-[13px] font-medium text-gray-800">{{ previewFrom }}</span>
          </div>
          <div class="flex justify-between items-center px-5 py-3">
            <span class="text-[12px] text-gray-500">Period To</span>
            <span class="text-[13px] font-medium text-gray-800">{{ previewTo }}</span>
          </div>
          <div class="flex justify-between items-center px-5 py-3">
            <span class="text-[12px] text-gray-500">Format</span>
            <span class="text-[13px] font-medium text-gray-800">PDF (.pdf)</span>
          </div>
          <div class="flex justify-between items-start px-5 py-3">
            <span class="text-[12px] text-gray-500">Contains</span>
            <span class="text-[12px] text-gray-600 text-right leading-relaxed">
              Transaction list<br />
              Payment status per row<br />
              Section subtotals<br />
              Grand total collected
            </span>
          </div>
        </div>

        <!-- Footer hint -->
        <div class="px-5 py-3 bg-blue-50 border-t border-blue-100">
          <p class="text-[11px] text-blue-600 leading-relaxed">
            The PDF can be sent to the treasurer via email or messaging app —
            no system access required on their end.
          </p>
        </div>

      </div>
    </div>
  </div>
</template>