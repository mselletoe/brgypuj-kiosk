<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NTabs, NTabPane } from 'naive-ui';
import PageTitle from '@/components/shared/PageTitle.vue';
import PendingTab from '@/views/requests/document-requests/subtabs/PendingTab.vue';
import ProcessingTab from '@/views/requests/document-requests/subtabs/ProcessingTab.vue';
import ReadyTab from '@/views/requests/document-requests/subtabs/ReadyTab.vue';
import ReleasedTab from '@/views/requests/document-requests/subtabs/ReleasedTab.vue';
import RejectedTab from '@/views/requests/document-requests/subtabs/RejectedTab.vue';
const route = useRoute();
const router = useRouter();
const searchQuery = ref('');

const tabMap = {
  pending: PendingTab,
  processing: ProcessingTab,
  ready: ReadyTab,
  released: ReleasedTab,
  rejected: RejectedTab
};

const activeTab = computed({
  get: () => route.params.status || 'pending',
  set: (newStatus) => {
    router.push({ name: 'DocumentRequests', params: { status: newStatus } });
  }
});

const currentTabComponent = computed(() => {
  return tabMap[activeTab.value] || PendingTab;
});
</script>

<template>
  <div class="p-6 bg-white rounded-md w-full h-full space-y-5 overflow-hidden">
    <PageTitle title="Document Requests" />

    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs
        v-model:value="activeTab"
        type="line"
        animated
        class="flex-grow"
      >
        <n-tab-pane name="pending" tab="Pending" />
        <n-tab-pane name="processing" tab="Processing" />
        <n-tab-pane name="ready" tab="Ready" />
        <n-tab-pane name="released" tab="Released" />
        <n-tab-pane name="rejected" tab="Rejected" />
      </n-tabs>

      <div class="w-full max-w-xs ml-4 mb-2 mr-4">
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