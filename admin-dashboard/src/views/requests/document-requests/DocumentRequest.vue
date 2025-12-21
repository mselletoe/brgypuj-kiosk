<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NTabs, NTabPane } from 'naive-ui';
import PageTitle from '@/components/shared/PageTitle.vue';
import PendingTab from '@/views/requests/document-requests/subtabs/PendingTab.vue';
import ApprovedTab from '@/views/requests/document-requests/subtabs/ApprovedTab.vue';
import ReleasedTab from '@/views/requests/document-requests/subtabs/ReleasedTab.vue';
import RejectedTab from '@/views/requests/document-requests/subtabs/RejectedTab.vue';

const route = useRoute();
const router = useRouter();
const searchQuery = ref('');
const showFilterModal = ref(false);

const tabMap = {
  pending: PendingTab,
  approved: ApprovedTab,
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

// Action handlers
const handleSort = () => {
  console.log('Sort clicked');
  // TODO: Implement sort functionality
};

const handleFilter = () => {
  showFilterModal.value = true;
  console.log('Filter clicked');
  // TODO: Implement filter modal
};

const handleUndo = () => {
  console.log('Undo clicked');
  // TODO: Implement undo functionality
};

const handleDelete = () => {
  console.log('Delete clicked');
  // TODO: Implement batch delete functionality
};

const handleSelect = () => {
  console.log('Select clicked');
  // TODO: Implement select all functionality
};
</script>

<template>
  <div class="p-6 bg-white rounded-md w-full h-full space-y-3 overflow-hidden">
    <!-- Header with Title and Action Buttons -->
    <div class="flex items-center justify-between">
      <PageTitle title="Document Requests" />
      
      <div class="flex items-center gap-2">
        <!-- Sort Button -->
        <button
          @click="handleSort"
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 7.5 7.5 3m0 0L12 7.5M7.5 3v13.5m13.5 0L16.5 21m0 0L12 16.5m4.5 4.5V7.5" />
          </svg>
          Sort
        </button>

        <!-- Filter Button -->
        <button
          @click="handleFilter"
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25 0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 1.591v2.927a2.25 2.25 0 0 1-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 0 0-.659-1.591L3.659 7.409A2.25 2.25 0 0 1 3 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0 1 12 3Z" />
          </svg>
          Filter
        </button>

        <!-- Undo Button -->
        <button
          @click="handleUndo"
          class="flex items-center justify-center w-10 h-10 text-orange-500 bg-white border border-orange-300 rounded-lg hover:bg-orange-50 transition-colors"
          title="Undo"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 15 3 9m0 0 6-6M3 9h12a6 6 0 0 1 0 12h-3" />
          </svg>
        </button>

        <!-- Delete Button -->
        <button
          @click="handleDelete"
          class="flex items-center justify-center w-10 h-10 text-red-600 bg-white border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
          title="Delete"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
          </svg>
        </button>

        <!-- Select Button -->
        <button
          @click="handleSelect"
          class="flex items-center justify-center w-10 h-10 text-blue-600 bg-white border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
          title="Select"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 3.75H6.912a2.25 2.25 0 0 0-2.15 1.588L2.35 13.177a2.25 2.25 0 0 0-.1.661V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 0 0-2.15-1.588H15M2.25 13.5h3.86a2.25 2.25 0 0 1 2.012 1.244l.256.512a2.25 2.25 0 0 0 2.013 1.244h3.218a2.25 2.25 0 0 0 2.013-1.244l.256-.512a2.25 2.25 0 0 1 2.013-1.244h3.859M12 3v8.25m0 0-3-3m3 3 3-3" />
          </svg>
        </button>
      </div>
    </div>

    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs
        v-model:value="activeTab"
        type="line"
        animated
        class="flex-grow"
      >
        <n-tab-pane name="pending" tab="Pending" />
        <n-tab-pane name="approved" tab="Approved" />
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