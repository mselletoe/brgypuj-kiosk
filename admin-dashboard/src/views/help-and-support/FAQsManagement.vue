<script setup>
/**
 * @file FAQsManagement.vue
 * @description Admin interface for managing Frequently Asked Questions (FAQs).
 * Allows administrators to add, edit, and remove FAQs displayed on the Kiosk.
 */
import { ref } from "vue";
import {
  useMessage,
  NButton,
  NInput,
  NModal,
  NCard,
  NPopconfirm,
  NForm,
  NFormItem,
} from "naive-ui";
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  QuestionMarkCircleIcon,
} from "@heroicons/vue/24/outline";

const message = useMessage();

// Initial state matching the hardcoded Kiosk FAQs
const faqs = ref([
  {
    question: "How do I use the Barangay Kiosk?",
    answer:
      "Simply touch anywhere on the screen to begin, then authenticate using your RFID card and PIN. Navigate through the services using the touch interface.",
  },
  {
    question: "What if I forgot my PIN?",
    answer:
      "Please visit the Barangay Office during office hours with your RFID card and ask for assistance from a staff in resetting your PIN.",
  },
  {
    question: "How long does it take to process the documents?",
    answer:
      "Processing times vary depending on the document type. Most standard certificates can be processed within the same day, while others may take 1-3 business days. Please check the specific service details.",
  },
  {
    question: "What equipment can I borrow from the barangay?",
    answer:
      "Available equipment includes event tents, monobloc chairs, folding tables, and sound systems. Availability may vary, please check the Equipment Borrowing section.",
  },
]);

// Modal & Form State
const showModal = ref(false);
const isEditing = ref(false);
const editingIndex = ref(-1);
const faqForm = ref({ question: "", answer: "" });

/**
 * Opens the modal to add a completely new FAQ.
 */
const openAddModal = () => {
  isEditing.value = false;
  faqForm.value = { question: "", answer: "" };
  showModal.value = true;
};

/**
 * Opens the modal to edit an existing FAQ.
 * @param {number} index - The array index of the FAQ being edited.
 */
const openEditModal = (index) => {
  isEditing.value = true;
  editingIndex.value = index;
  // Clone object to avoid reactive mutations before save
  faqForm.value = { ...faqs.value[index] };
  showModal.value = true;
};

/**
 * Handles saving the FAQ (either creating or updating).
 */
const saveFaq = () => {
  if (!faqForm.value.question.trim() || !faqForm.value.answer.trim()) {
    message.warning("Please fill in both the question and answer.");
    return;
  }

  if (isEditing.value) {
    faqs.value[editingIndex.value] = { ...faqForm.value };
    message.success("FAQ updated successfully.");
  } else {
    faqs.value.push({ ...faqForm.value });
    message.success("New FAQ added successfully.");
  }

  showModal.value = false;
};

/**
 * Removes an FAQ from the list.
 * @param {number} index - The array index of the FAQ to delete.
 */
const deleteFaq = (index) => {
  faqs.value.splice(index, 1);
  message.success("FAQ deleted successfully.");
};
</script>

<template>
  <div class="flex flex-col gap-6 p-6 h-full w-full">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">FAQs Management</h1>
        <p class="text-gray-500 text-sm mt-1">
          Manage the frequently asked questions displayed on the Kiosk.
        </p>
      </div>
      <n-button type="primary" size="large" @click="openAddModal">
        <template #icon>
          <PlusIcon class="w-5 h-5" />
        </template>
        Add New FAQ
      </n-button>
    </div>

    <div class="flex flex-col gap-4 mt-2">
      <div
        v-if="faqs.length === 0"
        class="flex flex-col items-center justify-center p-12 text-gray-400 bg-gray-50 rounded-xl border border-dashed border-gray-300"
      >
        <QuestionMarkCircleIcon class="w-12 h-12 mb-2 text-gray-300" />
        <p>No FAQs available. Click "Add New FAQ" to create one.</p>
      </div>

      <n-card
        v-for="(faq, index) in faqs"
        :key="index"
        class="shadow-sm rounded-xl border border-gray-200"
      >
        <div
          class="flex flex-col sm:flex-row justify-between items-start gap-4"
        >
          <div class="flex-1">
            <h3 class="text-lg font-bold text-[#013C6D] mb-2">
              {{ faq.question }}
            </h3>
            <p class="text-gray-600 leading-relaxed">{{ faq.answer }}</p>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <n-button tertiary circle type="info" @click="openEditModal(index)">
              <template #icon>
                <PencilSquareIcon class="w-5 h-5" />
              </template>
            </n-button>

            <n-popconfirm
              @positive-click="deleteFaq(index)"
              positive-text="Delete"
              negative-text="Cancel"
            >
              <template #trigger>
                <n-button tertiary circle type="error">
                  <template #icon>
                    <TrashIcon class="w-5 h-5" />
                  </template>
                </n-button>
              </template>
              Are you sure you want to delete this FAQ?
            </n-popconfirm>
          </div>
        </div>
      </n-card>
    </div>

    <n-modal
      v-model:show="showModal"
      preset="card"
      class="max-w-xl"
      :title="isEditing ? 'Edit FAQ' : 'Add New FAQ'"
    >
      <n-form :model="faqForm" class="flex flex-col gap-4 mt-4">
        <n-form-item label="Question" required>
          <n-input
            v-model:value="faqForm.question"
            placeholder="e.g. What are the office hours?"
          />
        </n-form-item>

        <n-form-item label="Answer" required>
          <n-input
            v-model:value="faqForm.answer"
            type="textarea"
            placeholder="Type the answer here..."
            :autosize="{ minRows: 4 }"
          />
        </n-form-item>

        <div class="flex justify-end gap-3 mt-4">
          <n-button @click="showModal = false">Cancel</n-button>
          <n-button type="primary" @click="saveFaq">
            {{ isEditing ? "Save Changes" : "Add FAQ" }}
          </n-button>
        </div>
      </n-form>
    </n-modal>
  </div>
</template>
