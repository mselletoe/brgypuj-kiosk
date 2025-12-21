<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NTabs, NTabPane } from 'naive-ui';
import PageTitle from '@/components/shared/PageTitle.vue';

// Sub-tab Imports
import AllTab from '@/views/feedback-and-reports/subtabs/AllTab.vue';
import FeedbackTab from '@/views/feedback-and-reports/subtabs/FeedbackTab.vue';
import ReportsTab from '@/views/feedback-and-reports/subtabs/ReportsTab.vue';

const route = useRoute();
const router = useRouter();
const searchQuery = ref('');

// 1. Map route params to Components
const tabMap = {
  all: AllTab,
  feedbacks: FeedbackTab,
  reports: ReportsTab
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
  <div class="p-6 bg-white rounded-md w-full h-full space-y-5 overflow-hidden">
    <div class="flex justify-between items-center">
      <PageTitle title="Feedback and Reports" />
      
      <div class="flex items-center gap-2">
        <div class="relative w-64">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search"
            class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <button class="p-2 text-gray-400 hover:text-red-500 border border-gray-200 rounded-md">
          <i class="pi pi-trash"></i> </button>
        <button class="p-2 text-gray-400 border border-gray-200 rounded-md">
          <i class="pi pi-stop"></i>
        </button>
      </div>
    </div>

    <div class="border-b border-gray-200">
      <n-tabs
        v-model:value="activeTab"
        type="line"
        animated
        class="flex-grow"
      >
        <n-tab-pane name="all" tab="All" />
        <n-tab-pane name="feedbacks" tab="Feedbacks" />
        <n-tab-pane name="reports" tab="Reports" />
      </n-tabs>
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