<script setup>
import { ref } from 'vue';
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/vue/24/solid';

const openIndex = ref(0);

const faqs = ref([
  {
    question: 'How do I use the Barangay Kiosk?',
    answer: 'Simply touch anywhere on the screen to begin, then authenticate using your RFID card and PIN. Navigate through the services using the touch interface.',
  },
  {
    question: 'What if I forgot my PIN?',
    answer: 'Please visit the Barangay Office during office hours with your RFID card and ask for assistance from a staff in resetting your PIN.',
  },
  {
    question: 'How long does it take to process the documents?',
    answer: 'Processing times vary depending on the document type. Most standard certificates can be processed within the same day, while others may take 1-3 business days. Please check the specific service details.',
  },
  {
    question: 'What equipment can I borrow from the barangay?',
    answer: 'Available equipment includes event tents, monobloc chairs, folding tables, and sound systems. Availability may vary, please check the Equipment Borrowing section.',
  },
]);

const toggleFAQ = (index) => {
  openIndex.value = openIndex.value === index ? null : index; 
};
</script>

<template>
  <div class="space-y-[12px]">
    <div
      v-for="(faq, index) in faqs"
      :key="index"
      class="bg-white rounded-xl shadow border border-gray-200 overflow-hidden"
    >
      <button
        @click="toggleFAQ(index)"
        class="w-full flex justify-between items-center p-5 text-left text-lg font-semibold text-[#013C6D]"
      >
        <span>{{ faq.question }}</span>
        <ChevronUpIcon v-if="openIndex === index" class="w-5 h-5 transition-transform" />
        <ChevronDownIcon v-else class="w-5 h-5 transition-transform" />
      </button>
      <div
        v-if="openIndex === index"
        class="px-5 pb-5 text-gray-600"
      >
        <p>{{ faq.answer }}</p>
      </div>
    </div>
  </div>
</template>