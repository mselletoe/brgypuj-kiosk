<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NTabs, NTabPane } from 'naive-ui';
import { TrashIcon } from '@heroicons/vue/24/outline';
import PageTitle from '@/components/shared/PageTitle.vue';
import AllTab from '@/views/feedback-and-reports/subtabs/AllTab.vue';
import FeedbackTab from '@/views/feedback-and-reports/subtabs/FeedbackTab.vue';
import ReportsTab from '@/views/feedback-and-reports/subtabs/ReportsTab.vue';
import LostReports from '@/views/feedback-and-reports/subtabs/LostReports.vue';

const route = useRoute();
const router = useRouter();
const searchQuery = ref('');

// 1. Map route params to Components
const tabMap = {
  all: AllTab,
  feedbacks: FeedbackTab,
  reports: ReportsTab,
  lostreports: LostReports
};

// 2. Sync activeTab with URL (Defaults to 'all')
const activeTab = computed({
  get: () => route.params.status || 'all',
  set: (newStatus) => {
    router.push({ name: 'FeedbackReports', params: { status: newStatus } });
  }
});

const currentTabComponent = computed(() => tabMap[activeTab.value] || AllTab);
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <div class="flex justify-between items-center mb-4">
      <PageTitle title="Feedback and Reports" />
      
      <div class="flex items-center space-x-2">
        <button 
          @click="triggerDelete"
          :disabled="selectionState === 'none'"
          :class="[selectionState === 'none' ? 'opacity-50 cursor-not-allowed' : 'hover:bg-red-50']"
          class="p-2 border border-red-700 rounded-lg transition-colors"
        >
          <TrashIcon class="w-5 h-5 text-red-700" />
        </button>

        <div class="flex items-center border rounded-lg overflow-hidden"
          :class="selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'"
        >
          <button 
            @click="handleMainSelectToggle"
            class="p-2 hover:bg-gray-50 flex items-center"
          >
            <div class="w-5 h-5 border rounded flex items-center justify-center" 
                 :class="selectionState !== 'none' ? 'bg-blue-600 border-blue-600' : 'border-gray-400'">
              <div v-if="selectionState === 'partial'" class="w-2 h-0.5 bg-white"></div>
              <svg v-if="selectionState === 'all'" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </button>
        </div>
      </div>
    </div>

    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs
        v-model:value="activeTab"
        type="line"
        animated
        class="flex-grow"
      >
        <n-tab-pane name="all" tab="All" />
        <n-tab-pane name="feedbacks" tab="Feedbacks" />
        <n-tab-pane name="reports" tab="Reports" />
        <n-tab-pane name="lostreports" tab="Lost Reports" />
      </n-tabs>

      <div class="w-full max-w-xs ml-4 mb-2">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search requests..."
          class="block w-full px-4 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 transition-all"
        />
      </div>
    </div>

    <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2">
      <keep-alive>
        <component 
          :is="currentTabComponent" 
          :search-query="searchQuery" 
          :key="activeTab"
        />
      </keep-alive>
    </div>
  </div>
</template>