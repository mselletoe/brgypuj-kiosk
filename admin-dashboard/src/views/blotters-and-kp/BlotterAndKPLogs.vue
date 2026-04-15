<script setup>
import { ref, computed, h, watch, onMounted } from "vue";
import {
  NDataTable,
  NInput,
  NButton,
  NCheckbox,
  NModal,
  NSelect,
  NDatePicker,
  useMessage,
  NEmpty,
  NPopover,
  NTag,
} from "naive-ui";
import {
  FunnelIcon,
  TrashIcon,
  CheckIcon,
  XMarkIcon,
  CheckCircleIcon,
  ArrowPathIcon,
} from "@heroicons/vue/24/outline";
import PageTitle from "@/components/shared/PageTitle.vue";
import ConfirmModal from "@/components/shared/ConfirmationModal.vue";
import {
  getAllBlotters,
  createBlotter,
  updateBlotter,
  deleteBlotter,
  bulkDeleteBlotters,
  resolveBlotter,
  reopenBlotter,
} from "@/api/blotterService";
import { fetchResidents } from "@/api/residentService";
import { useSearchSync } from "@/composables/useSearchSync";

const message = useMessage();
const blotters = ref([]);
const loading = ref(false);
const searchQuery = ref("");
useSearchSync(searchQuery);
const selectedIds = ref([]);
const showDeleteModal = ref(false);
const showBlotterModal = ref(false);
const showFilterPopover = ref(false);
const currentBlotter = ref(null);
const modalMode = ref("add");
const saving = ref(false);
const formData = ref({});
const residents = ref([]);
const showResolveModal = ref(false);
const showReopenModal = ref(false);
const pendingActionId = ref(null);
const actionLoading = ref(false);

const filterState = ref({
  incidentType: null,
  incidentDateRange: null,
  status: null,
});

const hasActiveFilters = computed(
  () =>
    !!(
      filterState.value.incidentType ||
      filterState.value.incidentDateRange ||
      filterState.value.status
    ),
);

function handleFilterClear() {
  filterState.value = { incidentType: null, incidentDateRange: null, status: null };
}

async function loadBlotters() {
  loading.value = true;
  try {
    const data = await getAllBlotters();
    blotters.value = data.map(normalizeRecord);
  } catch {
    message.error("Failed to load blotter records");
  } finally {
    loading.value = false;
  }
}

async function loadResidents() {
  try {
    const data = await fetchResidents();
    residents.value = data;
  } catch {
    message.error("Failed to load residents");
  }
}

onMounted(() => {
  loadBlotters();
  loadResidents();
});

const residentOptions = computed(() =>
  residents.value.map((r) => ({
    label:
      r.full_name ||
      [r.first_name, r.middle_name, r.last_name].filter(Boolean).join(" ") ||
      `Resident #${r.id}`,
    value: r.id,
    resident: r,
  })),
);

function handleComplainantSelect(residentId) {
  if (!residentId) {
    formData.value.complainant_id = null;
    formData.value.complainant_name = "";
    formData.value.complainant_age = null;
    formData.value.complainant_address = "";
    return;
  }
  const option = residentOptions.value.find((o) => o.value === residentId);
  if (!option) return;
  const r = option.resident;
  formData.value.complainant_id = r.id;
  formData.value.complainant_name = option.label;
  formData.value.complainant_age = r.age ?? null;
  formData.value.complainant_address = r.address ?? "";
}

function handleRespondentSelect(residentId) {
  if (!residentId) {
    formData.value.respondent_id = null;
    formData.value.respondent_name = "";
    formData.value.respondent_age = null;
    formData.value.respondent_address = "";
    return;
  }
  const option = residentOptions.value.find((o) => o.value === residentId);
  if (!option) return;
  const r = option.resident;
  formData.value.respondent_id = r.id;
  formData.value.respondent_name = option.label;
  formData.value.respondent_age = r.age ?? null;
  formData.value.respondent_address = r.address ?? "";
}

function normalizeRecord(record) {
  return {
    ...record,
    date: record.incident_date
      ? new Date(record.incident_date).getTime()
      : null,
    time: record.incident_time ? record.incident_time.slice(0, 5) : "",
  };
}

function toApiPayload(form) {
  const payload = { ...form };
  if (form.date) {
    payload.incident_date = new Date(form.date).toISOString().split("T")[0];
  } else {
    payload.incident_date = null;
  }
  payload.incident_time = form.time || null;
  const remove = [
    "date",
    "time",
    "id",
    "blotter_no",
    "created_at",
    "status",
    "complainant_resident_name",
    "complainant_resident_first_name",
    "complainant_resident_middle_name",
    "complainant_resident_last_name",
    "complainant_resident_phone",
    "respondent_resident_name",
    "respondent_resident_first_name",
    "respondent_resident_middle_name",
    "respondent_resident_last_name",
    "respondent_resident_phone",
  ];
  remove.forEach((k) => delete payload[k]);
  return payload;
}

const filteredBlotters = computed(() => {
  let list = blotters.value;

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    list = list.filter(
      (b) =>
        b.blotter_no.toLowerCase().includes(query) ||
        b.complainant_name.toLowerCase().includes(query) ||
        (b.incident_type && b.incident_type.toLowerCase().includes(query)),
    );
  }

  if (filterState.value.incidentType) {
    list = list.filter(
      (b) => b.incident_type === filterState.value.incidentType,
    );
  }

  if (filterState.value.incidentDateRange) {
    const [start, end] = filterState.value.incidentDateRange;
    list = list.filter(
      (b) => b.date && b.date >= start && b.date <= end + 86399999,
    );
  }

  if (filterState.value.status) {
    list = list.filter((b) => b.status === filterState.value.status);
  }

  return list;
});

const totalCount = computed(() => filteredBlotters.value.length);
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
    selectedIds.value = filteredBlotters.value.map((b) => b.id);
  }
}

watch(searchQuery, () => {
  selectedIds.value = [];
});

function formatDate(timestamp) {
  if (!timestamp) return "N/A";
  return new Date(timestamp).toLocaleDateString("en-PH", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function openAddModal() {
  modalMode.value = "add";
  currentBlotter.value = null;
  showBlotterModal.value = true;
}

function openViewModal(blotter) {
  modalMode.value = "view";
  currentBlotter.value = { ...blotter };
  showBlotterModal.value = true;
}

function handleModalClose() {
  showBlotterModal.value = false;
  currentBlotter.value = null;
}

function requestResolve(id) {
  pendingActionId.value = id;
  showResolveModal.value = true;
}

function requestReopen(id) {
  pendingActionId.value = id;
  showReopenModal.value = true;
}

async function confirmResolve() {
  actionLoading.value = true;
  try {
    const updated = await resolveBlotter(pendingActionId.value);
    const idx = blotters.value.findIndex((b) => b.id === pendingActionId.value);
    if (idx !== -1) blotters.value[idx] = normalizeRecord(updated);
    message.success("Blotter record marked as resolved. Respondent's clean record has been restored.");
  } catch (err) {
    const detail = err?.response?.data?.detail;
    message.error(detail || "Failed to resolve blotter record");
  } finally {
    actionLoading.value = false;
    showResolveModal.value = false;
    pendingActionId.value = null;
  }
}

async function confirmReopen() {
  actionLoading.value = true;
  try {
    const updated = await reopenBlotter(pendingActionId.value);
    const idx = blotters.value.findIndex((b) => b.id === pendingActionId.value);
    if (idx !== -1) blotters.value[idx] = normalizeRecord(updated);
    message.success("Blotter record re-opened.");
  } catch (err) {
    const detail = err?.response?.data?.detail;
    message.error(detail || "Failed to re-open blotter record");
  } finally {
    actionLoading.value = false;
    showReopenModal.value = false;
    pendingActionId.value = null;
  }
}

function requestBulkDelete() {
  if (selectedIds.value.length === 0) {
    message.warning("Please select records to delete");
    return;
  }
  showDeleteModal.value = true;
}

async function confirmDelete() {
  try {
    await bulkDeleteBlotters(selectedIds.value);
    blotters.value = blotters.value.filter(
      (b) => !selectedIds.value.includes(b.id),
    );
    message.success(
      `${selectedIds.value.length} record(s) deleted successfully`,
    );
    selectedIds.value = [];
    showDeleteModal.value = false;
  } catch {
    message.error("Failed to delete some records");
  }
}

async function handleDeleteSingle(id) {
  try {
    await deleteBlotter(id);
    blotters.value = blotters.value.filter((b) => b.id !== id);
    message.success("Blotter record deleted successfully");
  } catch {
    message.error("Failed to delete record");
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
    title: "Blotter No.",
    key: "blotter_no",
    width: 130,
    render(row) {
      return h("span", { class: "font-bold text-blue-700" }, row.blotter_no);
    },
  },
  { title: "Complainant", key: "complainant_name", minWidth: 160 },
  {
    title: "Respondent",
    key: "respondent_name",
    minWidth: 160,
    render(row) {
      return row.respondent_name || "N/A";
    },
  },
  {
    title: "Date",
    key: "date",
    width: 140,
    render(row) {
      return formatDate(row.date);
    },
  },
  {
    title: "Type of Incident",
    key: "incident_type",
    minWidth: 160,
    render(row) {
      return row.incident_type || "N/A";
    },
  },
  {
    title: "Status",
    key: "status",
    width: 120,
    render(row) {
      const isResolved = row.status === "resolved";
      return h(
        NTag,
        {
          type: isResolved ? "success" : "warning",
          size: "small",
          round: true,
        },
        { default: () => (isResolved ? "Resolved" : "Unresolved") },
      );
    },
  },
  {
    title: "Actions",
    key: "actions",
    width: 170,
    render(row) {
      const isResolved = row.status === "resolved";
      return h("div", { class: "flex gap-1.5 items-center" }, [
        h(
          NButton,
          { type: "info", size: "small", onClick: () => openViewModal(row) },
          { default: () => "View" },
        ),
        isResolved
          ? h(
              "button",
              {
                title: "Re-open record",
                onClick: () => requestReopen(row.id),
                class:
                  "p-1.5 text-amber-500 hover:bg-amber-50 rounded transition",
              },
              [h(ArrowPathIcon, { class: "w-4 h-4" })],
            )
          : h(
              "button",
              {
                title: "Mark as resolved",
                onClick: () => requestResolve(row.id),
                class:
                  "p-1.5 text-green-600 hover:bg-green-50 rounded transition",
              },
              [h(CheckCircleIcon, { class: "w-4 h-4" })],
            ),
        // Delete button
        h(
          "button",
          {
            onClick: () => handleDeleteSingle(row.id),
            class: "p-1.5 text-red-500 hover:bg-red-50 rounded transition",
          },
          [h(TrashIcon, { class: "w-4 h-4" })],
        ),
      ]);
    },
  },
]);

const incidentTypeOptions = [
  {
    label: "Physical Altercation (Pananakit o Pisikal na Pag-aaway)",
    value: "Physical Altercation",
  },
  {
    label: "Verbal Dispute (Pagmumura o Pag-aaway sa Salita)",
    value: "Verbal Dispute",
  },
  {
    label: "Property Dispute (Away sa Lupa o Hangganan)",
    value: "Property Dispute",
  },
  { label: "Unpaid Debt (Utang na Hindi Nababayaran)", value: "Unpaid Debt" },
  {
    label: "Noise Complaint (Reklamo sa Ingay (Videoke, atbp.))",
    value: "Noise Complaint",
  },
  { label: "Theft (Pagnanakaw)", value: "Theft" },
  {
    label: "Trespassing (Pagpasok nang Walang Pahintulot)",
    value: "Trespassing",
  },
  {
    label: "Domestic Disturbance (Gulo sa Loob ng Tahanan)",
    value: "Domestic Disturbance",
  },
  {
    label: "Lost Item/Document (Nawawalang Gamit o Dokumento)",
    value: "Lost Item/Document",
  },
  {
    label: "Vehicular Accident (Aksidente sa Sasakyan)",
    value: "Vehicular Accident",
  },
  {
    label: "Stray Animal/Pet Issue (Reklamo sa Pagala-galang Hayop)",
    value: "Stray Animal/Pet Issue",
  },
  {
    label: "Vandalism (Paninira ng Ari-arian / Graffitti)",
    value: "Vandalism",
  },
  { label: "Threats (Pananakot)", value: "Threats" },
  { label: "Slander/Libel (Paninirang-puri)", value: "Slander" },
  { label: "Other", value: "Other" },
];

const incidentTypeFilterOptions = computed(() => [
  { label: "All Incident Types", value: null },
  ...incidentTypeOptions,
]);

const statusFilterOptions = [
  { label: "All Statuses", value: null },
  { label: "Active", value: "active" },
  { label: "Resolved", value: "resolved" },
];

function emptyForm() {
  return {
    complainant_id: null,
    complainant_name: "",
    complainant_age: null,
    complainant_address: "",
    respondent_id: null,
    respondent_name: "",
    respondent_age: null,
    respondent_address: "",
    date: new Date().getTime(),
    time: "",
    incident_place: "",
    incident_type: null,
    narrative: "",
    recorded_by: "",
    contact_no: "",
  };
}

watch(
  () => showBlotterModal.value,
  (val) => {
    if (val) {
      formData.value =
        modalMode.value === "view" && currentBlotter.value
          ? { ...currentBlotter.value }
          : emptyForm();
    }
  },
);

async function handleSave() {
  if (!formData.value.complainant_name) {
    message.error("Complainant name is required");
    return;
  }
  saving.value = true;
  try {
    const payload = toApiPayload(formData.value);
    if (modalMode.value === "add") {
      const created = await createBlotter(payload);
      blotters.value.unshift(normalizeRecord(created));
      message.success("Blotter record added successfully");
    } else {
      const updated = await updateBlotter(currentBlotter.value.id, payload);
      const idx = blotters.value.findIndex(
        (b) => b.id === currentBlotter.value.id,
      );
      if (idx !== -1) blotters.value[idx] = normalizeRecord(updated);
      message.success("Blotter record updated successfully");
    }
    showBlotterModal.value = false;
  } catch {
    message.error(
      modalMode.value === "add"
        ? "Failed to add blotter record"
        : "Failed to update blotter record",
    );
  } finally {
    saving.value = false;
  }
}

const modalTitle = computed(() => {
  if (modalMode.value === "add") return "Add New Blotter Record";
  return formData.value.blotter_no
    ? `Blotter # ${formData.value.blotter_no}`
    : "Blotter Record";
});
</script>

<template>
  <div class="flex flex-col p-4 sm:p-6 bg-white rounded-md w-full h-full overflow-hidden">

    <!-- HEADER -->
    <div class="grid grid-cols-1 md:grid-cols-[1fr_auto] items-center gap-4 mb-6">

      <!-- TITLE -->
      <div class="min-w-0">
        <PageTitle title="Blotter and KP Logs" />
        <p class="text-sm text-gray-500 mt-1">Manage Blotter and KP logs for residents</p>
      </div>

      <!-- CONTROLS -->
      <div class="flex flex-nowrap items-center justify-start md:justify-end gap-3 w-full">

        <!-- SEARCH -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 flex-1 md:flex-none md:w-[180px] lg:w-[250px] min-w-0 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />

        <!-- ACTION BUTTONS -->
        <div class="flex items-center gap-2 sm:gap-3">

          <!-- FILTER POPOVER -->
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
                  'flex items-center px-3 py-2 border rounded-lg text-sm font-medium transition-colors',
                  hasActiveFilters
                    ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50',
                ]"
              >
                <FunnelIcon
                  class="w-5 h-5 sm:mr-2"
                  :class="hasActiveFilters ? 'text-white' : 'text-gray-500'"
                />
                <span class="hidden sm:inline">Filter</span>
              </button>
            </template>

            <div class="w-[270px] bg-white rounded-lg overflow-hidden flex flex-col">
              <div class="p-4 border-b border-gray-200">
                <h3 class="text-[16px] font-semibold text-gray-800">Filter Blotter Records</h3>
              </div>
              <div class="px-6 py-4 space-y-4 flex-1">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Incident Type</label>
                  <NSelect v-model:value="filterState.incidentType" :options="incidentTypeFilterOptions" placeholder="All Incident Types" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <NSelect v-model:value="filterState.status" :options="statusFilterOptions" placeholder="All Statuses" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Incident Date Range</label>
                  <NDatePicker
                    v-model:value="filterState.incidentDateRange"
                    type="daterange"
                    clearable
                    class="w-full"
                    format="dd/MM/yyyy"
                    :placeholder="['Start date', 'End date']"
                  />
                </div>
              </div>
              <div class="flex justify-end space-x-2 p-4 border-t border-gray-200">
                <NButton @click="handleFilterClear" secondary>Clear</NButton>
              </div>
            </div>
          </NPopover>

          <!-- DELETE -->
          <div class="relative group inline-block">
            <button
              @click="requestBulkDelete"
              :disabled="selectionState === 'none'"
              class="p-2 border border-red-400 rounded-lg transition-colors"
              :class="selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-50'"
            >
              <TrashIcon class="w-5 h-5 text-red-500" />
            </button>
            <div class="absolute hidden sm:block -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">
              Delete
            </div>
          </div>

          <!-- SELECT ALL -->
          <div class="relative group inline-block">
            <div
              class="flex items-center border rounded-lg overflow-hidden transition-colors"
              :class="selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'"
            >
              <button
                @click="handleMainSelectToggle"
                class="p-2 hover:bg-gray-50 flex items-center"
              >
                <div
                  class="w-5 h-5 border rounded flex items-center justify-center transition-colors"
                  :class="selectionState !== 'none' ? 'bg-blue-600 border-blue-600' : 'border-gray-400'"
                >
                  <div v-if="selectionState === 'partial'" class="w-2 h-0.5 bg-white"></div>
                  <CheckIcon v-if="selectionState === 'all'" class="w-3 h-3 text-white" />
                </div>
              </button>
            </div>
            <div class="absolute hidden sm:block -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">
              Select All
            </div>
          </div>

          <!-- ADD -->
          <button
            @click="openAddModal"
            class="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2 whitespace-nowrap"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span class="hidden sm:inline">Add</span>
          </button>

        </div>
      </div>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center gap-4">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      <p class="text-gray-500 font-medium">Loading blotter records...</p>
    </div>

    <template v-else>

      <!-- TABLE -->
      <div
        v-if="blotters.length > 0"
        class="flex-1 overflow-y-auto bg-white rounded-lg border border-gray-200"
      >
        <n-data-table :columns="columns" :data="filteredBlotters" :bordered="false" />
      </div>

      <!-- EMPTY STATE -->
      <div v-else class="h-full flex flex-col items-center justify-center flex-1">
        <NEmpty description="No blotter records yet">
          <template #extra>
            <NButton type="primary" @click="openAddModal">Add Record</NButton>
          </template>
        </NEmpty>
      </div>

    </template>

    <!-- BLOTTER MODAL -->
    <NModal :show="showBlotterModal" @update:show="handleModalClose" :mask-closable="false">
      <div
        class="w-[820px] max-w-[95vw] max-h-[90vh] overflow-hidden bg-white rounded-xl shadow-lg flex flex-col"
        role="dialog"
        aria-modal="true"
      >
        <div class="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
          <div class="flex items-center gap-3">
            <h2 class="text-lg font-semibold text-gray-800">{{ modalTitle }}</h2>
            <NTag
              v-if="modalMode === 'view' && formData.status"
              :type="formData.status === 'resolved' ? 'success' : 'warning'"
              size="small"
              round
            >
              {{ formData.status === "resolved" ? "Resolved" : "Active" }}
            </NTag>
          </div>
          <button @click="handleModalClose" class="p-1 rounded hover:bg-gray-200 transition">
            <XMarkIcon class="w-6 h-6 text-gray-500" />
          </button>
        </div>

        <div class="px-6 py-5 overflow-y-auto space-y-5">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Blotter No.</label>
              <n-input :value="modalMode === 'view' ? formData.blotter_no : 'Auto-generated'" :disabled="true" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Date</label>
              <NDatePicker v-model:value="formData.date" type="date" placeholder="Select Date" class="w-full" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Time</label>
              <n-input v-model:value="formData.time" placeholder="e.g. 14:30" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Place of Incident</label>
            <n-input v-model:value="formData.incident_place" placeholder="Location of the incident" />
          </div>

          <!-- COMPLAINANT -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Complainant (Nagreklamo)</p>
            <div class="mb-3">
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Registered Resident
                <span class="text-gray-400 font-normal">(optional — select to auto-fill)</span>
              </label>
              <NSelect
                v-model:value="formData.complainant_id"
                :options="residentOptions"
                filterable
                clearable
                placeholder="Search resident by name..."
                @update:value="handleComplainantSelect"
              />
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Full Name <span class="text-red-500">*</span></label>
                <n-input v-model:value="formData.complainant_name" placeholder="Full Name" :disabled="!!formData.complainant_id" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Age</label>
                <n-input v-model:value="formData.complainant_age" placeholder="Age" type="number" :disabled="!!formData.complainant_id" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Address</label>
                <n-input v-model:value="formData.complainant_address" placeholder="Address" :disabled="!!formData.complainant_id" />
              </div>
            </div>
          </div>

          <!-- RESPONDENT -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Respondent (Inireklamo)</p>
            <div class="mb-3">
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Registered Resident
                <span class="text-gray-400 font-normal">(optional — select to auto-fill)</span>
              </label>
              <NSelect
                v-model:value="formData.respondent_id"
                :options="residentOptions"
                filterable
                clearable
                placeholder="Search resident by name..."
                @update:value="handleRespondentSelect"
              />
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
                <n-input v-model:value="formData.respondent_name" placeholder="Full Name" :disabled="!!formData.respondent_id" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Age</label>
                <n-input v-model:value="formData.respondent_age" placeholder="Age" type="number" :disabled="!!formData.respondent_id" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Address</label>
                <n-input v-model:value="formData.respondent_address" placeholder="Address" :disabled="!!formData.respondent_id" />
              </div>
            </div>
          </div>

          <!-- INCIDENT DETAILS -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Incident Details</p>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Type of Incident</label>
              <NSelect v-model:value="formData.incident_type" :options="incidentTypeOptions" placeholder="Select Type" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Narrative of Events</label>
              <n-input v-model:value="formData.narrative" type="textarea" placeholder="Describe what happened..." :rows="4" />
            </div>
          </div>

          <!-- RECORD INFORMATION -->
          <div class="border-t pt-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">Record Information</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Recorded By</label>
                <n-input v-model:value="formData.recorded_by" placeholder="Name of officer" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Contact No.</label>
                <n-input v-model:value="formData.contact_no" placeholder="09XXXXXXXXX" />
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 px-6 py-4 border-t">
          <NButton @click="handleModalClose" :disabled="saving">Cancel</NButton>
          <NButton type="primary" @click="handleSave" :loading="saving" :disabled="saving">Save</NButton>
        </div>
      </div>
    </NModal>

    <!-- CONFIRM MODALS -->
    <ConfirmModal
      :show="showDeleteModal"
      :title="`Delete ${selectedIds.length} record(s)?`"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmDelete"
      @cancel="showDeleteModal = false"
    />

    <ConfirmModal
      :show="showResolveModal"
      title="Mark as Resolved?"
      confirm-text="Resolve"
      cancel-text="Cancel"
      @confirm="confirmResolve"
      @cancel="showResolveModal = false"
    >
      <template #default>
        <p class="text-sm text-gray-600">
          Resolving this record will restore the respondent resident's
          <span class="font-semibold text-green-700">clean record</span> status,
          provided they have no other active blotter records as respondent.
        </p>
        <p class="text-sm text-gray-500 mt-2">You can re-open this record at any time if needed.</p>
      </template>
    </ConfirmModal>

    <ConfirmModal
      :show="showReopenModal"
      title="Re-open this record?"
      confirm-text="Re-open"
      cancel-text="Cancel"
      @confirm="confirmReopen"
      @cancel="showReopenModal = false"
    >
      <template #default>
        <p class="text-sm text-gray-600">
          Re-opening this record will flag the respondent as having an
          <span class="font-semibold text-amber-600">active blotter record</span>,
          which may affect their eligibility for clean-record documents.
        </p>
      </template>
    </ConfirmModal>

  </div>
</template>