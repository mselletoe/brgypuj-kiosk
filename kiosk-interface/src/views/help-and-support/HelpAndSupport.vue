<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import FAQs from './FAQs.vue'
import Contact from './Contact.vue'

const router = useRouter()
const currentTab = ref('faqs')

const setActiveTab = (tabName) => {
  currentTab.value = tabName;
};

const goBackToHome = () => {
  router.push('/home')
};

const activeTabClass = 'bg-[#013C6D] text-white'
const inactiveTabClass = 'bg-white text-gray-600 hover:bg-gray-300'
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <div class="flex items-center justify-between mb-6 flex-shrink-0">
      <div class="flex items-center gap-7">
        <ArrowBackButton @click="goBackToHome" />
        <div>
          <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">Help & Support</h1>
          <p class="text-[#03335C] -mt-2">Description</p>          
        </div>
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