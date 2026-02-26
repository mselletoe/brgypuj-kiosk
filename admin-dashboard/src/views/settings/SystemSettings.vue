<script setup>
/**
 * @file SystemSettings.vue
 * @description Main view for managing system-wide configurations. Typography and container
 * styles have been strictly updated to match specific design requirements.
 */

import { ref } from 'vue';
import { 
  NTabs, 
  NTabPane, 
  NButton, 
  NAvatar, 
  useMessage 
} from 'naive-ui';
import PageTitle from '@/components/shared/PageTitle.vue';

// Initialize Naive UI message provider for feedback notifications
const message = useMessage();

// State management for form inputs, search, and active tab
const searchQuery = ref('');
const activeTab = ref('general');

// Barangay name set as a constant ref (read-only and unclickable in the template)
const brgyName = ref('Brgy. Poblacion Uno');

/**
 * Handles the click event for uploading a new photo.
 */
const handleUploadPhoto = () => {
  message.success('Ready to upload a new photo.');
};

/**
 * Handles the click event for removing the current photo.
 */
const handleRemovePhoto = () => {
  message.error('Photo has been removed.');
};
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="System Settings" />
        <p class="text-sm text-gray-500 mt-1">Manage system-wide configurations and preferences</p>
      </div>
      
      <div class="flex items-center gap-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search"
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />
      </div>
    </div>

    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs
        v-model:value="activeTab"
        type="line"
        animated
        class="flex-grow"
      >
        <n-tab-pane name="general" tab="General" />
        <n-tab-pane name="admin" tab="Admin" />
        <n-tab-pane name="backup" tab="Backup Data" />
        <n-tab-pane name="audit" tab="Audit Log" />
      </n-tabs>
    </div>

    <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">
      
      <div v-if="activeTab === 'general'" class="flex flex-row justify-between w-full gap-16">
        
        <div class="flex flex-col w-1/2 gap-6">
          <span class="font-['Inter'] font-semibold text-[16px] text-[#373737]">Barangay Information</span>
          
          <div class="flex flex-col gap-2">
            <label class="font-['Inter'] font-medium text-[13px] text-[#757575]">Brgy. Name</label>
            
            <input 
              v-model="brgyName" 
              disabled
              class="bg-[#F8F8F8] border border-[#D9D9D9] font-['Inter'] font-medium text-[15px] text-gray-800 rounded-md px-3 py-2 outline-none cursor-default pointer-events-none w-full" 
            />
          </div>
        </div>

        <div class="flex flex-col gap-6 items-end mr-12">
          <div class="flex flex-col w-[320px]">
            <span class="font-['Inter'] font-semibold text-[16px] text-[#373737] mb-6">Barangay Logo</span>
            
            <div class="flex flex-col items-center justify-center w-[320px] h-[320px] p-8 border border-gray-200 rounded-md bg-white">
              
              <n-avatar 
                round 
                :size="150" 
                style="background: linear-gradient(135deg, #0066D4, #011784); color: white; font-size: 48px; font-weight: bold;"
                class="mb-6 ring-4 ring-blue-50 shadow-sm"
              >
                PU
              </n-avatar>
              
              <span class="font-['Inter'] font-medium text-[13px] text-[#757575] mb-1">JPG, PNG. Max 2MB</span>
              
              <div class="flex flex-row gap-4 mt-1">
                <n-button 
                  ghost 
                  color="#0957FF"
                  class="font-['Inter'] font-medium text-[15px] rounded-md" 
                  @click="handleUploadPhoto"
                >
                  Upload photo
                </n-button>
                
                <n-button 
                  ghost 
                  color="#FF2B3A"
                  class="font-['Inter'] font-medium text-[15px] rounded-md" 
                  @click="handleRemovePhoto"
                >
                  Remove Photo
                </n-button>
              </div>

            </div>
          </div>
        </div>

      </div>

      <div v-if="activeTab === 'admin'" class="flex flex-col">
        <span class="text-sm text-gray-500">Admin settings content pending implementation.</span>
      </div>
      
      <div v-if="activeTab === 'backup'" class="flex flex-col">
        <span class="text-sm text-gray-500">Backup configuration content pending implementation.</span>
      </div>
      
      <div v-if="activeTab === 'audit'" class="flex flex-col">
        <span class="text-sm text-gray-500">Audit logs view pending implementation.</span>
      </div>

    </div>
  </div>
</template>