<script setup>
/**
 * @file SecuritySettings.vue
 * @description Security-related settings: RFID expiration, idle timeout,
 *              auto-logout, and failed login lockout threshold.
 */
import { ref } from "vue";
import { NButton, NSwitch, useMessage } from "naive-ui";

const message = useMessage();

// ── RFID / Brgy ID Expiration ─────────────────────────────────────────────────
const rfidExpirationMonths = ref(12);
const rfidReminderDays     = ref(30);

// ── Session / Idle ────────────────────────────────────────────────────────────
const idleTimeoutMinutes  = ref(10);
const autoLogoutMinutes   = ref(30);
const idleEnabled         = ref(true);
const autoLogoutEnabled   = ref(true);

// ── Failed Login Lockout ──────────────────────────────────────────────────────
const maxFailedAttempts   = ref(5);
const lockoutDurationMins = ref(15);
const lockoutEnabled      = ref(true);

const saveSettings = () => {
  // Replace with actual API save call
  message.success("Security settings saved successfully.");
};

const resetDefaults = () => {
  rfidExpirationMonths.value = 12;
  rfidReminderDays.value     = 30;
  idleTimeoutMinutes.value   = 10;
  autoLogoutMinutes.value    = 30;
  idleEnabled.value          = true;
  autoLogoutEnabled.value    = true;
  maxFailedAttempts.value    = 5;
  lockoutDurationMins.value  = 15;
  lockoutEnabled.value       = true;
  message.info("Settings reset to defaults.");
};
</script>

<template>
  <div class="flex flex-col gap-8 max-w-2xl">

    <!-- ── RFID Expiration ─────────────────────────────────── -->
    <section class="flex flex-col gap-4">
      <div class="flex items-center gap-2 mb-1">
        <span class="font-semibold text-[16px] text-[#373737]">Brgy. ID (RFID) Expiration</span>
      </div>
      <p class="text-[13px] text-gray-400 -mt-3 leading-relaxed">
        Define how long a barangay ID remains valid and when residents are notified of upcoming expiry.
      </p>

      <div class="grid grid-cols-2 gap-4">
        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Validity Period (months)</label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="rfidExpirationMonths"
              type="number" min="1" max="120"
              class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-full focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
            />
            <span class="text-[13px] text-gray-400 whitespace-nowrap">months</span>
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Expiry Reminder (days before)</label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="rfidReminderDays"
              type="number" min="1" max="365"
              class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-full focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
            />
            <span class="text-[13px] text-gray-400 whitespace-nowrap">days</span>
          </div>
        </div>
      </div>

      <div class="text-[12px] text-gray-400 bg-blue-50 border border-blue-100 rounded-md px-4 py-3 mt-1">
        ℹ️ IDs issued today will expire on <strong>{{ new Date(Date.now() + rfidExpirationMonths * 30 * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) }}</strong>.
        Reminders will be sent <strong>{{ rfidReminderDays }} days</strong> before expiry.
      </div>
    </section>

    <div class="border-t border-gray-100" />

    <!-- ── Idle Timeout ────────────────────────────────────── -->
    <section class="flex flex-col gap-4">
      <div class="flex items-center justify-between">
        <div>
          <span class="font-semibold text-[16px] text-[#373737]">Idle Timeout</span>
          <p class="text-[13px] text-gray-400 mt-0.5">Lock the screen after a period of inactivity on the kiosk.</p>
        </div>
        <n-switch v-model:value="idleEnabled" />
      </div>

      <div class="flex items-center gap-3" :class="{ 'opacity-40 pointer-events-none': !idleEnabled }">
        <label class="text-[13px] font-medium text-gray-600 w-48">Lock screen after</label>
        <div class="flex items-center gap-2">
          <input
            v-model.number="idleTimeoutMinutes"
            type="number" min="1" max="60"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-24 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          />
          <span class="text-[13px] text-gray-400">minutes of inactivity</span>
        </div>
      </div>
    </section>

    <div class="border-t border-gray-100" />

    <!-- ── Auto-Logout ────────────────────────────────────── -->
    <section class="flex flex-col gap-4">
      <div class="flex items-center justify-between">
        <div>
          <span class="font-semibold text-[16px] text-[#373737]">Auto-Logout</span>
          <p class="text-[13px] text-gray-400 mt-0.5">Automatically log out admin sessions after prolonged inactivity.</p>
        </div>
        <n-switch v-model:value="autoLogoutEnabled" />
      </div>

      <div class="flex items-center gap-3" :class="{ 'opacity-40 pointer-events-none': !autoLogoutEnabled }">
        <label class="text-[13px] font-medium text-gray-600 w-48">Log out admin after</label>
        <div class="flex items-center gap-2">
          <input
            v-model.number="autoLogoutMinutes"
            type="number" min="1" max="480"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-24 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          />
          <span class="text-[13px] text-gray-400">minutes of inactivity</span>
        </div>
      </div>

      <p class="text-[12px] text-gray-400">
        Note: Idle Timeout locks the kiosk screen. Auto-Logout ends the admin dashboard session entirely.
      </p>
    </section>

    <div class="border-t border-gray-100" />

    <!-- ── Failed Login Lockout ───────────────────────────── -->
    <section class="flex flex-col gap-4">
      <div class="flex items-center justify-between">
        <div>
          <span class="font-semibold text-[16px] text-[#373737]">Failed Login Lockout</span>
          <p class="text-[13px] text-gray-400 mt-0.5">Temporarily block access after too many failed login attempts.</p>
        </div>
        <n-switch v-model:value="lockoutEnabled" />
      </div>

      <div class="grid grid-cols-2 gap-4" :class="{ 'opacity-40 pointer-events-none': !lockoutEnabled }">
        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Max Failed Attempts</label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="maxFailedAttempts"
              type="number" min="1" max="20"
              class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-full focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
            />
            <span class="text-[13px] text-gray-400">attempts</span>
          </div>
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Lockout Duration</label>
          <div class="flex items-center gap-2">
            <input
              v-model.number="lockoutDurationMins"
              type="number" min="1" max="1440"
              class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-full focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
            />
            <span class="text-[13px] text-gray-400">minutes</span>
          </div>
        </div>
      </div>

      <div v-if="lockoutEnabled" class="text-[12px] text-amber-700 bg-amber-50 border border-amber-100 rounded-md px-4 py-3">
        ⚠️ After <strong>{{ maxFailedAttempts }}</strong> failed attempts, the account will be locked for
        <strong>{{ lockoutDurationMins }} minutes</strong>.
      </div>
    </section>

    <div class="border-t border-gray-100" />

    <!-- Save / Reset -->
    <div class="flex items-center gap-3 pb-4">
      <n-button type="primary" @click="saveSettings">Save Settings</n-button>
      <n-button @click="resetDefaults">Reset to Defaults</n-button>
    </div>

  </div>
</template>