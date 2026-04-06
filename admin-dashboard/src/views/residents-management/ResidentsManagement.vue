<script setup>
import { ref, computed, h, watch, onMounted } from "vue";
import {
  NDataTable,
  NInput,
  NButton,
  NCheckbox,
  NPopover,
  NSelect,
  useMessage,
  NEmpty,
} from "naive-ui";
import { FunnelIcon, TrashIcon, CheckIcon } from "@heroicons/vue/24/outline";
import PageTitle from "@/components/shared/PageTitle.vue";
import ResidentModal from "./ResidentModal.vue";
import ConfirmModal from "@/components/shared/ConfirmationModal.vue";
import {
  fetchResidents,
  deleteResident as deleteResidentAPI,
  fetchPuroks,
} from "@/api/residentService";
import { useSearchSync } from "@/composables/useSearchSync";

const message = useMessage();
const residents = ref([]);
const loading = ref(false);
const searchQuery = ref("");
useSearchSync(searchQuery);
const selectedIds = ref([]);
const showDeleteModal = ref(false);
const showFilterPopover = ref(false);
const showResidentModal = ref(false);
const currentResident = ref(null);
const modalMode = ref("add");
const showSingleDeleteModal = ref(false);
const pendingDeleteId = ref(null);

const filterState = ref({
  gender: null,
  purokId: null,
  rfidStatus: null,
});

const genderOptions = [
  { label: "All Genders", value: null },
  { label: "Male", value: "male" },
  { label: "Female", value: "female" },
  { label: "Other", value: "other" },
];

const rfidStatusOptions = [
  { label: "All Statuses", value: null },
  { label: "Active", value: "active" },
  { label: "Inactive", value: "inactive" },
  { label: "No RFID", value: "none" },
];

const purokOptions = ref([{ label: "All Puroks", value: null }]);

const hasActiveFilters = computed(
  () =>
    !!(
      filterState.value.gender ||
      filterState.value.purokId ||
      filterState.value.rfidStatus
    ),
);

function handleFilterClear() {
  filterState.value = { gender: null, purokId: null, rfidStatus: null };
}

async function loadResidents() {
  loading.value = true;
  try {
    const data = await fetchResidents();
    residents.value = data;
  } catch (error) {
    console.error("Failed to load residents:", error);
    message.error("Failed to load residents");
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  loadResidents();
  try {
    const data = await fetchPuroks();
    purokOptions.value = [
      { label: "All Puroks", value: null },
      ...data.map((p) => ({ label: p.purok_name, value: p.id })),
    ];
  } catch {
    // silently fail — filter will still work without puroks
  }
});

const filteredResidents = computed(() => {
  let list = residents.value;

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    list = list.filter(
      (r) =>
        r.full_name.toLowerCase().includes(query) ||
        (r.phone_number && r.phone_number.includes(query)) ||
        (r.rfid_no && r.rfid_no.toLowerCase().includes(query)) ||
        (r.current_address && r.current_address.toLowerCase().includes(query)),
    );
  }

  if (filterState.value.gender) {
    list = list.filter((r) => r.gender === filterState.value.gender);
  }

  if (filterState.value.purokId) {
    list = list.filter((r) => r.purok_id === filterState.value.purokId);
  }

  if (filterState.value.rfidStatus === "active") {
    list = list.filter((r) => r.rfid_no && r.rfid_no !== "Inactive");
  } else if (filterState.value.rfidStatus === "inactive") {
    list = list.filter((r) => r.rfid_no === "Inactive");
  } else if (filterState.value.rfidStatus === "none") {
    list = list.filter((r) => !r.rfid_no);
  }

  return list;
});

const totalCount = computed(() => filteredResidents.value.length);
const selectedCount = computed(() => selectedIds.value.length);

const selectionState = computed(() => {
  if (totalCount.value === 0 || selectedCount.value === 0) return "none";
  if (selectedCount.value < totalCount.value) return "partial";
  return "all";
});

function handleMainSelectToggle() {
  if (selectionState.value === "all" || selectionState.value === "partial") {
    selectedIds.value = [];
  } else {
    selectedIds.value = filteredResidents.value.map((r) => r.id);
  }
}

watch(searchQuery, () => {
  selectedIds.value = [];
});

function openAddModal() {
  modalMode.value = "add";
  currentResident.value = null;
  showResidentModal.value = true;
}

function openViewModal(resident) {
  modalMode.value = "view";
  currentResident.value = resident;
  showResidentModal.value = true;
}

function handleModalClose() {
  showResidentModal.value = false;
  currentResident.value = null;
}

function handleResidentSaved() {
  showResidentModal.value = false;
  currentResident.value = null;
  loadResidents();
}

function requestBulkDelete() {
  if (selectedIds.value.length === 0) {
    message.warning("Please select residents to delete");
    return;
  }
  showDeleteModal.value = true;
}

async function confirmDelete() {
  try {
    await Promise.all(selectedIds.value.map((id) => deleteResidentAPI(id)));
    message.success(
      `${selectedIds.value.length} resident(s) deleted successfully`,
    );
    selectedIds.value = [];
    showDeleteModal.value = false;
    loadResidents();
  } catch (error) {
    console.error("Failed to delete residents:", error);
    message.error("Failed to delete some residents");
  }
}

async function handleDeleteSingle(id) {
  pendingDeleteId.value = id;
  showSingleDeleteModal.value = true;
}

async function confirmSingleDelete() {
  try {
    await deleteResidentAPI(pendingDeleteId.value);
    message.success("Resident deleted successfully");
    showSingleDeleteModal.value = false;
    pendingDeleteId.value = null;
    loadResidents();
  } catch (error) {
    console.error("Failed to delete resident:", error);
    message.error("Failed to delete resident");
  }
}

const columns = computed(() => [
  {
    title: "",
    key: "select",
    width: 50,
    render(row) {
      return h(NCheckbox, {
        checked: selectedIds.value.includes(row.id),
        onUpdateChecked(checked) {
          if (checked) {
            if (!selectedIds.value.includes(row.id))
              selectedIds.value.push(row.id);
          } else {
            selectedIds.value = selectedIds.value.filter((id) => id !== row.id);
          }
        },
      });
    },
  },
  {
    title: "#",
    key: "index",
    width: 50,
    render(_row, index) {
      return index + 1;
    },
  },
  {
    title: "Full Name",
    key: "full_name",
    minWidth: 100,
  },
  {
    title: "Phone Number",
    key: "phone_number",
    width: 150,
    render(row) {
      return row.phone_number || "N/A";
    },
  },
  {
    title: "RFID No.",
    key: "rfid_no",
    width: 150,
    render(row) {
      if (!row.rfid_no) return h("span", { class: "text-gray-400" }, "N/A");
      if (row.rfid_no === "Inactive") {
        return h(
          "span",
          {
            class:
              "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700",
          },
          "Inactive",
        );
      }
      return h("span", { class: "text-blue-600 font-medium" }, row.rfid_no);
    },
  },
  {
    title: "Current Address",
    key: "current_address",
    minWidth: 250,
    render(row) {
      return row.current_address || "N/A";
    },
  },
  {
    title: "Actions",
    key: "actions",
    width: 130,
    render(row) {
      return h("div", { class: "flex gap-2 items-center" }, [
        h(
          NButton,
          { type: "info", size: "small", onClick: () => openViewModal(row) },
          { default: () => "View" },
        ),
        h(
          "button",
          {
            onClick: () => handleDeleteSingle(row.id),
            class: "p-1.5 text-red-500 hover:bg-red-50 rounded transition",
          },
          [h(TrashIcon, { class: "w-5 h-5" })],
        ),
      ]);
    },
  },
]);
</script>

<template>
  <div
    class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden"
  >
    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Residents Information Management" />
        <p class="text-sm text-gray-500 mt-1">Manage Residents Information</p>
      </div>

      <div class="flex items-center gap-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />

        <!-- Filter Popover -->
        <NPopover
          v-model:show="showFilterPopover"
          trigger="click"
          placement="bottom-end"
          :show-arrow="false"
          style="padding: 0"
        >
          <template #trigger>
            <button
              :class="[
                'flex items-center px-4 py-2 border rounded-lg text-sm font-medium transition-colors',
                hasActiveFilters
                  ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50',
              ]"
            >
              <FunnelIcon
                class="w-5 h-5 mr-2"
                :class="hasActiveFilters ? 'text-white' : 'text-gray-500'"
              />
              Filter
            </button>
          </template>

          <div
            class="w-[270px] bg-white rounded-lg overflow-hidden flex flex-col"
          >
            <div class="p-4 border-b border-gray-200">
              <h3 class="text-[16px] font-semibold text-gray-800">
                Filter Residents
              </h3>
            </div>

            <div class="px-6 py-4 space-y-4 flex-1">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >Gender</label
                >
                <NSelect
                  v-model:value="filterState.gender"
                  :options="genderOptions"
                  placeholder="All Genders"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >Purok</label
                >
                <NSelect
                  v-model:value="filterState.purokId"
                  :options="purokOptions"
                  placeholder="All Puroks"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >RFID Status</label
                >
                <NSelect
                  v-model:value="filterState.rfidStatus"
                  :options="rfidStatusOptions"
                  placeholder="All Statuses"
                />
              </div>
            </div>

            <div
              class="flex justify-end space-x-2 p-4 border-t border-gray-200"
            >
              <NButton @click="handleFilterClear" secondary>Clear</NButton>
            </div>
          </div>
        </NPopover>

        <!-- Delete -->
        <div class="relative group inline-block">
          <button
            @click="requestBulkDelete"
            :disabled="selectionState === 'none'"
            class="p-2 border border-red-400 rounded-lg transition-colors"
            :class="
              selectionState === 'none'
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:bg-red-50'
            "
          >
            <TrashIcon class="w-5 h-5 text-red-500" />
          </button>
          <div
            class="absolute -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 ease-in-out bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50"
          >
            Delete
          </div>
        </div>

        <!-- Select All -->
        <div class="relative group inline-block">
          <div
            class="flex items-center border rounded-lg overflow-hidden transition-colors"
            :class="
              selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'
            "
          >
            <button
              @click="handleMainSelectToggle"
              class="p-2 hover:bg-gray-50 flex items-center"
            >
              <div
                class="w-5 h-5 border rounded flex items-center justify-center transition-colors"
                :class="
                  selectionState !== 'none'
                    ? 'bg-blue-600 border-blue-600'
                    : 'border-gray-400'
                "
              >
                <div
                  v-if="selectionState === 'partial'"
                  class="w-2 h-0.5 bg-white"
                ></div>
                <CheckIcon
                  v-if="selectionState === 'all'"
                  class="w-3 h-3 text-white"
                />
              </div>
            </button>
          </div>
          <div
            class="absolute -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 ease-in-out bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50"
          >
            Select All
          </div>
        </div>

        <button
          @click="openAddModal"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
          Register
        </button>
      </div>
    </div>

    <div
      v-if="loading"
      class="flex-1 flex flex-col items-center justify-center gap-4"
    >
      <div
        class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"
      ></div>
      <p class="text-gray-500 font-medium">Loading residents...</p>
    </div>

    <template v-else>
      <div
        v-if="residents.length > 0"
        class="flex-1 overflow-y-auto bg-white rounded-lg border border-gray-200"
      >
        <n-data-table
          :columns="columns"
          :data="filteredResidents"
          :bordered="false"
        />
      </div>

      <div
        v-else
        class="h-full flex flex-col items-center justify-center flex-1"
      >
        <NEmpty description="No residents registered yet">
          <template #extra>
            <NButton type="primary" @click="openAddModal">
              Register Resident
            </NButton>
          </template>
        </NEmpty>
      </div>
    </template>

    <ResidentModal
      :show="showResidentModal"
      :mode="modalMode"
      :resident-id="currentResident?.id"
      @close="handleModalClose"
      @saved="handleResidentSaved"
    />

    <ConfirmModal
      :show="showDeleteModal"
      :title="`Delete ${selectedIds.length} resident(s)?`"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />

    <ConfirmModal
      :show="showSingleDeleteModal"
      title="Delete this resident?"
      description="This will permanently remove the resident and all associated data. This action cannot be undone."
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmSingleDelete"
      @cancel="
        showSingleDeleteModal = false;
        pendingDeleteId = null;
      "
    />
  </div>
</template>
