<script setup>
import { ref, computed, onMounted } from 'vue'
import { NButton, NSwitch, NSpin, useMessage } from 'naive-ui'
import { getSystemConfig, updateSystemConfig } from '@/api/systemConfigService'

const message = useMessage()
const loading = ref(true)
const saving  = ref(false)

const rfidExpirationMonths = ref(12) 
const rfidReminderDays     = ref(30)

const autoLogoutEnabled = ref(true)
const autoLogoutMins    = ref(30)
const autoLogoutSecs    = ref(0)

const autoLogoutDuration = computed(() =>
  autoLogoutMins.value * 60 + autoLogoutSecs.value
)

const lockoutEnabled    = ref(true)
const maxFailedAttempts = ref(5)
const lockoutMinutes    = ref(15)

onMounted(async () => {
  try {
    const config = await getSystemConfig()

    const expiryDays             = config.rfid_expiry_days    ?? 365
    rfidExpirationMonths.value   = Math.round(expiryDays / 30)
    rfidReminderDays.value       = config.rfid_reminder_days  ?? 30
    maxFailedAttempts.value      = config.max_failed_attempts ?? 5
    lockoutMinutes.value    = config.lockout_minutes     ?? 15
    lockoutEnabled.value    = maxFailedAttempts.value > 0

    const totalSecs      = config.auto_logout_duration ?? 1800
    autoLogoutEnabled.value = totalSecs > 0
    autoLogoutMins.value = Math.floor(totalSecs / 60)
    autoLogoutSecs.value = totalSecs % 60
  } catch {
    message.error('Failed to load security settings.')
  } finally {
    loading.value = false
  }
})

const saveSettings = async () => {
  if (autoLogoutEnabled.value && autoLogoutDuration.value < 10) {
    message.warning('Auto-logout duration must be at least 10 seconds.')
    return
  }
  if (autoLogoutSecs.value < 0 || autoLogoutSecs.value > 59) {
    message.warning('Seconds must be between 0 and 59.')
    return
  }

  saving.value = true
  try {
    await updateSystemConfig({
      rfid_expiry_days:     rfidExpirationMonths.value * 30,
      rfid_reminder_days:   rfidReminderDays.value,
      auto_logout_duration: autoLogoutEnabled.value ? autoLogoutDuration.value : 0,
      max_failed_attempts:  lockoutEnabled.value ? maxFailedAttempts.value : 0,
      lockout_minutes:      lockoutMinutes.value,
    })
    message.success('Security settings saved.')
  } catch {
    message.error('Failed to save settings.')
  } finally {
    saving.value = false
  }
}

const resetDefaults = () => {
  rfidExpirationMonths.value  = 12
  rfidReminderDays.value      = 30
  autoLogoutEnabled.value = true
  autoLogoutMins.value    = 30
  autoLogoutSecs.value    = 0
  lockoutEnabled.value    = true
  maxFailedAttempts.value = 5
  lockoutMinutes.value    = 15
  message.info('Reset to defaults — click Save to apply.')
}

const autoLogoutPreview = computed(() => {
  const m = autoLogoutMins.value
  const s = autoLogoutSecs.value
  if (m === 0 && s === 0) return '—'
  if (m === 0) return `${s}s`
  if (s === 0) return `${m} min`
  return `${m} min ${s}s`
})
</script>

<template>
  <div class="flex flex-col gap-8 max-w-2xl">

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <n-spin size="medium" />
    </div>

    <template v-else>

      <!-- ── RFID Expiration ─────────────────────────────────────────────── -->
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

        <div class="text-[12px] text-gray-600 bg-blue-50 border border-blue-200 rounded-md px-4 py-3 mt-1">
          ℹ️ IDs issued today will expire on <strong>{{ new Date(Date.now() + rfidExpirationMonths * 30 * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) }}</strong>.
          Reminders will be sent <strong>{{ rfidReminderDays }} day{{ rfidReminderDays !== 1 ? 's' : '' }}</strong> before expiry.
        </div>
      </section>

      <div class="border-t border-gray-100" />

      <!-- ── Auto-Logout ────────────────────────────────────────────────── -->
      <section class="flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <div>
            <span class="font-semibold text-[16px] text-[#373737]">Auto-Logout</span>
            <p class="text-[13px] text-gray-400 mt-0.5">
              Automatically log out kiosk sessions after prolonged inactivity.
            </p>
          </div>
          <n-switch v-model:value="autoLogoutEnabled" />
        </div>

        <div
          class="flex flex-col gap-3 transition-opacity"
          :class="{ 'opacity-40 pointer-events-none': !autoLogoutEnabled }"
        >
          <label class="text-[13px] font-medium text-gray-600">Log out kiosk user after</label>

          <!-- Minutes + Seconds side by side -->
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-2">
              <input
                v-model.number="autoLogoutMins"
                type="number" min="0" max="480"
                class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-24 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
              />
              <span class="text-[13px] text-gray-400">min</span>
            </div>

            <span class="text-gray-300 text-lg font-light">:</span>

            <div class="flex items-center gap-2">
              <input
                v-model.number="autoLogoutSecs"
                type="number" min="0" max="59"
                class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-24 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
              />
              <span class="text-[13px] text-gray-400">sec</span>
            </div>

            <!-- Live preview -->
            <span
              v-if="autoLogoutEnabled && autoLogoutDuration >= 10"
              class="ml-2 text-[12px] text-blue-600 bg-blue-50 border border-blue-200 rounded-full px-3 py-1 font-medium"
            >
              {{ autoLogoutPreview }} of inactivity
            </span>
            <span
              v-else-if="autoLogoutEnabled && autoLogoutDuration < 10"
              class="ml-2 text-[12px] text-red-500"
            >
              Minimum is 10 seconds
            </span>
          </div>

          <p class="text-[12px] text-gray-400">
            A 30-second warning will appear before the session is ended.
            Both Guest and RFID sessions are affected.
          </p>
        </div>
      </section>

      <div class="border-t border-gray-100" />

      <!-- ── Failed Login Lockout ───────────────────────────────────────── -->
      <section class="flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <div>
            <span class="font-semibold text-[16px] text-[#373737]">Failed Login Lockout</span>
            <p class="text-[13px] text-gray-400 mt-0.5">
              Temporarily block RFID access after too many consecutive wrong PINs.
            </p>
          </div>
          <n-switch v-model:value="lockoutEnabled" />
        </div>

        <div
          class="grid grid-cols-2 gap-4"
          :class="{ 'opacity-40 pointer-events-none': !lockoutEnabled }"
        >
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
                v-model.number="lockoutMinutes"
                type="number" min="1" max="1440"
                class="border border-gray-200 rounded-md px-3 py-2 text-[14px] w-full focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
              />
              <span class="text-[13px] text-gray-400">minutes</span>
            </div>
          </div>
        </div>

        <div
          v-if="lockoutEnabled"
          class="text-[12px] text-amber-700 bg-amber-50 border border-amber-100 rounded-md px-4 py-3"
        >
          ⚠️ After <strong>{{ maxFailedAttempts }}</strong> failed attempts, the RFID card will be
          locked for <strong>{{ lockoutMinutes }} minute{{ lockoutMinutes !== 1 ? 's' : '' }}</strong>.
        </div>
      </section>

      <div class="border-t border-gray-100" />

      <!-- ── Actions ────────────────────────────────────────────────────── -->
      <div class="flex items-center gap-3 pb-4">
        <n-button type="primary" :loading="saving" @click="saveSettings">
          Save Settings
        </n-button>
        <n-button :disabled="saving" @click="resetDefaults">
          Reset to Defaults
        </n-button>
      </div>

    </template>
  </div>
</template>