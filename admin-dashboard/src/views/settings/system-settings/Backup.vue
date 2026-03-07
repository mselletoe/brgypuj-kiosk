<script setup>
/**
 * @file BackupSettings.vue
 * @description Backup and restore data configuration.
 */
import { ref } from "vue";
import { NButton, NSwitch, NSelect, useMessage } from "naive-ui";

const message = useMessage();

const autoBackupEnabled   = ref(true);
const backupFrequency     = ref("daily");
const backupTime          = ref("02:00");
const retentionDays       = ref(30);
const isBackingUp         = ref(false);
const isRestoring         = ref(false);

const frequencyOptions = [
  { label: "Daily",   value: "daily" },
  { label: "Weekly",  value: "weekly" },
  { label: "Monthly", value: "monthly" },
];

// Mock backup history
const backupHistory = ref([
  { id: 1, date: "Mar 6, 2026",  time: "02:00 AM", size: "4.2 MB",  status: "success", type: "auto" },
  { id: 2, date: "Mar 5, 2026",  time: "02:00 AM", size: "4.1 MB",  status: "success", type: "auto" },
  { id: 3, date: "Mar 4, 2026",  time: "11:45 AM", size: "4.0 MB",  status: "success", type: "manual" },
  { id: 4, date: "Mar 3, 2026",  time: "02:00 AM", size: "3.9 MB",  status: "failed",  type: "auto" },
  { id: 5, date: "Mar 2, 2026",  time: "02:00 AM", size: "3.8 MB",  status: "success", type: "auto" },
]);

const runManualBackup = async () => {
  isBackingUp.value = true;
  await new Promise((r) => setTimeout(r, 1800));
  isBackingUp.value = false;
  backupHistory.value.unshift({
    id: Date.now(),
    date:   new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
    time:   new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
    size:   "4.3 MB",
    status: "success",
    type:   "manual",
  });
  message.success("Manual backup completed successfully.");
};

const downloadBackup = (backup) => {
  message.info(`Downloading backup from ${backup.date}...`);
};

const restoreBackup = (backup) => {
  message.warning(`Restore from ${backup.date} initiated. This may take a moment.`);
};

const saveSettings = () => {
  message.success("Backup settings saved.");
};

const statusClass = (status) =>
  status === "success"
    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
    : "bg-red-50 text-red-600 border border-red-200";

const typeBadge = (type) =>
  type === "manual"
    ? "bg-indigo-50 text-indigo-600 border border-indigo-200"
    : "bg-gray-100 text-gray-500 border border-gray-200";
</script>

<template>
  <div class="flex flex-col gap-8 w-full">

    <!-- ── Auto Backup Config ──────────────────────────────── -->
    <div class="flex flex-col gap-4 max-w-2xl">
      <div class="flex items-center justify-between">
        <div>
          <span class="font-semibold text-[16px] text-[#373737]">Automatic Backup</span>
          <p class="text-[13px] text-gray-400 mt-0.5">Schedule regular backups of all barangay data.</p>
        </div>
        <n-switch v-model:value="autoBackupEnabled" />
      </div>

      <div class="grid grid-cols-3 gap-4" :class="{ 'opacity-40 pointer-events-none': !autoBackupEnabled }">

        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Frequency</label>
          <n-select v-model:value="backupFrequency" :options="frequencyOptions" />
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Time</label>
          <input
            v-model="backupTime"
            type="time"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          />
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Retention Period</label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="retentionDays"
              type="number" min="7" max="365"
              class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-full focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
            />
            <span class="text-[13px] text-gray-400 whitespace-nowrap">days</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3 mt-1">
        <n-button type="primary" size="small" @click="saveSettings">Save Settings</n-button>
      </div>
    </div>

    <div class="border-t border-gray-100" />

    <!-- ── Manual Backup ──────────────────────────────────── -->
    <div class="flex flex-col gap-3 max-w-2xl">
      <span class="font-semibold text-[16px] text-[#373737]">Manual Backup</span>
      <p class="text-[13px] text-gray-400">Create an on-demand backup of the current system state.</p>
      <div class="flex items-center gap-3">
        <n-button
          type="primary"
          :loading="isBackingUp"
          @click="runManualBackup"
          :disabled="isBackingUp"
        >
          {{ isBackingUp ? "Backing up..." : "Run Backup Now" }}
        </n-button>
        <span v-if="!isBackingUp" class="text-[12px] text-gray-400">
          Last backup: {{ backupHistory[0]?.date }} at {{ backupHistory[0]?.time }}
        </span>
      </div>
    </div>

    <div class="border-t border-gray-100" />

    <!-- ── Backup History ─────────────────────────────────── -->
    <div class="flex flex-col gap-4 w-full">
      <span class="font-semibold text-[16px] text-[#373737]">Backup History</span>

      <div class="overflow-x-auto w-full">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-gray-200">
              <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Date & Time</th>
              <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Type</th>
              <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Size</th>
              <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Status</th>
              <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="backup in backupHistory"
              :key="backup.id"
              class="border-b border-gray-100 last:border-none hover:bg-gray-50 transition-colors"
            >
              <td class="py-4 px-4">
                <span class="block text-[13px] text-gray-800 font-medium">{{ backup.date }}</span>
                <span class="block text-[11px] text-gray-400 mt-0.5">{{ backup.time }}</span>
              </td>
              <td class="py-4 px-4">
                <span class="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize" :class="typeBadge(backup.type)">
                  {{ backup.type }}
                </span>
              </td>
              <td class="py-4 px-4 text-[13px] text-gray-600">{{ backup.size }}</td>
              <td class="py-4 px-4">
                <span class="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize" :class="statusClass(backup.status)">
                  {{ backup.status }}
                </span>
              </td>
              <td class="py-4 px-4">
                <div class="flex items-center gap-2">
                  <button
                    v-if="backup.status === 'success'"
                    @click="downloadBackup(backup)"
                    class="text-[12px] font-medium px-3 py-1 rounded-md border border-blue-200 text-blue-600 hover:bg-blue-50 transition-colors"
                  >
                    Download
                  </button>
                  <button
                    v-if="backup.status === 'success'"
                    @click="restoreBackup(backup)"
                    class="text-[12px] font-medium px-3 py-1 rounded-md border border-amber-200 text-amber-600 hover:bg-amber-50 transition-colors"
                  >
                    Restore
                  </button>
                  <span v-if="backup.status === 'failed'" class="text-[12px] text-gray-400">—</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>