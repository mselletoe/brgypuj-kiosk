<script setup>
import { ref, onMounted } from 'vue'
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/vue/24/solid'
import faqService from '@/api/faqService'

const openIndex = ref(0);
const faqs = ref([]);

const loadFAQs = async () => {
  try {
    faqs.value = await faqService.getKioskFAQs()
  } catch (err) {
    console.error('Failed to fetch FAQs:', err)
  }
};

// Call on component mount
onMounted(() => {
  loadFAQs()
})

// Toggle FAQ expansion
const toggleFAQ = (index) => {
  openIndex.value = openIndex.value === index ? null : index
}
</script>

<template>
  <div class="space-y-[12px]">
    <div
      v-for="(faq, index) in faqs"
      :key="faq.id"
      class="bg-white rounded-2xl shadow-sm border border-gray-300 overflow-hidden"
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