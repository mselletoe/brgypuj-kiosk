<script setup>
/**
 * @file AdminAccounts.vue
 * @description Manage admin accounts — view, add, deactivate admins.
 */
import { ref, computed } from "vue";
import { NButton, NModal, NSelect, useMessage } from "naive-ui";

const message = useMessage();
const showAddModal = ref(false);
const searchQuery  = ref("");

const roleOptions = [
  { label: "Super Admin", value: "super_admin" },
  { label: "Admin",       value: "admin" },
];

// Mock data — replace with API call
const accounts = ref([
  { id: 1, name: "Juan dela Cruz",  email: "juan@brgy.gov.ph",  role: "super_admin", status: "active",   lastLogin: "Mar 6, 2026" },
  { id: 2, name: "Maria Santos",    email: "maria@brgy.gov.ph", role: "admin",       status: "active",   lastLogin: "Mar 5, 2026" },
]);

const newAccount = ref({ name: "", email: "", role: "admin", password: "" });

const filteredAccounts = computed(() => {
  const q = searchQuery.value.toLowerCase();
  if (!q) return accounts.value;
  return accounts.value.filter(
    (a) =>
      a.name.toLowerCase().includes(q) ||
      a.email.toLowerCase().includes(q) ||
      a.role.toLowerCase().includes(q)
  );
});

const roleBadge = (role) => {
  const map = {
    super_admin: "bg-indigo-50 text-indigo-700 border border-indigo-200",
    admin:       "bg-pink-50 text-pink-700 border border-pink-200"
  };
  return map[role] || "bg-gray-100 text-gray-600 border border-gray-200";
};

const roleLabel = (role) => {
  const map = { super_admin: "Super Admin", admin: "Admin" };
  return map[role] || role;
};

const toggleStatus = (account) => {
  account.status = account.status === "active" ? "inactive" : "active";
  message.success(`Account ${account.status === "active" ? "activated" : "deactivated"}.`);
};

const submitAdd = () => {
  if (!newAccount.value.name.trim() || !newAccount.value.email.trim()) {
    message.warning("Name and email are required.");
    return;
  }
  accounts.value.unshift({
    id: Date.now(),
    name:      newAccount.value.name.trim(),
    email:     newAccount.value.email.trim(),
    role:      newAccount.value.role,
    status:    "active",
    lastLogin: "—",
  });
  showAddModal.value = false;
  newAccount.value = { name: "", email: "", role: "admin", password: "" };
  message.success("Admin account created.");
};
</script>

<template>
  <div class="flex flex-col gap-5 w-full">

    <!-- Header row -->
    <div class="flex items-center justify-between">
      <span class="font-semibold text-[16px] text-[#373737]">Admin Accounts</span>
      <div class="flex items-center gap-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search accounts..."
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[220px] text-[13px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition placeholder:text-gray-400"
        />
        <button
          @click="showAddForm = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto w-full">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="border-b border-gray-200">
            <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Name</th>
            <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Email</th>
            <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Role</th>
            <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Status</th>
            <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Last Login</th>
            <th class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="acc in filteredAccounts"
            :key="acc.id"
            class="border-b border-gray-100 last:border-none hover:bg-gray-50 transition-colors"
          >
            <td class="py-4 px-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-[12px] font-bold flex-shrink-0">
                  {{ acc.name.charAt(0) }}
                </div>
                <span class="text-[13px] font-medium text-gray-800">{{ acc.name }}</span>
              </div>
            </td>
            <td class="py-4 px-4 text-[13px] text-gray-600">{{ acc.email }}</td>
            <td class="py-4 px-4">
              <span class="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize" :class="roleBadge(acc.role)">
                {{ roleLabel(acc.role) }}
              </span>
            </td>
            <td class="py-4 px-4">
              <span class="inline-flex items-center gap-1.5 text-[13px]" :class="acc.status === 'active' ? 'text-emerald-600' : 'text-gray-400'">
                <span class="w-2 h-2 rounded-full" :class="acc.status === 'active' ? 'bg-emerald-500' : 'bg-gray-300'"></span>
                {{ acc.status === 'active' ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="py-4 px-4 text-[13px] text-gray-500">{{ acc.lastLogin }}</td>
            <td class="py-4 px-4">
              <button
                @click="toggleStatus(acc)"
                class="text-[12px] font-medium px-3 py-1 rounded-md border transition-colors"
                :class="acc.status === 'active'
                  ? 'border-red-200 text-red-600 hover:bg-red-50'
                  : 'border-emerald-200 text-emerald-600 hover:bg-emerald-50'"
              >
                {{ acc.status === 'active' ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
          <tr v-if="filteredAccounts.length === 0">
            <td colspan="6" class="py-8 text-center text-gray-500 text-sm">No accounts found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Account Modal -->
    <n-modal v-model:show="showAddModal" preset="card" title="Add Admin Account" style="width: 480px;" :bordered="false">
      <div class="flex flex-col gap-4">

        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Full Name</label>
          <input v-model="newAccount.name" placeholder="e.g. Juan dela Cruz"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition" />
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Email Address</label>
          <input v-model="newAccount.email" type="email" placeholder="e.g. name@brgy.gov.ph"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition" />
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Role</label>
          <n-select v-model:value="newAccount.role" :options="roleOptions" />
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-[13px] font-medium text-gray-600">Temporary Password</label>
          <input v-model="newAccount.password" type="password" placeholder="Set a temporary password"
            class="border border-gray-200 rounded-md px-3 py-2 text-[14px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition" />
        </div>

        <div class="flex justify-end gap-3 mt-2">
          <n-button @click="showAddModal = false">Cancel</n-button>
          <n-button type="primary" @click="submitAdd">Create Account</n-button>
        </div>
      </div>
    </n-modal>

  </div>
</template>