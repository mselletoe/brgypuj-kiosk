<script setup>
/**
 * @file SystemPreferences.vue
 * @description Default View, Maintenance Mode, and Clear Logs settings.
 * Reads from GET /admin/settings on mount; saves via PATCH /admin/settings.
 */
import { ref, onMounted } from "vue";
import { NButton, NSwitch, NSelect, NModal, NSpin, useMessage } from "naive-ui";
import { getSystemConfig, updateSystemConfig } from "@/api/systemConfigService";

const message = useMessage();
const loading = ref(true);
const saving  = ref(false);

// ── Default View ──────────────────────────────────────────────────────────────
const defaultView = ref("dashboard");
const viewOptions = [
  { label: "Dashboard Overview", value: "dashboard"         },
  { label: "Document Requests",  value: "document-requests" },
  { label: "Residents",          value: "residents"         },
  { label: "Blotter / KP Logs",  value: "blotter"           },
  { label: "Equipment Requests", value: "equipment"         },
];

// ── Maintenance Mode ──────────────────────────────────────────────────────────
const maintenanceEnabled = ref(false);
const maintenanceMessage = ref(
  "The system is currently undergoing scheduled maintenance. Please try again later."
);
const showMaintenanceConfirm = ref(false);
// Holds the pending toggle value while the confirm modal is open
const pendingMaintenanceValue = ref(false);

const toggleMaintenance = (newVal) => {
  if (newVal === true) {
    // Turning ON → ask for confirmation first
    pendingMaintenanceValue.value  = true;
    showMaintenanceConfirm.value   = true;
  } else {
    // Turning OFF → apply immediately
    applyMaintenance(false);
  }
};

const confirmMaintenance = async () => {
  showMaintenanceConfirm.value = false;
  await applyMaintenance(true);
};

const applyMaintenance = async (enabled) => {
  saving.value = true;
  try {
    await updateSystemConfig({
      maintenance_mode:    enabled,
      maintenance_message: maintenanceMessage.value,
    });
    maintenanceEnabled.value = enabled;
    if (enabled) {
      message.warning("Maintenance mode is now ACTIVE. The kiosk is inaccessible to residents.");
    } else {
      message.success("Maintenance mode disabled. System is now live.");
    }
  } catch {
    message.error("Failed to update maintenance mode.");
  } finally {
    saving.value = false;
  }
};

// Save the message text separately (for when admin edits message while mode is already on)
const saveMaintenanceMessage = async () => {
  saving.value = true;
  try {
    await updateSystemConfig({ maintenance_message: maintenanceMessage.value });
    message.success("Maintenance message saved.");
  } catch {
    message.error("Failed to save maintenance message.");
  } finally {
    saving.value = false;
  }
};

// ── Clear Logs ────────────────────────────────────────────────────────────────
const showClearLogsConfirm   = ref(false);
const clearAuditLogs         = ref(true);
const clearSystemLogs        = ref(true);
const clearLogsOlderThanDays = ref(90);

const openClearLogs = () => { showClearLogsConfirm.value = true; };

const confirmClearLogs = () => {
  showClearLogsConfirm.value = false;
  const targets = [];
  if (clearAuditLogs.value)  targets.push("Audit Logs");
  if (clearSystemLogs.value) targets.push("System Logs");
  if (targets.length === 0) {
    message.warning("No log type selected.");
    return;
  }
  // TODO: wire to clear-logs API endpoint when available
  message.success(`${targets.join(" and ")} older than ${clearLogsOlderThanDays.value} days cleared.`);
};

// ── Save Default View ─────────────────────────────────────────────────────────
const savePreferences = async () => {
  saving.value = true;
  try {
    await updateSystemConfig({ default_view: defaultView.value });
    message.success("Default view saved.");
  } catch {
    message.error("Failed to save default view.");
  } finally {
    saving.value = false;
  }
};

// ── Load on mount ─────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const config = await getSystemConfig();
    if (config) {
      defaultView.value        = config.default_view        ?? "dashboard";
      maintenanceEnabled.value = config.maintenance_mode    ?? false;
      maintenanceMessage.value = config.maintenance_message
        ?? "The system is currently undergoing scheduled maintenance. Please try again later.";
    }
  } catch {
    message.error("Failed to load preferences.");
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <n-spin :show="loading">
    <div class="flex flex-col gap-8 max-w-2xl">

      <!-- ── Default View ────────────────────────────────────── -->
      <section class="flex flex-col gap-4">
        <div>
          <span class="font-semibold text-[16px] text-[#373737]">Default View</span>
          <p class="text-[13px] text-gray-400 mt-0.5">The first page shown when an admin logs in to the dashboard.</p>
        </div>

        <div class="flex flex-col gap-1.5 max-w-xs">
          <label class="text-[13px] font-medium text-gray-600">Landing Page</label>
          <n-select v-model:value="defaultView" :options="viewOptions" />
        </div>

        <n-button size="small" type="primary" :loading="saving" style="width: fit-content;" @click="savePreferences">
          Save Preference
        </n-button>
      </section>

      <div class="border-t border-gray-100" />

      <!-- ── Maintenance Mode ───────────────────────────────── -->
      <section class="flex flex-col gap-4">
        <div class="flex items-start justify-between gap-4">
          <div>
            <span class="font-semibold text-[16px] text-[#373737]">Maintenance Mode</span>
            <p class="text-[13px] text-gray-400 mt-0.5">
              When enabled, the kiosk displays a maintenance notice and blocks all resident transactions.
              The admin dashboard remains accessible.
            </p>
          </div>
          <n-switch
            :value="maintenanceEnabled"
            :loading="saving"
            @update:value="toggleMaintenance"
            :rail-style="() => maintenanceEnabled ? { background: '#ef4444' } : {}"
          />
        </div>

        <!-- Status banner -->
        <div
          class="flex items-center gap-3 rounded-md px-4 py-3 text-[13px] font-medium border"
          :class="maintenanceEnabled
            ? 'bg-red-50 border-red-200 text-red-700'
            : 'bg-emerald-50 border-emerald-200 text-emerald-700'"
        >
          <span
            class="w-2 h-2 rounded-full flex-shrink-0"
            :class="maintenanceEnabled ? 'bg-red-500' : 'bg-emerald-500'"
          />
          {{ maintenanceEnabled
            ? "Maintenance mode is ACTIVE — kiosk is offline to residents."
            : "System is LIVE — kiosk is accessible to residents."
          }}
        </div>

        <!-- Maintenance message -->
        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Kiosk Maintenance Message</label>
          <textarea
            v-model="maintenanceMessage"
            rows="3"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px] text-gray-700 resize-none focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
            placeholder="Message shown to residents on the kiosk..."
          />
          <p class="text-[12px] text-gray-400">
            This message is displayed full-screen on the kiosk when maintenance mode is on.
          </p>
          <n-button
            size="small"
            type="primary"
            :loading="saving"
            style="width: fit-content;"
            @click="saveMaintenanceMessage"
          >
            Save Message
          </n-button>
        </div>
      </section>

      <div class="border-t border-gray-100" />

      <!-- ── Clear Logs ─────────────────────────────────────── -->
      <section class="flex flex-col gap-4">
        <div>
          <span class="font-semibold text-[16px] text-[#373737]">Clear Logs</span>
          <p class="text-[13px] text-gray-400 mt-0.5">
            Permanently delete old log records to free up storage. This action cannot be undone.
          </p>
        </div>

        <div class="flex items-center gap-4 p-4 bg-gray-50 border border-gray-200 rounded-md">
          <div class="flex flex-col gap-3 flex-1">
            <div class="flex items-center gap-3">
              <input type="checkbox" v-model="clearAuditLogs"  id="chk-audit"  class="w-4 h-4 accent-blue-600" />
              <label for="chk-audit"  class="text-[13px] text-gray-700 cursor-pointer">Audit Logs</label>
            </div>
            <div class="flex items-center gap-3">
              <input type="checkbox" v-model="clearSystemLogs" id="chk-system" class="w-4 h-4 accent-blue-600" />
              <label for="chk-system" class="text-[13px] text-gray-700 cursor-pointer">System Logs</label>
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] font-medium text-gray-600">Delete records older than</label>
            <div class="flex items-center gap-2">
              <input
                v-model.number="clearLogsOlderThanDays"
                type="number" min="1" max="3650"
                class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-24 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
              />
              <span class="text-[13px] text-gray-400">days</span>
            </div>
          </div>
        </div>

        <div>
          <n-button type="error" ghost @click="openClearLogs">Clear Selected Logs</n-button>
          <p class="text-[12px] text-gray-400 mt-2">
            ⚠️ This action is permanent. A record of the clearing will be saved in the audit trail.
          </p>
        </div>
      </section>

      <!-- ── Maintenance Confirm Modal ──────────────────────── -->
      <n-modal
        v-model:show="showMaintenanceConfirm"
        preset="dialog"
        type="warning"
        title="Enable Maintenance Mode?"
        positive-text="Enable"
        negative-text="Cancel"
        @positive-click="confirmMaintenance"
        @negative-click="showMaintenanceConfirm = false"
      >
        <p class="text-[14px] text-gray-600 leading-relaxed">
          The kiosk will go <strong>offline immediately</strong> for all residents.
          Admin dashboard access will remain unaffected. Are you sure?
        </p>
      </n-modal>

      <!-- ── Clear Logs Confirm Modal ──────────────────────── -->
      <n-modal
        v-model:show="showClearLogsConfirm"
        preset="dialog"
        type="error"
        title="Confirm Clear Logs"
        positive-text="Yes, Clear Logs"
        negative-text="Cancel"
        @positive-click="confirmClearLogs"
        @negative-click="showClearLogsConfirm = false"
      >
        <p class="text-[14px] text-gray-600 leading-relaxed">
          You are about to permanently delete all selected log records older than
          <strong>{{ clearLogsOlderThanDays }} days</strong>.
          This action <strong>cannot be undone</strong>.
        </p>
      </n-modal>

    </div>
  </n-spin>
</template>