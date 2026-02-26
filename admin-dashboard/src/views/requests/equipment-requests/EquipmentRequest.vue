<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NTabs, NTabPane, NPopover, NDatePicker, NInput, NSelect, NButton } from 'naive-ui';
import { 
  FunnelIcon, 
  ArrowUturnLeftIcon, 
  TrashIcon
} from '@heroicons/vue/24/outline';

import PageTitle from '@/components/shared/PageTitle.vue';
import PendingTab from '@/views/requests/equipment-requests/subtabs/PendingTab.vue';
import ApprovedTab from '@/views/requests/equipment-requests/subtabs/ApprovedTab.vue';
import PickedUpTab from '@/views/requests/equipment-requests/subtabs/PickedUpTab.vue';
import ReturnedTab from '@/views/requests/equipment-requests/subtabs/ReturnedTab.vue';
import RejectedTab from '@/views/requests/equipment-requests/subtabs/RejectedTab.vue';

const route = useRoute();
const router = useRouter();
const searchQuery = ref('');

const tabRef = ref(null);
const showFilterPopover = ref(false);

// Filter state
const filterState = ref({
  requestedDate: null,
  borrowingPeriodStart: null,
  borrowingPeriodEnd: null,
  paymentStatus: null
});

const paymentStatusOptions = [
  { label: 'All Status', value: null },
  { label: 'Paid', value: 'paid' },
  { label: 'Unpaid', value: 'unpaid' }
];

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
  pickedup: PickedUpTab,
  returned: ReturnedTab,
  rejected: RejectedTab
};

const activeTab = computed({
  get: () => route.params.status || 'pending',
  set: (newStatus) => {
    router.push({ name: 'EquipmentRequests', params: { status: newStatus } });
  }
});

const currentTabComponent = computed(() => {
  return tabMap[activeTab.value] || PendingTab;
});

const handleFilterClear = () => {
  filterState.value = {
    requestedDate: null,
    borrowingPeriodStart: null,
    borrowingPeriodEnd: null,
    paymentStatus: null
  };
};

const hasActiveFilters = computed(() => {
  return !!(
    filterState.value.requestedDate ||
    filterState.value.borrowingPeriodStart ||
    filterState.value.borrowingPeriodEnd ||
    filterState.value.paymentStatus
  );
});
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="Equipment Requests" />
        <p class="text-sm text-gray-500 mt-1">Manage Equipment Requests submitted by residents</p>
      </div>
      
      <div class="flex items-center gap-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />

        <n-popover
          v-model:show="showFilterPopover"
          trigger="click"
          placement="bottom-end"
          :show-arrow="false"
          style="padding: 0;"
        >
          <template #trigger>
            <button 
              :class="[
                'flex items-center px-4 py-2 border rounded-lg text-sm font-medium transition-colors',
                hasActiveFilters 
                  ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700' 
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              ]"
            >
              <FunnelIcon class="w-5 h-5 mr-2" :class="hasActiveFilters ? 'text-white' : 'text-gray-500'" />
              Filter
            </button>
          </template>
          
          <div class="w-[270px] max-h-[500px] bg-white rounded-lg overflow-hidden flex flex-col">
            <div class="p-4 border-b border-gray-200">
              <h3 class="text-[16px] font-semibold text-gray-800">Filter Equipment Request</h3>
            </div>
            
            <div class="overflow-y-auto px-6 py-4 space-y-4 flex-1">
              <!-- Requested Date -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Requested Date</label>
                <n-date-picker
                  v-model:value="filterState.requestedDate"
                  type="date"
                  clearable
                  class="w-full"
                  format="dd/MM/yyyy"
                  placeholder="Start date"
                />
              </div>

              <!-- Borrowing Period -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Requested Date Range</label>
                <div class="flex flex-col gap-2">
                  <n-date-picker
                    v-model:value="filterState.borrowingPeriodStart"
                    type="date"
                    clearable
                    class="w-full"
                    format="dd/MM/yyyy"
                    placeholder="Start date"
                  />
                  <n-date-picker
                    v-model:value="filterState.borrowingPeriodEnd"
                    type="date"
                    clearable
                    class="w-full"
                    format="dd/MM/yyyy"
                    placeholder="End date"
                  />
                </div>
              </div>

              <!-- Payment Status -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Payment Status</label>
                <n-select
                  v-model:value="filterState.paymentStatus"
                  :options="paymentStatusOptions"
                  placeholder="All Status"
                />
              </div>

            </div>

            <!-- Action Buttons -->
            <div class="flex justify-end space-x-2 p-4 border-t border-gray-200">
              <n-button
                @click="handleFilterClear"
                class="px-6"
                secondary
              >
                Clear
              </n-button>
            </div>
          </div>
        </n-popover>

        <button 
          @click="triggerUndo"
          :disabled="selectionState === 'none' || isPendingTab"
          :class="[
            (selectionState === 'none' || isPendingTab) 
              ? 'opacity-50 cursor-not-allowed' 
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
          class="p-2 border border-red-400 rounded-lg transition-colors"
        >
          <TrashIcon class="w-5 h-5 text-red-500" />
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
        <n-tab-pane name="pickedup" tab="PickedUp" />
        <n-tab-pane name="returned" tab="Returned" />
        <n-tab-pane name="rejected" tab="Rejected" />
      </n-tabs>
    </div>

    <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-2">
      <keep-alive>
        <component 
          :is="currentTabComponent" 
          ref="tabRef" 
          :search-query="searchQuery"
          :filters="filterState"
          :key="activeTab"
        />
      </keep-alive>
    </div>
  </div>
</template>