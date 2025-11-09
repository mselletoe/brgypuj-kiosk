<script setup>
import { ref } from 'vue';
import { NTabs, NTabPane } from 'naive-ui';
import PageTitle from '@/components/shared/PageTitle.vue';
import PendingTab from '@/views/requests/subtabs/PendingTab.vue';
import ProcessingTab from '@/views/requests/subtabs/ProcessingTab.vue';
import ReadyTab from '@/views/requests/subtabs/ReadyTab.vue';
import ReleasedTab from '@/views/requests/subtabs/ReleasedTab.vue';
import RejectedTab from '@/views/requests/subtabs/RejectedTab.vue';

const activeTab = ref('pending');
const searchQuery = ref(''); // Added for the search bar
</script>

<template>
  <div class="p-6 bg-white rounded-md w-full h-full space-y-5">
    <PageTitle title="Requests Management" />

    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs
        v-model:value="activeTab"
        type="line"
        animated
        class="flex-grow"
      >
        <n-tab-pane name="pending" tab="Pending"></n-tab-pane>
        <n-tab-pane name="processing" tab="Processing"></n-tab-pane>
        <n-tab-pane name="ready" tab="Ready"></n-tab-pane>
        <n-tab-pane name="released" tab="Released"></n-tab-pane>
        <n-tab-pane name="rejected" tab="Rejected"></n-tab-pane>
      </n-tabs>

      <div class="w-full max-w-xs ml-4 mb-2 mr-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          class="block w-full px-4 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
    </div>

    <div>
      <PendingTab v-if="activeTab === 'pending'" :search-query="searchQuery" />
      <ProcessingTab v-if="activeTab === 'processing'" :search-query="searchQuery" />
      <ReadyTab v-if="activeTab === 'ready'" :search-query="searchQuery" />
      <ReleasedTab v-if="activeTab === 'released'" :search-query="searchQuery" />
      <RejectedTab v-if="activeTab === 'rejected'" :search-query="searchQuery" />
    </div>
  </div>
</template>