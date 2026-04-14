<script setup>
/**
 * @file views/feedback-and-reports/FeedbackAndReports.vue
 * @description Admin view for managing resident feedback and reports.
 * Organizes entries into two tabs (Feedbacks, Reports) driven by the route param.
 * Provides shared toolbar actions (search, undo, delete, select all) that
 * delegate to the active tab component via a template ref.
 */

import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { NTabs, NTabPane } from "naive-ui";
import { TrashIcon, ArrowUturnLeftIcon } from "@heroicons/vue/24/outline";
import PageTitle from "@/components/shared/PageTitle.vue";
import FeedbackTab from "@/views/feedback-and-reports/subtabs/FeedbackTab.vue";
import ReportsTab from "@/views/feedback-and-reports/subtabs/ReportsTab.vue";
import { useSearchSync } from "@/composables/useSearchSync";

const route = useRoute();
const router = useRouter();
const searchQuery = ref("");
useSearchSync(searchQuery);
const activeTabRef = ref(null);

// =============================================================================
// TAB ROUTING
// =============================================================================
const tabMap = {
  feedbacks: FeedbackTab,
  reports: ReportsTab,
};

const activeTab = computed({
  get: () => route.params.status || "feedbacks",
  set: (val) => {
    router.push({ name: "FeedbackReports", params: { status: val } });
  },
});

const currentTabComponent = computed(
  () => tabMap[activeTab.value] || FeedbackTab,
);

// =============================================================================
// SELECTION STATE
// =============================================================================
const selectedCount = computed(() => activeTabRef.value?.selectedCount ?? 0);
const totalCount = computed(() => activeTabRef.value?.totalCount ?? 0);

const selectionState = computed(() => {
  if (selectedCount.value === 0) return "none";
  if (selectedCount.value === totalCount.value) return "all";
  return "partial";
});

const handleMainSelectToggle = () => {
  if (!activeTabRef.value) return;

  if (selectionState.value === "all") {
    activeTabRef.value.deselectAll?.();
  } else {
    activeTabRef.value.selectAll?.();
  }
};

// =============================================================================
// TOOLBAR ACTIONS
// =============================================================================
const triggerDelete = () => {
  if (!activeTabRef.value || selectedCount.value === 0) return;
  activeTabRef.value.bulkDelete?.();
};

const triggerUndo = () => {
  if (!activeTabRef.value || selectedCount.value === 0) return;
  activeTabRef.value.bulkUndo?.();
};
</script>

<template>
  <div class="flex flex-col p-4 sm:p-6 bg-white rounded-md w-full h-full overflow-hidden">

    <!-- HEADER -->
    <div class="grid grid-cols-1 md:grid-cols-[1fr_auto] items-center gap-4 mb-4">

      <!-- TITLE -->
      <div class="min-w-0">
        <PageTitle title="Feedbacks and Reports" />
        <p class="text-sm text-gray-500 mt-1">Manage feedbacks and reports</p>
      </div>

      <!-- CONTROLS -->
      <div class="flex flex-nowrap items-center justify-start md:justify-end gap-3 w-full">

        <!-- SEARCH -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 flex-1 md:flex-none md:w-[180px] lg:w-[250px] min-w-0 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />

        <!-- ACTION BUTTONS -->
        <div class="flex items-center gap-2 sm:gap-3">

          <!-- UNDO (Reports tab only) -->
          <div v-if="activeTab === 'reports'" class="relative group inline-block">
            <button
              @click="triggerUndo"
              :disabled="selectionState === 'none'"
              :class="[
                selectionState === 'none'
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-orange-50 cursor-pointer',
              ]"
              class="p-2 border border-orange-400 rounded-lg transition-colors"
            >
              <ArrowUturnLeftIcon class="w-5 h-5 text-orange-500" />
            </button>
            <div class="absolute hidden sm:block -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">
              Undo
            </div>
          </div>

          <!-- DELETE -->
          <div class="relative group inline-block">
            <button
              @click="triggerDelete"
              :disabled="selectionState === 'none'"
              :class="[
                selectionState === 'none'
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-red-50',
              ]"
              class="p-2 border border-red-400 rounded-lg transition-colors"
            >
              <TrashIcon class="w-5 h-5 text-red-500" />
            </button>
            <div class="absolute hidden sm:block -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">
              Delete
            </div>
          </div>

          <!-- SELECT ALL -->
          <div class="relative group inline-block">
            <div
              class="flex items-center border rounded-lg"
              :class="selectionState !== 'none' ? 'border-blue-600' : 'border-gray-400'"
            >
              <button
                @click="handleMainSelectToggle"
                class="p-2 hover:bg-gray-50 rounded-lg flex items-center"
              >
                <div
                  class="w-5 h-5 border rounded flex items-center justify-center"
                  :class="selectionState !== 'none' ? 'bg-blue-600 border-blue-600' : 'border-gray-400'"
                >
                  <div v-if="selectionState === 'partial'" class="w-2 h-0.5 bg-white"></div>
                  <svg
                    v-if="selectionState === 'all'"
                    class="w-3 h-3 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M5 13l4 4L19 7"/>
                  </svg>
                </div>
              </button>
            </div>
            <div class="absolute hidden sm:block -bottom-8 left-1/2 -translate-x-1/2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 bg-[#013C6D] text-[#E5F5FF] text-xs px-2 py-1 rounded whitespace-nowrap shadow-md z-50">
              Select All
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- TABS -->
    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs v-model:value="activeTab" type="line" animated class="flex-grow">
        <n-tab-pane name="feedbacks" tab="Feedbacks" />
        <n-tab-pane name="reports" tab="Reports" />
      </n-tabs>
    </div>

    <!-- CONTENT -->
    <div class="overflow-y-auto h-[calc(100vh-320px)] sm:h-[calc(100vh-260px)] pr-2 pt-2">
      <keep-alive>
        <component
          :is="currentTabComponent"
          ref="activeTabRef"
          :search-query="searchQuery"
          :key="activeTab"
        />
      </keep-alive>
    </div>

  </div>
</template>