<script setup>
/**
 * @file Backup.vue
 * @description Backup settings tab — wired to the real backend.
 */
import { ref, computed, onMounted } from "vue";
import { NButton, NSwitch, NSelect, NModal, useMessage } from "naive-ui";
import { getSystemConfig, updateSystemConfig } from "@/api/systemConfigService";
import {
  triggerManualBackup,
  getBackupHistory,
  downloadBackupFile,
  restoreBackup,
} from "@/api/backupService";

const message = useMessage();

// ── State ─────────────────────────────────────────────────────────────────────
const loading          = ref(true);
const savingSettings   = ref(false);
const isBackingUp      = ref(false);
const historyLoading   = ref(false);

const autoBackupEnabled = ref(false);
const backupFrequency   = ref("daily");
const backupTime        = ref("02:00");

const backupHistory = ref([]);

const showRestoreModal = ref(false);
const restoreTarget    = ref(null);
const restoreFile      = ref(null);
const restoreFileInput = ref(null);
const isRestoring      = ref(false);

const lastBackupAt = ref(null);

const frequencyOptions = [
  { label: "Daily",  value: "daily"  },
  { label: "Weekly", value: "weekly" },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

const formattedLastBackup = computed(() => {
  if (!lastBackupAt.value) return "Never";
  const d = new Date(lastBackupAt.value);
  return d.toLocaleString("en-US", {
    month: "short", day: "numeric", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
});

const statusClass = (status) =>
  status === "success"
    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
    : "bg-red-50 text-red-600 border border-red-200";

const typeBadge = (type) =>
  type === "manual"
    ? "bg-indigo-50 text-indigo-600 border border-indigo-200"
    : "bg-gray-100 text-gray-500 border border-gray-200";

const formatDate = (iso) => {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
};

const formatTime = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
};

// ── Load on mount ─────────────────────────────────────────────────────────────

const loadConfig = async () => {
  const config = await getSystemConfig();
  if (config) {
    autoBackupEnabled.value = config.backup_schedule !== "manual";
    backupFrequency.value   = config.backup_schedule === "manual" ? "daily" : config.backup_schedule;
    backupTime.value        = config.backup_time || "02:00";
    lastBackupAt.value      = config.last_backup_at || null;
  }
};

const loadHistory = async () => {
  historyLoading.value = true;
  try {
    backupHistory.value = await getBackupHistory();
  } catch {
    backupHistory.value = [];
  } finally {
    historyLoading.value = false;
  }
};

onMounted(async () => {
  loading.value = true;
  await Promise.all([loadConfig(), loadHistory()]);
  loading.value = false;
});

// ── Save schedule settings ────────────────────────────────────────────────────

const saveSettings = async () => {
  savingSettings.value = true;
  try {
    const schedule = autoBackupEnabled.value ? backupFrequency.value : "manual";
    await updateSystemConfig({
      backup_schedule: schedule,
      backup_time:     backupTime.value,
    });
    message.success("Backup settings saved.");
  } catch {
    message.error("Failed to save backup settings.");
  } finally {
    savingSettings.value = false;
  }
};

// ── Manual backup → triggers browser download ────────────────────────────────

const runManualBackup = async () => {
  isBackingUp.value = true;
  try {
    const response = await triggerManualBackup();

    const disposition = response.headers["content-disposition"] || "";
    const headerName  = response.headers["x-backup-filename"]   || "";
    let filename      = headerName;
    if (!filename) {
      const match = disposition.match(/filename="?([^"]+)"?/);
      filename = match ? match[1] : `backup_manual_${Date.now()}.sql`;
    }

    const url  = URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href  = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);

    message.success("Backup completed — downloading now.");

    const config = await getSystemConfig();
    if (config) lastBackupAt.value = config.last_backup_at;
    await loadHistory();

  } catch (err) {
    const detail = err.response?.data?.detail || "Backup failed. Check server logs.";
    message.error(detail);
  } finally {
    isBackingUp.value = false;
  }
};

// ── Download a saved backup from Pi ──────────────────────────────────────────

const handleDownload = async (backup) => {
  try {
    const response = await downloadBackupFile(backup.filename);
    const url  = URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href  = url;
    link.download = backup.filename;
    link.click();
    URL.revokeObjectURL(url);
    message.success(`Downloading ${backup.filename}`);
  } catch {
    message.error("Download failed.");
  }
};

// ── Restore ───────────────────────────────────────────────────────────────────

const openRestoreModal = (backup) => {
  restoreTarget.value    = backup;
  restoreFile.value      = null;
  showRestoreModal.value = true;
};

const onFileSelected = (e) => {
  const f = e.target.files?.[0];
  if (f && !f.name.endsWith(".sql")) {
    message.error("Only .sql backup files are accepted.");
    restoreFile.value = null;
    return;
  }
  restoreFile.value = f || null;
};

const confirmRestore = async () => {
  if (!restoreFile.value) {
    message.error("Please select the backup .sql file to restore.");
    return;
  }
  isRestoring.value = true;
  try {
    await restoreBackup(restoreFile.value);
    message.success("Database restored successfully.");
    showRestoreModal.value = false;
  } catch (err) {
    const detail = err.response?.data?.detail || "Restore failed.";
    message.error(detail);
  } finally {
    isRestoring.value = false;
  }
};
</script>

<template>
  <div class="flex flex-col gap-8 w-full">

    <!-- ── Loading ────────────────────────────────────────────── -->
    <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-[13px]">
      <svg class="animate-spin h-4 w-4 text-blue-400" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
      Loading backup settings…
    </div>

    <template v-else>

      <!-- ── Auto Backup Config ─────────────────────────────────── -->
      <div class="flex flex-col gap-4 max-w-2xl">
        <div class="flex items-center justify-between">
          <div>
            <span class="font-semibold text-[16px] text-[#373737]">Automatic Backup</span>
            <p class="text-[13px] text-gray-400 mt-0.5">
              Schedule regular backups saved on this device.
            </p>
          </div>
          <n-switch v-model:value="autoBackupEnabled" />
        </div>

        <div
          class="grid grid-cols-2 gap-4"
          :class="{ 'opacity-40 pointer-events-none': !autoBackupEnabled }"
        >
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] font-medium text-gray-600">Frequency</label>
            <n-select v-model:value="backupFrequency" :options="frequencyOptions" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] font-medium text-gray-600">Time</label>
            <input
              v-model="backupTime"
              type="time"
              class="border border-gray-200 rounded-md px-3 py-2 text-[14px]
                     focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
            />
          </div>
        </div>

        <div
          v-if="autoBackupEnabled"
          class="flex items-start gap-2 bg-blue-50 border border-blue-100 rounded-lg px-4 py-3 text-[13px] text-blue-700"
        >
          <svg class="w-4 h-4 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10A8 8 0 11 2 10a8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zm-1 9a1 1 0 01-1-1v-4a1 1 0 112 0v4a1 1 0 01-1 1z" clip-rule="evenodd"/>
          </svg>
          <span>
            Scheduled backups are saved automatically on this device.
            You can download any saved backup from the history table below.
          </span>
        </div>

        <div class="flex items-center gap-3 mt-1">
          <n-button type="primary" size="small" :loading="savingSettings" @click="saveSettings">
            Save Settings
          </n-button>
        </div>
      </div>

      <div class="border-t border-gray-100" />

      <!-- ── Manual Backup ──────────────────────────────────────── -->
      <div class="flex flex-col gap-3 max-w-2xl">
        <span class="font-semibold text-[16px] text-[#373737]">Manual Backup</span>
        <p class="text-[13px] text-gray-400">
          Create an on-demand backup. The file will download automatically to this computer.
        </p>
        <div class="flex items-center gap-3">
          <n-button
            type="primary"
            :loading="isBackingUp"
            :disabled="isBackingUp"
            @click="runManualBackup"
          >
            {{ isBackingUp ? "Backing up…" : "Run Backup Now" }}
          </n-button>
          <span v-if="!isBackingUp" class="text-[12px] text-gray-400">
            Last backup: {{ formattedLastBackup }}
          </span>
        </div>
      </div>

      <div class="border-t border-gray-100" />

      <!-- ── Backup History ─────────────────────────────────────── -->
      <div class="flex flex-col gap-4 w-full">
        <div class="flex items-center justify-between">
          <span class="font-semibold text-[16px] text-[#373737]">Backup History</span>
          <button
            class="text-[12px] text-blue-500 hover:underline"
            :disabled="historyLoading"
            @click="loadHistory"
          >
            {{ historyLoading ? "Refreshing…" : "Refresh" }}
          </button>
        </div>

        <div
          v-if="!historyLoading && backupHistory.length === 0"
          class="text-[13px] text-gray-400 py-6 text-center border border-dashed border-gray-200 rounded-lg"
        >
          No backups found. Run a manual backup or enable automatic backups.
        </div>

        <div v-else class="overflow-x-auto w-full">
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
                :key="backup.filename"
                class="border-b border-gray-100 last:border-none hover:bg-gray-50 transition-colors"
              >
                <td class="py-4 px-4">
                  <span class="block text-[13px] text-gray-800 font-medium">{{ formatDate(backup.created_at) }}</span>
                  <span class="block text-[11px] text-gray-400 mt-0.5">{{ formatTime(backup.created_at) }}</span>
                </td>
                <td class="py-4 px-4">
                  <span
                    class="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize"
                    :class="typeBadge(backup.type)"
                  >{{ backup.type }}</span>
                </td>
                <td class="py-4 px-4 text-[13px] text-gray-600">{{ backup.size }}</td>
                <td class="py-4 px-4">
                  <span
                    class="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize"
                    :class="statusClass(backup.status)"
                  >{{ backup.status }}</span>
                </td>
                <td class="py-4 px-4">
                  <div class="flex items-center gap-2">
                    <button
                      @click="handleDownload(backup)"
                      class="text-[12px] font-medium px-3 py-1 rounded-md border border-blue-200
                             text-blue-600 hover:bg-blue-50 transition-colors"
                    >
                      Download
                    </button>
                    <button
                      @click="openRestoreModal(backup)"
                      class="text-[12px] font-medium px-3 py-1 rounded-md border border-amber-200
                             text-amber-600 hover:bg-amber-50 transition-colors"
                    >
                      Restore
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </template>

    <!-- ── Restore Confirmation Modal ────────────────────────────── -->
    <n-modal v-model:show="showRestoreModal" :mask-closable="false">
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">

        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center shrink-0">
            <svg class="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213
                   3.006-1.742 3.006H4.42c-1.53 0-2.493-1.672-1.742-3.006l5.58-9.92zM11
                   13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1
                   1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <h3 class="font-semibold text-[15px] text-gray-800">Restore Database</h3>
            <p class="text-[12px] text-gray-400 mt-0.5">This will overwrite all current data.</p>
          </div>
        </div>

        <div class="bg-amber-50 border border-amber-100 rounded-lg px-4 py-3 text-[13px] text-amber-700 mb-4">
          ⚠️ Restoring replaces everything in the database. Make sure you have a
          current backup before proceeding.
        </div>

        <p class="text-[13px] text-gray-600 mb-3">
          Upload the <strong>.sql</strong> backup file to restore from:
        </p>

        <input
          ref="restoreFileInput"
          type="file"
          accept=".sql"
          class="block w-full text-[13px] text-gray-600
                 file:mr-3 file:py-1.5 file:px-3
                 file:rounded-md file:border file:border-gray-200
                 file:text-[12px] file:font-medium file:text-gray-600
                 file:bg-gray-50 file:cursor-pointer
                 hover:file:bg-gray-100 transition mb-5"
          @change="onFileSelected"
        />

        <div class="flex items-center justify-end gap-3">
          <n-button size="small" @click="showRestoreModal = false" :disabled="isRestoring">
            Cancel
          </n-button>
          <n-button
            type="warning"
            size="small"
            :loading="isRestoring"
            :disabled="!restoreFile || isRestoring"
            @click="confirmRestore"
          >
            {{ isRestoring ? "Restoring…" : "Restore Now" }}
          </n-button>
        </div>

      </div>
    </n-modal>

  </div>
</template>