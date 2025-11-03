<script setup>
import { ref } from 'vue';
import { NTabs, NTabPane } from 'naive-ui';
import { CloudArrowUpIcon } from '@heroicons/vue/24/outline';

// Make sure your paths are correct for these files
import UploadTemplateModal from '@/components/UploadTemplate.vue'; 
import AllDocumentsTab from './AllDocuments.vue';
import ArchivedTab from './Archived.vue';
import RecentlyDeletedTab from './RecentlyDeleted.vue';

const activeTab = ref('all');
const showUploadModal = ref(false);

const handleUploadComplete = () => {
  console.log('Template uploaded!');
  showUploadModal.value = false;
  // Here you would refresh your list of documents
};
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
      <h1 class="text-3xl font-bold text-gray-800">
        Document Templates Management
      </h1>

      <div class="flex space-x-2 flex-shrink-0">
        <button
          @click="showUploadModal = true"
          class="flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm bg-[#0957FF] text-white shadow-md hover:bg-blue-700"
        >
          <CloudArrowUpIcon class="w-5 h-5" />
          Upload Template
        </button>
      </div>
    </div>

    <div>
      <div class="bg-white p-6 rounded-lg shadow-md">
        <n-tabs v-model:value="activeTab" type="line" animated>
          <n-tab-pane name="all" tab="All Documents">
            <AllDocumentsTab />
          </n-tab-pane>
          
          <n-tab-pane name="archived" tab="Archived">
            <ArchivedTab />
          </n-tab-pane>
          
          <n-tab-pane name="deleted" tab="Recently Deleted">
            <RecentlyDeletedTab />
          </n-tab-pane>
        </n-tabs>
      </div>
    </div>
  </div>

  <UploadTemplateModal
    :show="showUploadModal"
    @close="showUploadModal = false"
    @upload="handleUploadComplete"
  />
</template>