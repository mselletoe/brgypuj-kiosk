<script setup>
/**
 * @file FAQsManagement.vue
 * @description Admin interface for managing Frequently Asked Questions (FAQs).
 * Includes inline editing, bulk deletion, and data table presentation modeled
 * after the system's standard CRUD interface.
 */
import { ref, computed, watch, h } from "vue";
import { NDataTable, NInput, NButton, NCheckbox, useMessage } from "naive-ui";
import {
  PencilSquareIcon,
  TrashIcon,
  XMarkIcon,
  CheckIcon,
} from "@heroicons/vue/24/outline";
import PageTitle from "@/components/shared/PageTitle.vue";
import ConfirmModal from "@/components/shared/ConfirmationModal.vue";

const message = useMessage();

// ======================================
// State Management
// ======================================
// Using a pseudo-id for frontend logic until a backend is connected
const faqs = ref([
  {
    id: 1,
    question: "How do I use the Barangay Kiosk?",
    answer:
      "Simply touch anywhere on the screen to begin, then authenticate using your RFID card and PIN. Navigate through the services using the touch interface.",
  },
  {
    id: 2,
    question: "What if I forgot my PIN?",
    answer:
      "Please visit the Barangay Office during office hours with your RFID card and ask for assistance from a staff in resetting your PIN.",
  },
  {
    id: 3,
    question: "How long does it take to process the documents?",
    answer:
      "Processing times vary depending on the document type. Most standard certificates can be processed within the same day, while others may take 1-3 business days. Please check the specific service details.",
  },
  {
    id: 4,
    question: "What equipment can I borrow from the barangay?",
    answer:
      "Available equipment includes event tents, monobloc chairs, folding tables, and sound systems. Availability may vary, please check the Equipment Borrowing section.",
  },
]);

const editingId = ref(null);
const showAddForm = ref(false);
const searchQuery = ref("");
const showDeleteModal = ref(false);
const deleteTargetId = ref(null);
const selectedIds = ref([]);
const isBulkDelete = ref(false);

const newFaq = ref({
  question: "",
  answer: "",
});

// ======================================
// CRUD Handlers
// ======================================
function addFaq() {
  if (!newFaq.value.question.trim() || !newFaq.value.answer.trim()) {
    return message.warning("Please enter both a question and an answer.");
  }

  const nextId =
    faqs.value.length > 0 ? Math.max(...faqs.value.map((f) => f.id)) + 1 : 1;

  faqs.value.push({
    id: nextId,
    question: newFaq.value.question,
    answer: newFaq.value.answer,
  });

  message.success("FAQ created successfully.");

  showAddForm.value = false;
  newFaq.value = { question: "", answer: "" };
}

function updateFaq(row) {
  if (!row.question.trim() || !row.answer.trim()) {
    return message.warning("Fields cannot be empty.");
  }
  editingId.value = null;
  message.success("FAQ updated successfully.");
}

// ======================================
// Delete Logic (Single & Bulk)
// ======================================
function requestDelete(id) {
  deleteTargetId.value = id;
  isBulkDelete.value = false;
  showDeleteModal.value = true;
}

function bulkDelete() {
  if (!selectedIds.value.length) return;
  isBulkDelete.value = true;
  showDeleteModal.value = true;
}

function confirmDelete() {
  if (isBulkDelete.value) {
    faqs.value = faqs.value.filter((f) => !selectedIds.value.includes(f.id));
    message.success(`${selectedIds.value.length} FAQ(s) deleted successfully.`);
    selectedIds.value = [];
  } else {
    faqs.value = faqs.value.filter((f) => f.id !== deleteTargetId.value);
    message.success("FAQ deleted successfully.");
  }

  deleteTargetId.value = null;
  showDeleteModal.value = false;
}

function cancelDelete() {
  showDeleteModal.value = false;
  deleteTargetId.value = null;
}

// ======================================
// Selection Logic
// ======================================
const filteredFaqs = computed(() => {
  const filtered = !searchQuery.value
    ? faqs.value
    : faqs.value.filter(
        (f) =>
          f.question.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          f.answer.toLowerCase().includes(searchQuery.value.toLowerCase()),
      );

  if (editingId.value && !filtered.find((f) => f.id === editingId.value)) {
    editingId.value = null;
  }

  return filtered;
});

const totalCount = computed(() => filteredFaqs.value.length);
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
    selectedIds.value = filteredFaqs.value.map((f) => f.id);
  }
}

watch(searchQuery, () => {
  selectedIds.value = [];
});

// ======================================
// Table Columns
// ======================================
const columns = computed(() => [
  {
    title: "",
    key: "select",
    width: 40,
    render(row) {
      return h(NCheckbox, {
        checked: selectedIds.value.includes(row.id),
        onUpdateChecked(checked) {
          if (checked) {
            if (!selectedIds.value.includes(row.id)) {
              selectedIds.value.push(row.id);
            }
          } else {
            selectedIds.value = selectedIds.value.filter((id) => id !== row.id);
          }
        },
      });
    },
  },
  {
    title: "Question",
    key: "question",
    width: 300,
    render(row) {
      if (editingId.value === row.id) {
        return h(NInput, {
          value: row.question,
          onUpdateValue(v) {
            row.question = v;
          },
        });
      }
      return h("span", { class: "font-semibold text-gray-800" }, row.question);
    },
  },
  {
    title: "Answer",
    key: "answer",
    render(row) {
      if (editingId.value === row.id) {
        return h(NInput, {
          value: row.answer,
          type: "textarea",
          autosize: { minRows: 2, maxRows: 5 },
          onUpdateValue(v) {
            row.answer = v;
          },
        });
      }
      return h("span", { class: "text-gray-600" }, row.answer);
    },
  },
  {
    title: "Actions",
    key: "actions",
    width: 150,
    render(row) {
      if (editingId.value === row.id) {
        return h("div", { class: "flex gap-2" }, [
          h(
            NButton,
            { type: "success", size: "small", onClick: () => updateFaq(row) },
            { default: () => "Save" },
          ),
          h(
            NButton,
            {
              type: "default",
              size: "small",
              onClick: () => (editingId.value = null),
            },
            { default: () => "Cancel" },
          ),
        ]);
      }

      return h("div", { class: "flex gap-2 items-center flex-wrap" }, [
        h(
          "button",
          {
            onClick: () => (editingId.value = row.id),
            class:
              "p-1.5 text-orange-500 hover:bg-orange-50 rounded transition",
          },
          [h(PencilSquareIcon, { class: "w-5 h-5" })],
        ),
        h(
          "button",
          {
            onClick: () => requestDelete(row.id),
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
        <PageTitle title="FAQs Management" />
        <p class="text-sm text-gray-500 mt-1">
          Create, edit, and manage frequently asked questions displayed on the
          Kiosk.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search FAQs"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />

        <button
          @click="bulkDelete"
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

        <button
          @click="showAddForm = true"
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          Add FAQ
        </button>
      </div>
    </div>

    <div
      v-if="showAddForm"
      class="bg-[#F0F5FF] p-6 mb-3 rounded-lg border border-[#0957FF] relative shrink-0"
    >
      <button
        @click="showAddForm = false"
        class="absolute top-4 right-4 p-1 hover:bg-gray-200 rounded transition"
      >
        <XMarkIcon class="w-5 h-5 text-gray-600" />
      </button>

      <div class="flex flex-col gap-4 max-w-4xl">
        <div>
          <label class="block text-sm text-gray-600 mb-1">Question</label>
          <n-input
            v-model:value="newFaq.question"
            placeholder="e.g. What are the office hours?"
          />
        </div>

        <div>
          <label class="block text-sm text-gray-600 mb-1">Answer</label>
          <n-input
            v-model:value="newFaq.answer"
            type="textarea"
            placeholder="Provide a detailed answer here..."
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </div>
      </div>

      <div class="flex justify-end gap-3 mt-4">
        <n-button @click="showAddForm = false">Cancel</n-button>
        <n-button type="primary" @click="addFaq"> Save FAQ </n-button>
      </div>
    </div>

    <div
      class="overflow-y-auto bg-white rounded-lg border border-gray-200 flex-1"
    >
      <n-data-table :columns="columns" :data="filteredFaqs" :bordered="false" />
    </div>

    <ConfirmModal
      :show="showDeleteModal"
      :title="
        isBulkDelete
          ? `Delete ${selectedIds.length} FAQ(s)?`
          : 'Delete this FAQ?'
      "
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>
