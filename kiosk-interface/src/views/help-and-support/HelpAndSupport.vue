<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'; // Adjust path if needed
import FAQs from './FAQs.vue'; // Adjust path if needed
import Contact from './Contact.vue'; // Adjust path if needed

const router = useRouter();
const currentTab = ref('faqs'); // 'faqs' or 'contact'

const setActiveTab = (tabName) => {
  currentTab.value = tabName;
};

const goBackToHome = () => {
  router.push('/home'); // Assuming '/home' is your home route
};

// Button classes for active/inactive states
const activeTabClass = 'bg-[#013C6D] text-white';
const inactiveTabClass = 'bg-white text-gray-600 hover:bg-gray-300';
</script>

<template>
  <div class="px-8 pb-0 pt-4">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <ArrowBackButton @click="goBackToHome" />
        <h1 class="text-[40px] font-bold text-[#013C6D]">Help & Support</h1>
      </div>

      <div class="flex items-center gap-2 rounded-lg border-2 border-[#013C6D] p-1">
        <button
          @click="setActiveTab('faqs')"
          :class="[
            'px-6 py-2 rounded-md text-sm font-semibold transition-colors',
            currentTab === 'faqs' ? activeTabClass : inactiveTabClass,
          ]"
        >
          FAQs
        </button>
        <button
          @click="setActiveTab('contact')"
          :class="[
            'px-6 py-2 rounded-md text-sm font-semibold transition-colors',
            currentTab === 'contact' ? activeTabClass : inactiveTabClass,
          ]"
        >
          Contact
        </button>
      </div>
    </div>

    <div>
      <FAQs v-if="currentTab === 'faqs'" />
      <Contact v-if="currentTab === 'contact'" />
    </div>
  </div>
</template>