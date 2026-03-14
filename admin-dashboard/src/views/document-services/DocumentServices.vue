<script setup>
import { ref, onMounted, h, computed, watch } from "vue";
import {
  NDataTable,
  NInput,
  NButton,
  NCheckbox,
  useMessage,
  NEmpty,
  NSpin,
  NUpload,
  NUploadDragger,
  NModal,
} from "naive-ui";
import {
  PencilSquareIcon,
  TrashIcon,
  XMarkIcon,
  CheckIcon,
  ListBulletIcon,
  ClipboardDocumentListIcon,
  ArrowUpTrayIcon,
  ArrowDownTrayIcon,
  IdentificationIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  ChevronDownIcon,
  ArrowPathIcon,
  EyeIcon,
} from "@heroicons/vue/24/outline";
import PageTitle from "@/components/shared/PageTitle.vue";
import FieldEditor from "./FieldEditor.vue";
import RequirementsEditor from "./RequirementsEditor.vue";
import ConfirmModal from "@/components/shared/ConfirmationModal.vue";
import {
  getDocumentTypes,
  createDocumentType,
  updateDocumentType,
  deleteDocumentType,
  uploadDocumentTemplate,
  downloadDocumentTemplate,
  updateDocumentRequirements,
} from "@/api/documentService";
import { getIDTemplatePreviewUrl, } from "@/api/idService";
import { useSearchSync } from "@/composables/useSearchSync";

const message = useMessage();

const services = ref([]);
const isLoading = ref(true);
const editingId = ref(null);
const showAddForm = ref(false);
const searchQuery = ref("");
useSearchSync(searchQuery);
const showDeleteModal = ref(false);
const deleteTargetId = ref(null);
const selectedIds = ref([]);
const isBulkDelete = ref(false);

const newService = ref({
  request_type_name: "",
  description: "",
  price: 0,
  available: true,
  fields: [],
});

const idPanelOpen = ref(false);
const idDocType = ref(null);
const idLocalPrice = ref(0);
const idSaving = ref(false);
const idUploading = ref(false);
const idHasTemplate = computed(() => !!idDocType.value?.has_template);

const showIdFieldModal = ref(false);
const showIdReqModal = ref(false);

const showIdPreviewModal = ref(false);
const idPreviewUrl = computed(() =>
  idDocType.value?.id ? getIDTemplatePreviewUrl() : null
);

async function fetchServices() {
  isLoading.value = true;
  try {
    const { data } = await getDocumentTypes();
    const idType = data.find((d) => !!d.is_id_application);
    if (idType) {
      idDocType.value = {
        id: idType.id,
        request_type_name: idType.doctype_name,
        description: idType.description,
        price: Number(idType.price),
        available: idType.is_available,
        is_id_application: true,
        fields: idType.fields || [],
        requirements: idType.requirements || [],
        has_template: !!idType.has_template,
      };
      idLocalPrice.value = Number(idType.price) ?? 0;
    }
    services.value = data
      .filter((d) => !d.is_id_application)
      .map((d) => ({
        id: d.id,
        request_type_name: d.doctype_name,
        description: d.description,
        price: Number(d.price),
        available: d.is_available,
        is_id_application: false,
        fields: d.fields || [],
        requirements: d.requirements || [],
        has_template: d.has_template || false,
      }));
  } catch (error) {
    console.error(error);
    message.error("Failed to fetch document types.");
  } finally {
    isLoading.value = false;
  }
}

async function ensureIDDocType() {
  if (idDocType.value) return idDocType.value;
  const { data } = await createDocumentType({
    doctype_name: "ID Application",
    description: "Barangay Identification Card application template.",
    price: idLocalPrice.value,
    fields: [],
    is_available: true,
    is_id_application: true,
  });
  idDocType.value = {
    id: data.id,
    request_type_name: data.doctype_name,
    price: Number(data.price),
    available: data.is_available,
    is_id_application: true,
    fields: data.fields || [],
    requirements: data.requirements || [],
    has_template: false,
  };
  return idDocType.value;
}

async function handleIDFileUpload({ file }) {
  if (!file?.file) return;
  const raw = file.file;
  if (!raw.name.endsWith(".docx")) { message.warning("Only .docx files are accepted."); return false; }
  idUploading.value = true;
  try {
    const docType = await ensureIDDocType();
    await uploadDocumentTemplate(docType.id, raw);
    // Update idDocType directly — GET /admin/documents/types may exclude
    // is_id_application types so fetchServices() cannot be relied upon here.
    idDocType.value = { ...idDocType.value, has_template: true };
    message.success("Template uploaded successfully.");
  } catch (err) {
    console.error(err);
    message.error("Upload failed. Please try again.");
  } finally {
    idUploading.value = false;
  }
  return false;
}

function handleIDReplaceTemplate() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".docx";
  input.onchange = async (e) => {
    const raw = e.target.files[0];
    if (!raw) return;
    if (!raw.name.endsWith(".docx")) { message.warning("Only .docx files are accepted."); return; }
    idUploading.value = true;
    try {
      await uploadDocumentTemplate(idDocType.value.id, raw);
      idDocType.value = { ...idDocType.value, has_template: true };
      message.success("Template replaced successfully.");
    } catch (err) {
      console.error(err);
      message.error("Replace failed.");
    } finally {
      idUploading.value = false;
    }
  };
  input.click();
}

async function handleIDDownloadTemplate() {
  if (!idDocType.value?.id) return;
  try {
    await downloadDocumentTemplate(idDocType.value.id, "id-application-template");
    message.success("Download started.");
  } catch { message.error("Download failed."); }
}

async function idSavePrice() {
  idSaving.value = true;
  try {
    const docType = await ensureIDDocType();
    await updateDocumentType(docType.id, { price: idLocalPrice.value });
    message.success("Price saved.");
    await fetchServices();
  } catch (err) {
    console.error(err);
    message.error("Failed to save price.");
  } finally {
    idSaving.value = false;
  }
}

async function saveIdFields(updatedFields, serviceId) {
  try {
    await updateDocumentType(serviceId, { fields: updatedFields });
    if (idDocType.value) idDocType.value.fields = updatedFields;
    message.success("ID fields updated.");
  } catch (err) {
    console.error(err);
    message.error("Failed to update ID fields.");
  } finally {
    showIdFieldModal.value = false;
  }
}

async function saveIdRequirements(updatedRequirements, serviceId) {
  if (updatedRequirements === null) { message.warning("Please fill in all requirement fields before saving."); return; }
  try {
    await updateDocumentRequirements(serviceId, updatedRequirements);
    if (idDocType.value) idDocType.value.requirements = updatedRequirements;
    message.success("ID requirements updated.");
    showIdReqModal.value = false;
  } catch (err) {
    console.error(err);
    message.error("Failed to update ID requirements.");
  }
}

async function addService() {
  if (!newService.value.request_type_name.trim()) return message.warning("Please enter a service name.");
  try {
    const { data } = await createDocumentType({
      doctype_name: newService.value.request_type_name,
      description: newService.value.description,
      price: newService.value.price,
      fields: [],
      is_available: newService.value.available,
      is_id_application: false,
    });
    services.value.push({
      id: data.id,
      request_type_name: data.doctype_name,
      description: data.description,
      price: Number(data.price),
      available: data.is_available,
      is_id_application: false,
      fields: data.fields || [],
      requirements: data.requirements || [],
      has_template: false,
    });
    message.success("Document type created. You can now upload a template.");
    showAddForm.value = false;
    newService.value = { request_type_name: "", description: "", price: 0, available: true, fields: [] };
  } catch (error) {
    message.error(error.response?.data?.detail || "Failed to add document type.");
  }
}

async function updateService(service) {
  try {
    const { data } = await updateDocumentType(service.id, {
      doctype_name: service.request_type_name,
      description: service.description,
      price: service.price,
      is_available: service.available,
      is_id_application: false,
      fields: service.fields,
    });
    const idx = services.value.findIndex((s) => s.id === service.id);
    if (idx !== -1) {
      services.value[idx] = {
        ...services.value[idx],
        id: data.id,
        request_type_name: data.doctype_name,
        description: data.description,
        price: Number(data.price),
        available: data.is_available,
        fields: data.fields || [],
      };
    }
    editingId.value = null;
    message.success("Service updated successfully.");
  } catch (err) {
    console.error(err);
    message.error("Update failed.");
  }
}

async function toggleAvailability(service) {
  try {
    const { data } = await updateDocumentType(service.id, { is_available: !service.available });
    service.available = data.is_available;
    message.success(`Service ${data.is_available ? "enabled" : "disabled"}.`);
  } catch (err) {
    console.error(err);
    message.error("Failed to update availability.");
  }
}

function requestDelete(id) { deleteTargetId.value = id; isBulkDelete.value = false; showDeleteModal.value = true; }
function bulkDelete() { if (!selectedIds.value.length) return; isBulkDelete.value = true; showDeleteModal.value = true; }

async function confirmDelete() {
  try {
    if (isBulkDelete.value) {
      await Promise.all(selectedIds.value.map((id) => deleteDocumentType(id)));
      services.value = services.value.filter((s) => !selectedIds.value.includes(s.id));
      message.success(`${selectedIds.value.length} service(s) deleted.`);
      selectedIds.value = [];
    } else {
      await deleteDocumentType(deleteTargetId.value);
      services.value = services.value.filter((s) => s.id !== deleteTargetId.value);
      message.success("Service deleted.");
    }
  } catch (err) {
    message.error(err.response?.data?.detail || "Delete failed.");
  } finally {
    deleteTargetId.value = null;
    showDeleteModal.value = false;
  }
}

function cancelDelete() { showDeleteModal.value = false; deleteTargetId.value = null; }

const totalCount = computed(() => filteredServices.value.length);
const selectedCount = computed(() => selectedIds.value.length);
const selectionState = computed(() => {
  if (totalCount.value === 0 || selectedCount.value === 0) return "none";
  if (selectedCount.value < totalCount.value) return "partial";
  return "all";
});

function handleMainSelectToggle() {
  if (selectionState.value === "all" || selectionState.value === "partial") selectedIds.value = [];
  else selectedIds.value = filteredServices.value.map((s) => s.id);
}

async function handleUploadTemplate(service) {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".pdf,.docx";
  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const allowed = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
    if (!allowed.includes(file.type)) { message.error("Only PDF or DOCX files are allowed."); return; }
    if (file.size > 10 * 1024 * 1024) { message.error("File size must not exceed 10MB."); return; }
    try {
      await uploadDocumentTemplate(service.id, file);
      service.has_template = true;
      message.success("Template uploaded successfully.");
    } catch { message.error("Failed to upload template."); }
  };
  input.click();
}

async function handleDownload(service) {
  try {
    await downloadDocumentTemplate(service.id, service.request_type_name);
    message.success("Download started.");
  } catch { message.error("Failed to download template."); }
}

const editingFields = ref(null);
const showFieldModal = ref(false);

function editFields(service) {
  editingFields.value = { fields: JSON.parse(JSON.stringify(service.fields || [])), serviceId: service.id };
  showFieldModal.value = true;
}

async function saveFields(updatedFields, serviceId) {
  const service = services.value.find((s) => s.id === serviceId);
  if (!service) return;
  try {
    await updateDocumentType(serviceId, {
      doctype_name: service.request_type_name,
      description: service.description,
      price: service.price,
      is_available: service.available,
      fields: updatedFields,
    });
    service.fields = updatedFields;
    message.success("Fields updated.");
  } catch { message.error("Failed to update fields."); }
  finally { showFieldModal.value = false; }
}

const showReqModal = ref(false);
const editingReqService = ref(null);

function editRequirements(service) { editingReqService.value = service; showReqModal.value = true; }

async function saveRequirements(updatedRequirements, serviceId) {
  if (updatedRequirements === null) { message.warning("Please fill in all requirement fields before saving."); return; }
  const service = services.value.find((s) => s.id === serviceId);
  if (!service) return;
  try {
    await updateDocumentRequirements(service.id, updatedRequirements);
    service.requirements = updatedRequirements;
    message.success("Requirements updated.");
    showReqModal.value = false;
  } catch { message.error("Failed to update requirements."); }
}

const filteredServices = computed(() => {
  const filtered = services.value.filter((s) =>
    !searchQuery.value || s.request_type_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
  if (editingId.value && !filtered.find((s) => s.id === editingId.value)) editingId.value = null;
  return filtered;
});

watch(searchQuery, () => { selectedIds.value = []; });

function iconBtn({ onClick, icon, colorClass, tooltip }) {
  return h("div", { class: "relative group/tip inline-flex" }, [
    h("button", { onClick, class: `p-1.5 ${colorClass} rounded transition` }, [h(icon, { class: "w-5 h-5" })]),
    h("div", {
      class: "pointer-events-none absolute -top-7 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover/tip:opacity-100 group-hover/tip:visible transition-all duration-200 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50",
    }, tooltip),
  ]);
}

const columns = computed(() => [
  {
    title: "", key: "select", width: 40,
    render(row) {
      return h(NCheckbox, {
        checked: selectedIds.value.includes(row.id),
        onUpdateChecked(checked) {
          if (checked) { if (!selectedIds.value.includes(row.id)) selectedIds.value.push(row.id); }
          else { selectedIds.value = selectedIds.value.filter((id) => id !== row.id); }
        },
      });
    },
  },
  {
    title: "Name", key: "request_type_name",
    render(row) {
      if (editingId.value === row.id) return h(NInput, { value: row.request_type_name, onUpdateValue(v) { row.request_type_name = v; } });
      return row.request_type_name;
    },
  },
  {
    title: "Price", key: "price", width: 120,
    render(row) {
      if (editingId.value === row.id) return h(NInput, { value: row.price, type: "number", onUpdateValue(v) { row.price = Number(v); } });
      return `₱${parseFloat(row.price).toFixed(2)}`;
    },
  },
  {
    title: "Status", key: "status", width: 140,
    render(row) {
      return h("button", {
        onClick: () => toggleAvailability(row),
        class: `px-3 py-1 rounded-full text-xs font-medium cursor-pointer transition ${row.available ? "bg-green-100 text-green-800 hover:bg-green-200" : "bg-gray-100 text-gray-800 hover:bg-gray-200"}`,
      }, row.available ? "Available" : "Not Available");
    },
  },
  {
    title: "Actions", key: "actions", width: 280,
    render(row) {
      if (editingId.value === row.id) {
        return h("div", { class: "flex gap-2" }, [
          h(NButton, { type: "success", size: "small", onClick: () => updateService(row) }, { default: () => "Save" }),
          h(NButton, { type: "default", size: "small", onClick: () => (editingId.value = null) }, { default: () => "Cancel" }),
        ]);
      }
      return h("div", { class: "flex gap-1 items-center" }, [
        iconBtn({ onClick: () => (editingId.value = row.id), icon: PencilSquareIcon, colorClass: "text-orange-500 hover:bg-orange-50", tooltip: "Edit" }),
        iconBtn({ onClick: () => requestDelete(row.id), icon: TrashIcon, colorClass: "text-red-500 hover:bg-red-50", tooltip: "Delete" }),
        iconBtn({ onClick: () => editFields(row), icon: ListBulletIcon, colorClass: "text-blue-500 hover:bg-blue-50", tooltip: "Fields" }),
        iconBtn({ onClick: () => editRequirements(row), icon: ClipboardDocumentListIcon, colorClass: "text-purple-500 hover:bg-purple-50", tooltip: "Requirements" }),
        iconBtn({
          onClick: () => handleUploadTemplate(row),
          icon: ArrowUpTrayIcon,
          colorClass: row.has_template ? "text-yellow-500 hover:bg-yellow-50" : "text-blue-600 hover:bg-blue-100",
          tooltip: row.has_template ? "Replace Template" : "Upload Template",
        }),
        row.has_template ? iconBtn({ onClick: () => handleDownload(row), icon: ArrowDownTrayIcon, colorClass: "text-green-500 hover:bg-green-50", tooltip: "Download Template" }) : null,
      ].filter(Boolean));
    },
  },
]);

onMounted(fetchServices);
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden animate-fade-in">

    <div class="flex mb-6 items-center justify-between">
      <div>
        <PageTitle title="Document Services Management" />
        <p class="text-sm text-gray-500 mt-1">
          Create, edit, and configure official barangay document templates and pricing.
        </p>
      </div>
      <div class="flex items-center gap-3">
        <input v-model="searchQuery" type="text" placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400" />
        <div class="relative group inline-block">
          <button @click="bulkDelete" :disabled="selectionState === 'none'"
            class="p-2 border border-red-400 rounded-lg transition-colors"
            :class="selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-50'">
            <TrashIcon class="w-5 h-5 text-red-500" />
          </button>
          <div class="absolute -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">Delete</div>
        </div>
        <div class="relative group inline-block">
          <div class="flex items-center border rounded-lg overflow-hidden transition-colors"
            :class="selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'">
            <button @click="handleMainSelectToggle" class="p-2 hover:bg-gray-50 flex items-center">
              <div class="w-5 h-5 border rounded flex items-center justify-center transition-colors"
                :class="selectionState !== 'none' ? 'bg-blue-600 border-blue-600' : 'border-gray-400'">
                <div v-if="selectionState === 'partial'" class="w-2 h-0.5 bg-white"></div>
                <CheckIcon v-if="selectionState === 'all'" class="w-3 h-3 text-white" />
              </div>
            </button>
          </div>
          <div class="absolute -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">Select All</div>
        </div>
        <button @click="showAddForm = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center gap-4">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      <p class="text-gray-500 font-medium">Loading document services...</p>
    </div>

    <template v-else>

      <!-- ID APPLICATION -->
      <div class="mb-4 rounded-xl border border-indigo-200 bg-indigo-50/60 overflow-hidden">
        <button @click="idPanelOpen = !idPanelOpen"
          class="w-full flex items-center justify-between px-5 py-4 hover:bg-indigo-50 transition">
          <div class="flex items-center gap-3">
            <div class="flex items-center justify-center w-9 h-9 rounded-lg bg-indigo-600 text-white flex-shrink-0">
              <IdentificationIcon class="w-5 h-5" />
            </div>
            <div class="text-left">
              <div class="flex items-center gap-2">
                <span class="text-sm font-semibold text-indigo-900">Barangay I.D</span>
              </div>
              <p class="text-xs text-indigo-500 mt-0.5">Manage your Barangay I.D fields, price and requirements.</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs px-2.5 py-1 rounded-full font-medium"
              :class="idHasTemplate ? 'bg-green-100 text-green-700 border border-green-300' : 'bg-amber-100 text-amber-700 border border-amber-300'">
              {{ idHasTemplate ? '✓ Template Uploaded' : '⚠ No Template' }}
            </span>
            <span class="text-xs text-green-700 font-bold">Fee: ₱{{ parseFloat(idLocalPrice).toFixed(2) }}</span>
            <ChevronDownIcon class="w-4 h-4 text-indigo-400 transition-transform duration-200" :class="idPanelOpen ? 'rotate-180' : ''" />
          </div>
        </button>

        <div v-if="idPanelOpen" class="border-t border-indigo-200 bg-white">
          <div class="p-5 flex gap-6 items-stretch">

            <!-- Col 1: Template -->
            <div class="flex-1 min-w-0 flex flex-col">
              <template v-if="!idHasTemplate">
                <NUpload :custom-request="handleIDFileUpload" :show-file-list="false" accept=".docx" :disabled="idUploading" class="flex-1">
                  <NUploadDragger class="h-full">
                    <div class="flex flex-col items-center justify-center h-full py-8 gap-2">
                      <NSpin v-if="idUploading" />
                      <template v-else>
                        <CloudArrowUpIcon class="w-8 h-8 text-gray-400" />
                        <p class="text-sm font-medium text-gray-600">Click or drag a <span class="text-indigo-600">.docx</span> here</p>
                        <p class="text-xs text-gray-400">No template uploaded yet</p>
                      </template>
                    </div>
                  </NUploadDragger>
                </NUpload>
              </template>
              <template v-else>
                <div class="flex items-center gap-4 p-4 bg-gray-50 border border-gray-200 rounded-lg h-full">
                  <div class="flex items-center justify-center w-14 h-16 bg-white border border-blue-200 rounded-md shadow-sm flex-shrink-0 relative">
                    <DocumentTextIcon class="w-7 h-7 text-blue-400" />
                    <span class="absolute bottom-1 text-[9px] font-bold text-blue-500 tracking-wide uppercase">docx</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-gray-800 truncate">brgy_id_template.docx</p>
                    <div class="flex items-center gap-2 mt-3">
                      <button @click="showIdPreviewModal = true"
                        class="flex items-center gap-1.5 text-xs font-medium text-indigo-600 border border-indigo-300 hover:bg-indigo-50 px-3 py-1.5 rounded-md transition">
                        <EyeIcon class="w-3.5 h-3.5" />Preview
                      </button>
                      <button @click="handleIDReplaceTemplate" :disabled="idUploading"
                        class="flex items-center gap-1.5 text-xs font-medium text-gray-600 border border-gray-300 hover:bg-gray-50 px-3 py-1.5 rounded-md transition disabled:opacity-50">
                        <NSpin v-if="idUploading" :size="12" /><ArrowPathIcon v-else class="w-3.5 h-3.5" />Replace
                      </button>
                      <button @click="handleIDDownloadTemplate"
                        class="flex items-center gap-1.5 text-xs font-medium text-green-600 border border-green-300 hover:bg-green-50 px-3 py-1.5 rounded-md transition">
                        <ArrowDownTrayIcon class="w-3.5 h-3.5" />Download
                      </button>
                    </div>
                  </div>
                </div>
              </template>
            </div>

            <!-- Col 2: Modals -->
            <div class="flex flex-col gap-3 w-52 flex-shrink-0 justify-center">
              <button @click="showIdFieldModal = true"
                class="flex h-full items-center gap-2 text-sm text-blue-600 border border-blue-200 hover:bg-blue-50 px-3 py-2 rounded-lg transition w-full text-left">
                <ListBulletIcon class="w-4 h-4 flex-shrink-0" />
                <span class="flex-1">Form Fields</span>
                <span class="text-xs bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded-full font-medium">{{ idDocType?.fields?.length ?? 0 }}</span>
              </button>
              <button @click="showIdReqModal = true"
                class="flex h-full items-center gap-2 text-sm text-purple-600 border border-purple-200 hover:bg-purple-50 px-3 py-2 rounded-lg transition w-full text-left">
                <ClipboardDocumentListIcon class="w-4 h-4 flex-shrink-0" />
                <span class="flex-1">Requirements</span>
                <span class="text-xs bg-purple-100 text-purple-600 px-1.5 py-0.5 rounded-full font-medium">{{ idDocType?.requirements?.length ?? 0 }}</span>
              </button>
            </div>

            <!-- Col 3: Price -->
            <div class="flex flex-col w-36 flex-shrink-0 justify-center gap-2">
              <label class="text-xs font-medium text-gray-500 block">Application Fee (₱)</label>
              <NInput v-model:value="idLocalPrice" type="number" size="small" :min="0" :step="0.01" placeholder="0.00" />
              <button class="px-3 py-1 border border-blue-600 text-blue-600 rounded-md font-medium text-xs hover:bg-blue-50 transition text-center" @click="idSavePrice">
                Save
              </button>
            </div>

          </div>
        </div>
      </div>

      <!-- REGULAR DOCUMENT TYPES -->
      <div v-if="showAddForm" class="bg-[#F0F5FF] p-6 mb-3 rounded-lg border border-[#0957FF] relative">
        <button @click="showAddForm = false" class="absolute top-4 right-4 p-1 hover:bg-gray-200 rounded">
          <XMarkIcon class="w-5 h-5 text-gray-600" />
        </button>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">Document Name</label>
            <n-input v-model:value="newService.request_type_name" placeholder="Enter name" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Description</label>
            <n-input v-model:value="newService.description" placeholder="Enter description" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">Price (₱)</label>
            <n-input v-model:value="newService.price" type="number" placeholder="0.00" min="0" step="0.01" />
          </div>
          <div class="flex items-end">
            <NCheckbox v-model:checked="newService.available">Available for Residents</NCheckbox>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <n-button @click="showAddForm = false">Cancel</n-button>
          <n-button type="primary" @click="addService">Add Document Type</n-button>
        </div>
      </div>

      <div v-if="services.length > 0 || showAddForm" class="overflow-y-auto bg-white rounded-lg border border-gray-200 flex-1">
        <n-data-table :columns="columns" :data="filteredServices" :bordered="false" />
      </div>

      <div v-else class="h-full flex flex-col items-center justify-center flex-1">
        <NEmpty description="No document services yet">
          <template #extra>
            <NButton type="primary" @click="showAddForm = true">Add Document Type</NButton>
          </template>
        </NEmpty>
      </div>

      <!-- ============================== -->
      <!-- Regular doc type modals        -->
      <!-- ============================== -->
      <FieldEditor
        :show="showFieldModal"
        :fields-data="editingFields?.fields"
        @close="showFieldModal = false"
        @saved="saveFields"
        :service-id="editingFields?.serviceId"
      />
      <RequirementsEditor
        :show="showReqModal"
        :requirements-data="editingReqService?.requirements"
        :service-id="editingReqService?.id"
        @close="showReqModal = false"
        @saved="saveRequirements"
      />

      <!-- ============================== -->
      <!-- ID Application modals          -->
      <!-- ============================== -->
      <FieldEditor
        :show="showIdFieldModal"
        :fields-data="idDocType?.fields"
        @close="showIdFieldModal = false"
        @saved="saveIdFields"
        :service-id="idDocType?.id"
      />
      <RequirementsEditor
        :show="showIdReqModal"
        :requirements-data="idDocType?.requirements"
        :service-id="idDocType?.id"
        :is-id-application="true"
        @close="showIdReqModal = false"
        @saved="saveIdRequirements"
      />

    </template>
  </div>

  <ConfirmModal :show="showDeleteModal" :title="isBulkDelete ? `Delete ${selectedIds.length} service(s)?` : 'Delete this service?'" confirm-text="Delete" cancel-text="Cancel" @confirm="confirmDelete" @cancel="cancelDelete" />

  <NModal :show="showIdPreviewModal" @update:show="showIdPreviewModal = false" :mask-closable="true">
    <div class="bg-white rounded-xl shadow-xl flex flex-col overflow-hidden" style="width: 860px; height: 90vh;">
      <div class="flex items-center justify-between px-5 py-3 border-b bg-gray-50 flex-shrink-0">
        <div class="flex items-center gap-2">
          <DocumentTextIcon class="w-4 h-4 text-indigo-500" />
          <span class="text-sm font-semibold text-gray-700">Template Preview</span>
          <span class="text-xs text-gray-400">· brgy_id_template.docx</span>
        </div>
        <div class="flex items-center gap-2">
          <button @click="handleIDDownloadTemplate"
            class="flex items-center gap-1.5 text-xs font-medium text-green-600 border border-green-300 hover:bg-green-50 px-2.5 py-1 rounded-md transition">
            <ArrowDownTrayIcon class="w-3.5 h-3.5" />Download
          </button>
          <button @click="showIdPreviewModal = false" class="p-1 rounded hover:bg-gray-200 transition">
            <XMarkIcon class="w-4 h-4 text-gray-500" />
          </button>
        </div>
      </div>
      <iframe v-if="idPreviewUrl" :src="idPreviewUrl" class="flex-1 w-full border-0" title="Template Preview" />
    </div>
  </NModal>
</template>