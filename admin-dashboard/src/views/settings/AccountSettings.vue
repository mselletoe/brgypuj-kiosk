<script setup>
/**
 * @file AccountSettings.vue
 * @description Admin account settings page — Profile and Security tabs wired to the backend.
 * Preferences tab is intentionally skipped for now.
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  NTabs,
  NTabPane,
  NInput,
  NButton,
  NAvatar,
  NSpin,
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
} from '@/api/adminService'

const message = useMessage()

// ----------------------------------------------------------------
// Confirm Modal
// ----------------------------------------------------------------
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

// ----------------------------------------------------------------
// UI State
// ----------------------------------------------------------------
const activeTab     = ref('Profile')
const loadingProfile  = ref(false)
const savingProfile   = ref(false)
const savingPassword  = ref(false)
const uploadingPhoto  = ref(false)

// ----------------------------------------------------------------
// Profile Tab
// ----------------------------------------------------------------
const fullName   = ref('')          // read-only — comes from resident record
const profileData = ref({
  username: '',
  position: '',
})
const photoUrl   = ref(null)        // blob URL or null
let   photoBlobUrl = null           // kept so we can revoke it on unmount

// ----------------------------------------------------------------
// Security Tab
// ----------------------------------------------------------------
const securityData = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// ----------------------------------------------------------------
// Password strength
// ----------------------------------------------------------------
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

// ----------------------------------------------------------------
// Load profile on mount
// ----------------------------------------------------------------
onMounted(async () => {
  loadingProfile.value = true
  try {
    const data = await getAdminProfile()

    const { last_name, first_name, middle_name, suffix } = data.resident
    fullName.value = [first_name, middle_name, last_name, suffix]
      .filter(Boolean)
      .join(' ')

    profileData.value.username = data.username
    profileData.value.position = data.position ?? ''

    if (data.has_photo) {
      photoBlobUrl = await getAdminPhotoUrl()
      photoUrl.value = photoBlobUrl
    }
  } catch {
    message.error('Failed to load profile.')
  } finally {
    loadingProfile.value = false
  }
})

// Revoke the blob URL when the component is destroyed to avoid memory leaks
onUnmounted(() => {
  if (photoBlobUrl) URL.revokeObjectURL(photoBlobUrl)
})

// ----------------------------------------------------------------
// Save profile (username + position)
// ----------------------------------------------------------------
const handleSaveProfile = async () => {
  savingProfile.value = true
  try {
    await updateAdminProfile({
      username: profileData.value.username,
      position: profileData.value.position,
    })
    message.success('Profile updated successfully.')
  } catch (err) {
    const detail = err.response?.data?.detail || 'Failed to update profile.'
    message.error(detail)
  } finally {
    savingProfile.value = false
  }
}

// ----------------------------------------------------------------
// Photo upload
// ----------------------------------------------------------------
const handleUploadPhoto = () => {
  const input = document.createElement('input')
  input.type   = 'file'
  input.accept = 'image/jpeg,image/png,image/webp'

  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    if (file.size > 2 * 1024 * 1024) {
      message.warning('Photo must be under 2 MB.')
      return
    }

    uploadingPhoto.value = true
    try {
      await uploadAdminPhoto(file)

      // Revoke old blob URL before replacing
      if (photoBlobUrl) URL.revokeObjectURL(photoBlobUrl)
      photoBlobUrl  = URL.createObjectURL(file)
      photoUrl.value = photoBlobUrl

      message.success('Photo updated.')
    } catch {
      message.error('Failed to upload photo.')
    } finally {
      uploadingPhoto.value = false
    }
  }

  input.click()
}

// ----------------------------------------------------------------
// Photo removal
// ----------------------------------------------------------------
const handleRemovePhoto = () => {
  openConfirm('Are you sure you want to remove your profile photo?', async () => {
    uploadingPhoto.value = true
    try {
      await removeAdminPhoto()
      if (photoBlobUrl) URL.revokeObjectURL(photoBlobUrl)
      photoBlobUrl   = null
      photoUrl.value = null
      message.success('Photo removed.')
    } catch {
      message.error('Failed to remove photo.')
    } finally {
      uploadingPhoto.value = false
    }
  })
}

// ----------------------------------------------------------------
// Change password
// ----------------------------------------------------------------
const handleChangePassword = async () => {
  const { currentPassword, newPassword, confirmPassword } = securityData.value

  if (!currentPassword || !newPassword || !confirmPassword) {
    message.warning('Please fill in all password fields.')
    return
  }
  if (newPassword !== confirmPassword) {
    message.error('New passwords do not match.')
    return
  }
  if (newPassword.length < 8) {
    message.error('New password must be at least 8 characters.')
    return
  }

  savingPassword.value = true
  try {
    await changeAdminPassword({
      current_password: currentPassword,
      new_password:     newPassword,
    })
    message.success('Password updated successfully.')
    securityData.value = { currentPassword: '', newPassword: '', confirmPassword: '' }
  } catch (err) {
    const detail = err.response?.data?.detail || 'Failed to update password.'
    message.error(detail)
  } finally {
    savingPassword.value = false
  }
}
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">

    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="Account Settings" />
        <p class="text-sm text-gray-500 mt-1">Manage your admin account</p>
      </div>
    </div>

    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs v-model:value="activeTab" type="line" animated class="flex-grow">
        <n-tab-pane name="Profile"  tab="Profile"  />
        <n-tab-pane name="Security" tab="Security" />
      </n-tabs>
    </div>

    <!-- Loading spinner while profile fetches -->
    <div v-if="loadingProfile" class="flex justify-center items-center h-48">
      <n-spin size="large" />
    </div>

    <div v-else class="overflow-y-auto h-[calc(100vh-200px)] pt-6 pr-2">

      <!-- ============================================================ -->
      <!-- PROFILE TAB                                                   -->
      <!-- ============================================================ -->
      <div
        v-if="activeTab === 'Profile'"
        class="flex flex-col lg:flex-row gap-12 lg:justify-between items-start"
      >
        <div class="flex-1 w-full max-w-2xl flex flex-col gap-6">

          <!-- Full Name — read-only, sourced from resident record -->
          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800">Name</label>
            <n-input :value="fullName" disabled placeholder="Full Name" />
            <p class="text-[11px] text-gray-400">
              Name is linked to your resident record and cannot be changed here.
            </p>
          </div>

          <!-- Position -->
          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800">Position</label>
            <n-input
              v-model:value="profileData.position"
              placeholder="e.g. Barangay Secretary"
            />
          </div>

          <!-- Username -->
          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800">Username</label>
            <n-input
              v-model:value="profileData.username"
              placeholder="Username"
            />
          </div>

          <div class="pt-4">
            <n-button
              type="info"
              class="px-6"
              :loading="savingProfile"
              @click="handleSaveProfile"
            >
              Save Changes
            </n-button>
          </div>
        </div>

        <!-- Profile Photo -->
        <div class="flex flex-col items-center lg:items-end w-full lg:w-auto lg:mr-12 mt-8 lg:mt-0">
          <div class="flex flex-col w-[320px]">
            <span class="font-['Inter'] font-semibold text-[16px] text-[#373737] mb-6">
              Profile Photo
            </span>

            <div
              class="flex flex-col items-center justify-center w-[320px] h-[320px] p-8
                     border border-gray-200 rounded-md bg-white"
            >
              <n-spin :show="uploadingPhoto">
                <n-avatar
                  round
                  :size="150"
                  :src="photoUrl || undefined"
                  :style="{ backgroundColor: '#e0e7ff', color: '#4f46e5', fontSize: '48px' }"
                  class="mb-6 ring-4 ring-blue-50 shadow-sm"
                >
                  <span v-if="!photoUrl">{{ fullName?.charAt(0)?.toUpperCase() || '?' }}</span>
                </n-avatar>
              </n-spin>

              <span class="font-['Inter'] font-medium text-[13px] text-[#757575] mb-1">
                JPG, PNG, WebP. Max 2MB
              </span>

              <div class="flex flex-row gap-4 mt-1">
                <n-button
                  ghost
                  color="#0957FF"
                  class="font-['Inter'] font-medium text-[15px] rounded-md"
                  :disabled="uploadingPhoto"
                  @click="handleUploadPhoto"
                >
                  Upload Photo
                </n-button>

                <n-button
                  ghost
                  color="#FF2B3A"
                  class="font-['Inter'] font-medium text-[15px] rounded-md"
                  :disabled="!photoUrl || uploadingPhoto"
                  @click="handleRemovePhoto"
                >
                  Remove Photo
                </n-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- SECURITY TAB                                                  -->
      <!-- ============================================================ -->
      <div
        v-if="activeTab === 'Security'"
        class="flex flex-col lg:flex-row gap-12 lg:justify-between items-start"
      >
        <div class="flex-1 w-full max-w-2xl flex flex-col gap-6">

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800">Current Password</label>
            <n-input
              v-model:value="securityData.currentPassword"
              type="password"
              show-password-on="click"
              placeholder="Enter current password"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800">New Password</label>
            <n-input
              v-model:value="securityData.newPassword"
              type="password"
              show-password-on="click"
              placeholder="Enter new password"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800">Confirm New Password</label>
            <n-input
              v-model:value="securityData.confirmPassword"
              type="password"
              show-password-on="click"
              placeholder="Confirm new password"
            />
          </div>

          <!-- Password strength indicator -->
          <div v-if="securityData.newPassword" class="flex flex-col gap-2 pt-1">
            <div class="flex items-center gap-1 text-[12px] font-bold">
              <span class="text-gray-800">Password Strength:</span>
              <span :style="{ color: passwordStrength.color }">
                {{ passwordStrength.label }}
              </span>
            </div>
            <div class="w-full bg-gray-200 h-1 rounded-full">
              <div
                class="h-1 rounded-full transition-all duration-300"
                :style="{ width: passwordStrength.width, backgroundColor: passwordStrength.color }"
              />
            </div>
            <p class="text-[11px] text-gray-400 mt-1">
              Use at least 8 characters with uppercase, lowercase, numbers, and symbols.
            </p>
          </div>

          <div class="pt-4">
            <n-button
              type="info"
              class="px-6"
              :loading="savingPassword"
              @click="handleChangePassword"
            >
              Update Password
            </n-button>
          </div>
        </div>

        <!-- Delete Account card -->
        <div
          class="w-full lg:w-[400px] border-2 border-[#B1202A] bg-[#fff5f5]
                 rounded-lg p-6 flex flex-col lg:mr-16"
        >
          <h3 class="font-['Inter'] font-bold text-[16px] text-[#B1202A] mb-2">
            Delete Account
          </h3>
          <p class="font-['Inter'] font-normal text-[14px] text-[#000000] mb-6 leading-relaxed">
            Permanently delete your admin account and all associated data.
            This action cannot be undone.
          </p>
          <div class="flex justify-end mt-auto">
            <n-button
              color="#FF0000"
              text-color="#FFFFFF"
              class="font-bold font-['Inter']"
              @click="openConfirm('Are you sure you want to delete your account? This cannot be undone.', () => {})"
            >
              Delete Account
            </n-button>
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