<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NTabs, NTabPane } from 'naive-ui';
import { 
  BarsArrowUpIcon, 
  FunnelIcon, 
  ArrowUturnLeftIcon, 
  TrashIcon
} from '@heroicons/vue/24/outline';

import PageTitle from '@/components/shared/PageTitle.vue';
import PendingTab from '@/views/requests/document-requests/subtabs/PendingTab.vue';
import ApprovedTab from '@/views/requests/document-requests/subtabs/ApprovedTab.vue';
import ReleasedTab from '@/views/requests/document-requests/subtabs/ReleasedTab.vue';
import RejectedTab from '@/views/requests/document-requests/subtabs/RejectedTab.vue';

const route = useRoute();
const router = useRouter();
const searchQuery = ref('');

const tabRef = ref(null);

const isPendingTab = computed(() => activeTab.value === 'pending');

const triggerUndo = () => {
  if (isPendingTab.value) return;
  tabRef.value?.bulkUndo();
};

const selectionState = computed(() => {
  const count = tabRef.value?.selectedCount || 0;
  const total = tabRef.value?.totalCount || 0;
  
  if (count === 0) return 'none';
  if (count > 0 && count < total) return 'partial';
  return 'all';
});

const handleMainSelectToggle = () => {
  if (selectionState.value === 'all' || selectionState.value === 'partial') {
    tabRef.value?.deselectAll();
  } else {
    tabRef.value?.selectAll();
  }
};

const triggerDelete = () => tabRef.value?.bulkDelete();

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

const handleSort = () => console.log('Sort clicked');
const handleFilter = () => console.log('Filter clicked');
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    
    <div class="flex justify-between items-center mb-4">
      <PageTitle title="Document Requests" />
      
      <div class="flex items-center space-x-2">
        <button @click="handleSort" class="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          <BarsArrowUpIcon class="w-5 h-5 mr-2 text-gray-500" />
          Sort
        </button>

        <button @click="handleFilter" class="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          <FunnelIcon class="w-5 h-5 mr-2 text-gray-500" />
          Filter
        </button>

        <button 
          @click="triggerUndo"
          :disabled="selectionState === 'none' || isPendingTab"
          :class="[
            (selectionState === 'none' || isPendingTab) 
              ? 'opacity-30 grayscale cursor-not-allowed' 
              : 'hover:bg-orange-50 cursor-pointer'
          ]"
          class="p-2 border border-orange-400 rounded-lg transition-colors"
        >
          <ArrowUturnLeftIcon class="w-5 h-5 text-orange-500" />
        </button>

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
        <n-tab-pane name="pending" tab="Pending" />
        <n-tab-pane name="approved" tab="Approved" />
        <n-tab-pane name="released" tab="Released" />
        <n-tab-pane name="rejected" tab="Rejected" />
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

    <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-2">
      <keep-alive>
        <component 
          :is="currentTabComponent" 
          ref="tabRef" 
          :search-query="searchQuery" 
          :key="activeTab"
        />
      </keep-alive>
    </div>
  </div>
</template>