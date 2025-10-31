<script setup>
import { ref} from 'vue'
import { NTabs, NTabPane } from 'naive-ui'
import PageTitle from '@/components/shared/PageTitle.vue'
import PendingTab from '@/views/requests/subtabs/PendingTab.vue'
import ProcessingTab from '@/views/requests/subtabs/ProcessingTab.vue'
import ReadyTab from '@/views/requests/subtabs/ReadyTab.vue'
import ReleasedTab from '@/views/requests/subtabs/ReleasedTab.vue'
import RejectedTab from '@/views/requests/subtabs/RejectedTab.vue'

const activeTab = ref('pending')
</script>

<template>
  <div class="p-6 bg-white rounded-md w-full h-full space-y-5">
    <PageTitle title="Requests Management" />

    <n-tabs v-model:value="activeTab" type="line" animated>
      <n-tab-pane name="pending" tab="Pending">
        <PendingTab />
      </n-tab-pane>
      
      <n-tab-pane name="processing" tab="Processing">
        <ProcessingTab />
      </n-tab-pane>
      
      <n-tab-pane name="ready" tab="Ready">
        <ReadyTab />
      </n-tab-pane>
      
      <n-tab-pane name="completed" tab="Completed">
        <CompletedTab />
      </n-tab-pane>
      
      <n-tab-pane name="rejected" tab="Rejected">
        <RejectedTab />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>