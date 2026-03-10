<script setup>
/**
 * @file AdminAccounts.vue
 * @description Superadmin-only tab for managing all admin accounts.
 *
 * Features:
 *  - Table: avatar/photo, full name, username, role badge, status, created date, actions
 *  - Online indicator (presence tracked via a shared online-admins store/composable)
 *  - Inline role selector (admin ↔ superadmin)
 *  - Activate / Deactivate toggle with confirmation
 *  - Delete with confirmation
 *  - Add Account modal (wraps POST /admin/auth/register)
 *  - Search filter
 */
import { ref, computed, onMounted } from 'vue'
import { NModal, NSelect, useMessage, NSpin } from 'naive-ui'
import { useAdminAuthStore } from '@/stores/auth'
import {
  getAllAdmins,
  getAdminAccountPhotoUrl,
  setAdminStatus,
  setAdminRole,
  deleteAdminAccount,
} from '@/api/adminAccountsService'
import { registerAdmin } from '@/api/authService'
import { fetchResidentsDropdown } from '@/api/authService'

// ── store / message ──────────────────────────────────────────────────────────
const authStore  = useAdminAuthStore()
const message    = useMessage()

// ── state ────────────────────────────────────────────────────────────────────
const accounts      = ref([])
const photoCache    = ref({})          // { adminId: objectUrl | null }
const loading       = ref(false)
const searchQuery   = ref('')

// Add-account modal
const showAddModal    = ref(false)
const addLoading      = ref(false)
const residents       = ref([])        // dropdown options
const newAccount      = ref({ resident_id: null, username: '', password: '', position: '', system_role: 'admin' })

// Confirmation modal
const confirmModal    = ref({ show: false, title: '', message: '', action: null, danger: false })

// Role options for the inline select and the add modal
const roleOptions = [
  { label: 'Admin',       value: 'admin' },
  { label: 'Super Admin', value: 'superadmin' },
]

// ── computed ─────────────────────────────────────────────────────────────────
const filteredAccounts = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return accounts.value
  return accounts.value.filter(
    a =>
      a.full_name.toLowerCase().includes(q) ||
      a.username.toLowerCase().includes(q) ||
      a.system_role.toLowerCase().includes(q) ||
      (a.position || '').toLowerCase().includes(q),
  )
})

const residentOptions = computed(() =>
  residents.value.map(r => ({ label: r.full_name, value: r.id })),
)

// ── helpers ───────────────────────────────────────────────────────────────────
const isSelf = (adminId) => adminId === authStore.admin?.id

const roleBadgeClass = (role) =>
  role === 'superadmin'
    ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
    : 'bg-sky-50 text-sky-700 border border-sky-200'

const roleLabel = (role) =>
  role === 'superadmin' ? 'Super Admin' : 'Admin'

const avatarInitials = (name) => {
  const parts = (name || '?').split(' ')
  return parts.length >= 2
    ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
    : (name[0] || '?').toUpperCase()
}

const avatarGradient = (id) => {
  const gradients = [
    'from-blue-500 to-indigo-600',
    'from-violet-500 to-purple-600',
    'from-rose-500 to-pink-600',
    'from-amber-500 to-orange-600',
    'from-emerald-500 to-teal-600',
    'from-cyan-500 to-sky-600',
  ]
  return gradients[id % gradients.length]
}

const formatDate = (iso) => {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-PH', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

// ── data loading ──────────────────────────────────────────────────────────────
const loadAccounts = async () => {
  loading.value = true
  try {
    accounts.value = await getAllAdmins()
    // Lazy-load photos in background
    accounts.value.forEach(async (acc) => {
      if (acc.has_photo && photoCache.value[acc.id] === undefined) {
        photoCache.value[acc.id] = await getAdminAccountPhotoUrl(acc.id)
      } else if (!acc.has_photo) {
        photoCache.value[acc.id] = null
      }
    })
  } catch (e) {
    message.error('Failed to load admin accounts.')
  } finally {
    loading.value = false
  }
}

const loadResidents = async () => {
  try {
    residents.value = await fetchResidentsDropdown()
  } catch {
    message.error('Failed to load residents list.')
  }
}

onMounted(() => {
  loadAccounts()
})

// ── confirmation helper ───────────────────────────────────────────────────────
const confirm = ({ title, msg, danger = false, action }) => {
  confirmModal.value = { show: true, title, message: msg, action, danger }
}

const runConfirmedAction = async () => {
  if (!confirmModal.value.action) return
  await confirmModal.value.action()
  confirmModal.value.show = false
}

// ── actions ───────────────────────────────────────────────────────────────────
const toggleStatus = (acc) => {
  const toActive = !acc.is_active
  confirm({
    title: toActive ? 'Activate Account' : 'Deactivate Account',
    msg: toActive
      ? `Activate the account of ${acc.full_name}? They will regain access to the dashboard.`
      : `Deactivate the account of ${acc.full_name}? They will lose access immediately.`,
    danger: !toActive,
    action: async () => {
      try {
        const res = await setAdminStatus(acc.id, toActive)
        acc.is_active = res.is_active
        message.success(res.detail)
      } catch (e) {
        message.error(e.response?.data?.detail || 'Failed to update status.')
      }
    },
  })
}

const changeRole = (acc, newRole) => {
  if (acc.system_role === newRole) return
  const label = newRole === 'superadmin' ? 'Super Admin' : 'Admin'
  confirm({
    title: 'Change Role',
    msg: `Change ${acc.full_name}'s role to ${label}?`,
    danger: false,
    action: async () => {
      try {
        const res = await setAdminRole(acc.id, newRole)
        acc.system_role = res.system_role
        message.success(res.detail)
      } catch (e) {
        // Revert optimistic UI by reloading
        message.error(e.response?.data?.detail || 'Failed to update role.')
        await loadAccounts()
      }
    },
  })
}

const removeAccount = (acc) => {
  confirm({
    title: 'Delete Account',
    msg: `Permanently delete ${acc.full_name}'s account? This cannot be undone.`,
    danger: true,
    action: async () => {
      try {
        const res = await deleteAdminAccount(acc.id)
        accounts.value = accounts.value.filter(a => a.id !== acc.id)
        message.success(res.detail)
      } catch (e) {
        message.error(e.response?.data?.detail || 'Failed to delete account.')
      }
    },
  })
}

// ── add account ───────────────────────────────────────────────────────────────
const openAddModal = async () => {
  newAccount.value = { resident_id: null, username: '', password: '', position: '', system_role: 'admin' }
  showAddModal.value = true
  await loadResidents()
}

const submitAdd = async () => {
  const { resident_id, username, password, system_role } = newAccount.value
  if (!resident_id || !username.trim() || !password.trim()) {
    message.warning('Resident, username, and password are required.')
    return
  }
  if (password.length < 8) {
    message.warning('Password must be at least 8 characters.')
    return
  }
  addLoading.value = true
  try {
    await registerAdmin({
      resident_id,
      username: username.trim(),
      password,
      role: system_role,
    })
    message.success('Admin account created successfully.')
    showAddModal.value = false
    await loadAccounts()
  } catch (e) {
    message.error(e.response?.data?.detail || 'Failed to create account.')
  } finally {
    addLoading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-5 w-full">

    <!-- ── Header ─────────────────────────────────────────────────────────── -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <span class="font-semibold text-[16px] text-[#373737]">Admin Accounts</span>

      <div class="flex items-center gap-3">
        <!-- Search -->
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none"
               xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search accounts..."
            class="border border-gray-200 text-gray-700 rounded-md py-2 pl-9 pr-3 w-[220px] text-[13px]
                   focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition
                   placeholder:text-gray-400"
          />
        </div>

        <!-- Add button -->
        <button
          @click="openAddModal"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm
                 hover:bg-blue-700 active:scale-95 transition flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Account
        </button>
      </div>
    </div>

    <!-- ── Loading skeleton ───────────────────────────────────────────────── -->
    <div v-if="loading" class="flex justify-center py-16">
      <n-spin size="medium" />
    </div>

    <!-- ── Table ──────────────────────────────────────────────────────────── -->
    <div v-else class="overflow-x-auto w-full rounded-lg border border-gray-100">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-gray-50 border-b border-gray-200">
            <th class="py-3 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Admin</th>
            <th class="py-3 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Username</th>
            <th class="py-3 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Role</th>
            <th class="py-3 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Status</th>
            <th class="py-3 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Created</th>
            <th class="py-3 px-4 text-[11px] font-bold text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="acc in filteredAccounts"
            :key="acc.id"
            class="border-b border-gray-100 last:border-none hover:bg-gray-50/70 transition-colors"
          >
            <!-- Avatar + name + position -->
            <td class="py-3.5 px-4">
              <div class="flex items-center gap-3">
                <!-- Photo or gradient initials -->
                <div class="relative flex-shrink-0">
                  <img
                    v-if="photoCache[acc.id]"
                    :src="photoCache[acc.id]"
                    :alt="acc.full_name"
                    class="w-9 h-9 rounded-full object-cover"
                  />
                  <div
                    v-else
                    class="w-9 h-9 rounded-full flex items-center justify-center text-white text-[12px] font-bold bg-gradient-to-br"
                    :class="avatarGradient(acc.id)"
                  >
                    {{ avatarInitials(acc.full_name) }}
                  </div>
                  <!-- Self indicator -->
                  <span
                    v-if="isSelf(acc.id)"
                    class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-blue-500 border-2 border-white"
                    title="This is you"
                  ></span>
                </div>

                <div class="min-w-0">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[13px] font-medium text-gray-800 truncate">{{ acc.full_name }}</span>
                    <span
                      v-if="isSelf(acc.id)"
                      class="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-blue-100 text-blue-600 leading-none"
                    >you</span>
                  </div>
                  <span class="text-[12px] text-gray-400 truncate block">{{ acc.position || '—' }}</span>
                </div>
              </div>
            </td>

            <!-- Username -->
            <td class="py-3.5 px-4 text-[13px] text-gray-600 font-mono">{{ acc.username }}</td>

            <!-- Role — inline selector for non-self rows -->
            <td class="py-3.5 px-4">
              <template v-if="isSelf(acc.id)">
                <span
                  class="inline-block text-[11px] font-semibold px-2.5 py-1 rounded-full"
                  :class="roleBadgeClass(acc.system_role)"
                >
                  {{ roleLabel(acc.system_role) }}
                </span>
              </template>
              <template v-else>
                <div
                  class="inline-flex rounded-md overflow-hidden"
                  :class="acc.system_role === 'superadmin'
                    ? 'bg-indigo-100 border border-indigo-200'
                    : 'bg-sky-50 border border-sky-200'"
                >
                  <n-select
                    :value="acc.system_role"
                    :options="roleOptions"
                    size="small"
                    style="width: 120px"
                    :bordered="false"
                    @update:value="(val) => changeRole(acc, val)"
                    :class="acc.system_role === 'superadmin'
                      ? 'text-indigo-700'
                      : 'text-sky-700'"
                  />
                </div>
              </template>
            </td>

            <!-- Status -->
            <td class="py-3.5 px-4">
              <span
                class="inline-flex items-center gap-1.5 text-[12px] font-medium px-2.5 py-1 rounded-full border"
                :class="acc.is_active
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-gray-50 text-gray-400 border-gray-200'"
              >
                <span
                  class="w-1.5 h-1.5 rounded-full"
                  :class="acc.is_active ? 'bg-emerald-500 animate-pulse' : 'bg-gray-300'"
                ></span>
                {{ acc.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>

            <!-- Created date -->
            <td class="py-3.5 px-4 text-[12px] text-gray-500">{{ formatDate(acc.created_at) }}</td>

            <!-- Actions -->
            <td class="py-3.5 px-4">
              <div class="flex items-center gap-2">
                <!-- Activate / Deactivate — hidden for self -->
                <button
                  v-if="!isSelf(acc.id)"
                  @click="toggleStatus(acc)"
                  class="text-[12px] font-medium px-3 py-1 rounded-md border transition-colors"
                  :class="acc.is_active
                    ? 'border-red-200 text-red-600 hover:bg-red-50'
                    : 'border-emerald-200 text-emerald-600 hover:bg-emerald-50'"
                >
                  {{ acc.is_active ? 'Deactivate' : 'Activate' }}
                </button>

                <!-- Delete — hidden for self -->
                <button
                  v-if="!isSelf(acc.id)"
                  @click="removeAccount(acc)"
                  class="p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                  title="Delete account"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7V4h6v3M4 7h16" />
                  </svg>
                </button>

                <!-- Self: locked label -->
                <span v-if="isSelf(acc.id)" class="text-[12px] text-gray-400 italic pr-1">Your account</span>
              </div>
            </td>
          </tr>

          <!-- Empty state -->
          <tr v-if="filteredAccounts.length === 0">
            <td colspan="6" class="py-12 text-center">
              <div class="flex flex-col items-center gap-2 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M17 20h5v-2a4 4 0 00-4-4h-1M9 20H4v-2a4 4 0 014-4h1m4-4a4 4 0 100-8 4 4 0 000 8zm6 0a3 3 0 100-6 3 3 0 000 6zM3 14a3 3 0 100-6 3 3 0 000 6z" />
                </svg>
                <span class="text-sm">{{ searchQuery ? 'No accounts match your search.' : 'No admin accounts found.' }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ── Add Account Modal ──────────────────────────────────────────────── -->
    <n-modal
      v-model:show="showAddModal"
      preset="card"
      title="Add Admin Account"
      style="width: 500px;"
      :bordered="false"
      :mask-closable="!addLoading"
    >
      <div class="flex flex-col gap-4">

        <!-- Resident picker -->
        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">
            Link to Resident <span class="text-red-500">*</span>
          </label>
          <n-select
            v-model:value="newAccount.resident_id"
            :options="residentOptions"
            placeholder="Search resident..."
            filterable
            clearable
          />
          <p class="text-[11px] text-gray-400">The admin account will be linked to this resident's profile.</p>
        </div>

        <!-- Username -->
        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">
            Username <span class="text-red-500">*</span>
          </label>
          <input
            v-model="newAccount.username"
            placeholder="e.g. jdelacruz"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px]
                   focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          />
        </div>

        <!-- Position (optional) -->
        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Position <span class="text-gray-400 font-normal">(optional)</span></label>
          <input
            v-model="newAccount.position"
            placeholder="e.g. Barangay Secretary"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px]
                   focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          />
        </div>

        <!-- Role -->
        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Role</label>
          <n-select v-model:value="newAccount.system_role" :options="roleOptions" />
        </div>

        <!-- Temporary password -->
        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">
            Temporary Password <span class="text-red-500">*</span>
          </label>
          <input
            v-model="newAccount.password"
            type="password"
            placeholder="Minimum 8 characters"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px]
                   focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
          />
          <p class="text-[11px] text-gray-400">The admin should change this on first login.</p>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 mt-1">
          <button
            :disabled="addLoading"
            @click="showAddModal = false"
            class="px-4 py-2 text-[13px] font-medium text-gray-600 border border-gray-200 rounded-md
                   hover:bg-gray-50 transition disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            :disabled="addLoading"
            @click="submitAdd"
            class="px-4 py-2 text-[13px] font-medium text-white bg-blue-600 rounded-md
                   hover:bg-blue-700 transition flex items-center gap-2 disabled:opacity-60"
          >
            <svg v-if="addLoading" class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            {{ addLoading ? 'Creating…' : 'Create Account' }}
          </button>
        </div>
      </div>
    </n-modal>

    <!-- ── Confirmation Modal ─────────────────────────────────────────────── -->
    <n-modal
      v-model:show="confirmModal.show"
      preset="card"
      :title="confirmModal.title"
      style="width: 400px;"
      :bordered="false"
    >
      <p class="text-[14px] text-gray-600 leading-relaxed">{{ confirmModal.message }}</p>
      <div class="flex justify-end gap-3 mt-5">
        <button
          @click="confirmModal.show = false"
          class="px-4 py-2 text-[13px] font-medium text-gray-600 border border-gray-200 rounded-md hover:bg-gray-50 transition"
        >
          Cancel
        </button>
        <button
          @click="runConfirmedAction"
          class="px-4 py-2 text-[13px] font-medium text-white rounded-md transition"
          :class="confirmModal.danger ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'"
        >
          Confirm
        </button>
      </div>
    </n-modal>

  </div>
</template>