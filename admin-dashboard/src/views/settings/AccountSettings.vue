<script setup>
/**
 * @file AccountSettings.vue
 * @description Admin account settings page — Profile and Security tabs wired to the backend.
 * Superadmins also see a "Linked Resident" section to relink their account to any resident.
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  NTabs,
  NTabPane,
  NInput,
  NButton,
  NAvatar,
  NSpin,
  NSelect,
  useMessage,
} from 'naive-ui'
import PageTitle from '@/components/shared/PageTitle.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getAdminProfile,
  updateAdminProfile,
  changeAdminPassword,
  uploadAdminPhoto,
  getAdminPhotoUrl,
  removeAdminPhoto,
  relinkAdminResident,
} from '@/api/accountSettingsService'
import { fetchResidentsDropdown } from '@/api/authService'
import { useAdminAuthStore } from '@/stores/auth'

const message = useMessage()
const auth = useAdminAuthStore()

// ── Confirm Modal ─────────────────────────────────────────────────────────────
const showConfirmModal = ref(false)
const confirmTitle     = ref('Are you sure?')
const confirmAction    = ref(null)

const openConfirm = (title, action) => {
  confirmTitle.value     = title
  confirmAction.value    = action
  showConfirmModal.value = true
}
const handleConfirm = async () => {
  if (confirmAction.value) await confirmAction.value()
  showConfirmModal.value = false
  confirmAction.value    = null
}
const handleCancel = () => {
  showConfirmModal.value = false
  confirmAction.value    = null
}

// ── UI State ──────────────────────────────────────────────────────────────────
const activeTab      = ref('Profile')
const loadingProfile = ref(false)
const savingProfile  = ref(false)
const savingPassword = ref(false)
const uploadingPhoto = ref(false)
const relinking      = ref(false)

// ── Profile ───────────────────────────────────────────────────────────────────
const fullName    = ref('')
const profileData = ref({ username: '', position: '' })
const photoUrl    = ref(null)
let   photoBlobUrl = null

// ── Linked Resident (superadmin only) ─────────────────────────────────────────
const residentOptions    = ref([])   // [{ label: 'First Last', value: id }]
const selectedResidentId = ref(null)

// ── Security ──────────────────────────────────────────────────────────────────
const securityData = ref({
  currentPassword: '',
  newPassword:     '',
  confirmPassword: '',
})

// ── Password strength ─────────────────────────────────────────────────────────
const passwordStrength = computed(() => {
  const pw = securityData.value.newPassword
  if (!pw) return { label: '', color: '', width: '0%' }
  let score = 0
  if (pw.length >= 8)           score++
  if (/[A-Z]/.test(pw))         score++
  if (/[0-9]/.test(pw))         score++
  if (/[^A-Za-z0-9]/.test(pw))  score++
  const levels = [
    { label: 'Weak',   color: '#ef4444', width: '25%'  },
    { label: 'Fair',   color: '#f97316', width: '50%'  },
    { label: 'Good',   color: '#eab308', width: '75%'  },
    { label: 'Strong', color: '#22c55e', width: '100%' },
  ]
  return levels[score - 1] ?? levels[0]
})

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  loadingProfile.value = true
  try {
    const [data, residents] = await Promise.all([
      getAdminProfile(),
      auth.isSuperAdmin ? fetchResidentsDropdown() : Promise.resolve([]),
    ])

    const { last_name, first_name, middle_name, suffix } = data.resident
    fullName.value = [first_name, middle_name, last_name, suffix].filter(Boolean).join(' ')
    profileData.value.username = data.username
    profileData.value.position = data.position ?? ''

    if (data.has_photo) {
      photoBlobUrl   = await getAdminPhotoUrl()
      photoUrl.value = photoBlobUrl
    }

    if (auth.isSuperAdmin) {
      residentOptions.value = residents.map(r => ({
        label: r.full_name,   // ResidentDropdownItem shape from the backend
        value: r.id,
      }))
      // Pre-select the currently linked resident
      selectedResidentId.value = data.resident_id ?? null
    }
  } catch {
    message.error('Failed to load profile.')
  } finally {
    loadingProfile.value = false
  }
})

onUnmounted(() => {
  if (photoBlobUrl) URL.revokeObjectURL(photoBlobUrl)
})

// ── Handlers ──────────────────────────────────────────────────────────────────
const handleSaveProfile = async () => {
  savingProfile.value = true
  try {
    await updateAdminProfile({ username: profileData.value.username, position: profileData.value.position })
    message.success('Profile updated successfully.')
  } catch (err) {
    message.error(err.response?.data?.detail || 'Failed to update profile.')
  } finally {
    savingProfile.value = false
  }
}

const handleRelinkResident = () => {
  if (!selectedResidentId.value) {
    message.warning('Please select a resident first.')
    return
  }
  const chosen = residentOptions.value.find(o => o.value === selectedResidentId.value)
  openConfirm(
    `Relink your account to "${chosen?.label ?? 'this resident'}"? Your displayed name will change immediately.`,
    async () => {
      relinking.value = true
      try {
        const updated = await relinkAdminResident(selectedResidentId.value)
        const { last_name, first_name, middle_name, suffix } = updated.resident
        fullName.value = [first_name, middle_name, last_name, suffix].filter(Boolean).join(' ')
        message.success('Account successfully relinked.')
      } catch (err) {
        message.error(err.response?.data?.detail || 'Failed to relink resident.')
      } finally {
        relinking.value = false
      }
    }
  )
}

const handleUploadPhoto = () => {
  const input = document.createElement('input')
  input.type   = 'file'
  input.accept = 'image/jpeg,image/png,image/webp'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    if (file.size > 2 * 1024 * 1024) { message.warning('Photo must be under 2 MB.'); return }
    uploadingPhoto.value = true
    try {
      await uploadAdminPhoto(file)
      if (photoBlobUrl) URL.revokeObjectURL(photoBlobUrl)
      photoBlobUrl   = URL.createObjectURL(file)
      photoUrl.value = photoBlobUrl
      message.success('Photo updated.')
    } catch { message.error('Failed to upload photo.') }
    finally { uploadingPhoto.value = false }
  }
  input.click()
}

const handleRemovePhoto = () => {
  openConfirm('Remove your profile photo?', async () => {
    uploadingPhoto.value = true
    try {
      await removeAdminPhoto()
      if (photoBlobUrl) URL.revokeObjectURL(photoBlobUrl)
      photoBlobUrl   = null
      photoUrl.value = null
      message.success('Photo removed.')
    } catch { message.error('Failed to remove photo.') }
    finally { uploadingPhoto.value = false }
  })
}

const handleChangePassword = async () => {
  const { currentPassword, newPassword, confirmPassword } = securityData.value
  if (!currentPassword || !newPassword || !confirmPassword) { message.warning('Please fill in all password fields.'); return }
  if (newPassword !== confirmPassword) { message.error('New passwords do not match.'); return }
  if (newPassword.length < 8) { message.error('Password must be at least 8 characters.'); return }
  savingPassword.value = true
  try {
    await changeAdminPassword({ current_password: currentPassword, new_password: newPassword })
    message.success('Password updated successfully.')
    securityData.value = { currentPassword: '', newPassword: '', confirmPassword: '' }
  } catch (err) {
    message.error(err.response?.data?.detail || 'Failed to update password.')
  } finally {
    savingPassword.value = false
  }
}

// Initials fallback
const initials = computed(() => {
  const parts = fullName.value.trim().split(' ').filter(Boolean)
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  return fullName.value.charAt(0).toUpperCase() || '?'
})
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">

    <!-- ── Page Header ────────────────────────────────────────────────────── -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="Account Settings" />
        <p class="text-sm text-gray-500 mt-1">Manage your admin account</p>
      </div>
    </div>

    <!-- ── Tabs bar ───────────────────────────────────────────────────────── -->
    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs v-model:value="activeTab" type="line" animated class="flex-grow">
        <n-tab-pane name="Profile"  tab="Profile"  />
        <n-tab-pane name="Security" tab="Security" />
      </n-tabs>
    </div>

    <!-- ── Loading ────────────────────────────────────────────────────────── -->
    <div v-if="loadingProfile" class="flex-1 flex flex-col items-center justify-center gap-4">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      <p class="text-gray-500 font-medium">Loading account settings...</p>
    </div>

    <!-- ── Content ────────────────────────────────────────────────────────── -->
    <div v-else class="overflow-y-auto h-[calc(100vh-200px)] pt-6 pr-2">

      <!-- ════════════════ PROFILE TAB ════════════════ -->
      <div v-if="activeTab === 'Profile'" class="flex gap-8 items-start">

        <!-- Left: Profile card -->
        <div class="w-64 flex-shrink-0 flex flex-col items-center gap-4
                    border border-gray-200 rounded-xl p-6 bg-gray-50">
          <n-spin :show="uploadingPhoto">
            <n-avatar
              round
              :size="96"
              :src="photoUrl || undefined"
              :style="{ background: 'linear-gradient(135deg,#0066d4,#011784)', color: 'white', fontSize: '32px', fontWeight: '700' }"
              class="ring-4 ring-white shadow-md"
            >
              <span v-if="!photoUrl">{{ initials }}</span>
            </n-avatar>
          </n-spin>

          <div class="text-center">
            <p class="text-[15px] font-semibold text-gray-800 leading-tight">{{ fullName || '—' }}</p>
            <p class="text-[12px] text-gray-400 mt-0.5">{{ profileData.position || 'No position set' }}</p>
          </div>

          <!-- Role tag -->
          <div
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold tracking-wide"
            :class="auth.isSuperAdmin
              ? 'bg-indigo-100 text-indigo-700 border border-indigo-200'
              : 'bg-pink-100 text-pink-600 border border-pink-200'"
          >
            <!-- Crown icon for superadmin -->
            <svg v-if="auth.isSuperAdmin" class="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2 19h20v2H2v-2zm2-8l4 4 4-6 4 6 4-4v6H4v-6z"/>
            </svg>
            <!-- Shield icon for admin -->
            <svg v-else class="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
            </svg>
            {{ auth.isSuperAdmin ? 'Super Admin' : 'Admin' }}
          </div>

          <div class="w-full border-t border-gray-200 pt-4 flex flex-col gap-2">
            <button
              @click="handleUploadPhoto"
              :disabled="uploadingPhoto"
              class="w-full text-[13px] font-medium text-[#0957FF] border border-[#0957FF]
                     rounded-md py-1.5 hover:bg-blue-50 transition-colors disabled:opacity-50"
            >
              {{ photoUrl ? 'Change Photo' : 'Upload Photo' }}
            </button>
            <button
              v-if="photoUrl"
              @click="handleRemovePhoto"
              :disabled="uploadingPhoto"
              class="w-full text-[13px] font-medium text-red-500 border border-red-300
                     rounded-md py-1.5 hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              Remove Photo
            </button>
          </div>

          <p class="text-[11px] text-gray-400 text-center">JPG, PNG, WebP · Max 2 MB</p>
        </div>

        <!-- Right: Form -->
        <div class="flex-1 flex flex-col gap-8">

          <!-- Section: Personal Info -->
          <div class="border-b border-gray-100 max-w-lg">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Personal Information</h3>
            <div class="flex flex-col gap-5">
              <div class="flex flex-col gap-1.5">
                <label class="text-[13px] font-semibold text-gray-700">Full Name</label>
                <!-- Superadmin: searchable resident select + relink button inline -->
                <template v-if="auth.isSuperAdmin">
                  <div class="flex gap-2">
                    <n-select
                      v-model:value="selectedResidentId"
                      :options="residentOptions"
                      filterable
                      placeholder="Search resident by name…"
                      clearable
                      class="flex-1"
                    />
                    <n-button
                      size="medium"
                      :loading="relinking"
                      :disabled="!selectedResidentId"
                      @click="handleRelinkResident"
                    >
                      Relink
                    </n-button>
                  </div>
                  <p class="text-[11px] text-gray-400">Currently linked to: <span class="font-medium text-indigo-600">{{ fullName || '—' }}</span></p>
                </template>
                <!-- Regular admin: read-only name field -->
                <n-input v-else :value="fullName" disabled placeholder="Full Name" />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="text-[13px] font-semibold text-gray-700">Position</label>
                <n-input v-model:value="profileData.position" placeholder="e.g. Barangay Secretary" />
              </div>
            </div>
          </div>

          <!-- Section: Account -->
          <div class="border-b border-gray-100 max-w-lg">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Account</h3>
            <div class="flex flex-col gap-5">
              <div class="flex flex-col gap-1.5">
                <label class="text-[13px] font-semibold text-gray-700">Username</label>
                <n-input v-model:value="profileData.username" placeholder="Username" />
              </div>
            </div>
          </div>

          <!-- Save profile -->
          <div>
            <n-button type="primary" :loading="savingProfile" @click="handleSaveProfile">
              Save Changes
            </n-button>
          </div>
        </div>
      </div>

      <!-- ════════════════ SECURITY TAB ════════════════ -->
      <div v-if="activeTab === 'Security'" class="flex gap-8 items-start max-w-5xl">

        <!-- Left: Password form -->
        <div class="flex-1 flex flex-col gap-8">

          <div class="border-b border-gray-100">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Change Password</h3>
            <div class="flex flex-col gap-5 max-w-lg">

              <div class="flex flex-col gap-1.5">
                <label class="text-[13px] font-semibold text-gray-700">Current Password</label>
                <n-input
                  v-model:value="securityData.currentPassword"
                  type="password"
                  show-password-on="click"
                  placeholder="Enter current password"
                />
              </div>

              <div class="flex flex-col gap-1.5">
                <label class="text-[13px] font-semibold text-gray-700">New Password</label>
                <n-input
                  v-model:value="securityData.newPassword"
                  type="password"
                  show-password-on="click"
                  placeholder="Enter new password"
                />
              </div>

              <div class="flex flex-col gap-1.5">
                <label class="text-[13px] font-semibold text-gray-700">Confirm New Password</label>
                <n-input
                  v-model:value="securityData.confirmPassword"
                  type="password"
                  show-password-on="click"
                  placeholder="Confirm new password"
                />
              </div>

              <!-- Strength meter -->
              <div v-if="securityData.newPassword" class="flex flex-col gap-2">
                <div class="flex items-center justify-between text-[12px]">
                  <span class="font-semibold text-gray-600">Password strength</span>
                  <span class="font-bold" :style="{ color: passwordStrength.color }">
                    {{ passwordStrength.label }}
                  </span>
                </div>
                <div class="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                  <div
                    class="h-1.5 rounded-full transition-all duration-500"
                    :style="{ width: passwordStrength.width, backgroundColor: passwordStrength.color }"
                  />
                </div>
                <p class="text-[11px] text-gray-400">
                  Use at least 8 characters with uppercase, numbers, and symbols.
                </p>
              </div>

            </div>
          </div>

          <div>
            <n-button type="primary" :loading="savingPassword" @click="handleChangePassword">
              Update Password
            </n-button>
          </div>

        </div>

        <!-- Right: Danger zone card -->
        <div class="w-80 flex-shrink-0">
          <div class="border border-red-200 bg-red-50 rounded-xl p-6 flex flex-col gap-4">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                </svg>
              </div>
              <h3 class="text-[15px] font-bold text-red-700">Danger Zone</h3>
            </div>

            <div class="border-t border-red-200 pt-4 flex flex-col gap-3">
              <div>
                <p class="text-[13px] font-semibold text-red-800">Delete Account</p>
                <p class="text-[12px] text-red-600 mt-1 leading-relaxed">
                  Permanently delete your admin account and all associated data. This cannot be undone.
                </p>
              </div>
              <div class="flex justify-end">
                <n-button
                  size="small"
                  color="#dc2626"
                  text-color="#ffffff"
                  @click="openConfirm('Are you sure you want to delete your account? This cannot be undone.', () => {})"
                >
                  Delete Account
                </n-button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>

  <ConfirmModal
    :show="showConfirmModal"
    :title="confirmTitle"
    confirm-text="Yes"
    cancel-text="Cancel"
    @confirm="handleConfirm"
    @cancel="handleCancel"
  />
</template>