<script setup>
/**
 * @file AccountSettings.vue
 * @description Admin account settings page to manage profile, security, preferences.
 */

import { ref } from "vue";
import {
  NTabs,
  NTabPane,
  NInput,
  NButton,
  NSwitch,
  NSelect,
  NAvatar,
  useMessage,
} from "naive-ui";
import { PhotoIcon, TrashIcon } from "@heroicons/vue/24/outline";
import PageTitle from "@/components/shared/PageTitle.vue";

// Initialize NaiveUI message service
const message = useMessage();

// Tab state management
const activeTab = ref("Profile");

// Profile data state
const profileData = ref({
  name: "Jett To Holidays",
  role: "Barangay Administrator",
  username: "admin.revivemejett",
});

// Security data state
const securityData = ref({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
});

// Preferences data state
const preferencesData = ref({
  newDocumentRequests: true,
  equipmentOverdue: true,
  defaultLandingPage: "Overview Dashboard",
});

// Select options for Default Landing Page
const landingPageOptions = [
  { label: "Overview Dashboard", value: "Overview Dashboard" },
  { label: "Document Request", value: "Document Request" },
  { label: "Equipment Request", value: "Equipment Request" },
  { label: "Residents Information", value: "Residents Information" },
];

/**
 * Handle save changes action
 */
const handleSaveChanges = () => {
  message.success("Changes saved successfully");
};

/**
 * Handle account deletion
 */
const handleDeleteAccount = () => {
  message.error("Account deletion initiated");
};

/**
 * Handle photo upload
 */
const handleUploadPhoto = () => {
  message.info("Upload photo clicked");
};

/**
 * Handle photo removal
 */
const handleRemovePhoto = () => {
  message.info("Remove photo clicked");
};
</script>

<template>
  <div
    class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden"
  >
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="Account Settings" />
        <p class="text-sm text-gray-500 mt-1">Manage your admin account</p>
      </div>
    </div>

    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs v-model:value="activeTab" type="line" animated class="flex-grow">
        <n-tab-pane name="Profile" tab="Profile" />
        <n-tab-pane name="Security" tab="Security" />
        <n-tab-pane name="Preferences" tab="Preferences" />
      </n-tabs>
    </div>

    <div class="overflow-y-auto h-[calc(100vh-200px)] pt-6 pr-2">
      <div
        v-if="activeTab === 'Profile'"
        class="flex flex-col lg:flex-row gap-12 lg:justify-between items-start"
      >
        <div class="flex-1 w-full max-w-2xl flex flex-col gap-6">
          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800">Name</label>
            <n-input
              v-model:value="profileData.name"
              disabled
              placeholder="Full Name"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800"
              >Role/Position</label
            >
            <n-input
              v-model:value="profileData.role"
              placeholder="Role/Position"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800">Username</label>
            <n-input
              v-model:value="profileData.username"
              placeholder="Username"
            />
          </div>

          <div class="pt-4">
            <n-button type="info" class="px-6" @click="handleSaveChanges">
              Save Changes
            </n-button>
          </div>
        </div>

        <div
          class="flex flex-col items-center lg:items-end w-full lg:w-auto lg:mr-12 mt-8 lg:mt-0"
        >
          <div class="flex flex-col w-[320px]">
            <span
              class="font-['Inter'] font-semibold text-[16px] text-[#373737] mb-6"
              >Profile Photo</span
            >

            <div
              class="flex flex-col items-center justify-center w-[320px] h-[320px] p-8 border border-gray-200 rounded-md bg-white"
            >
              <n-avatar
                round
                :size="150"
                src="https://api.dicebear.com/7.x/adventurer/svg?seed=Jett"
                class="mb-6 ring-4 ring-blue-50 shadow-sm bg-blue-50"
              />

              <span
                class="font-['Inter'] font-medium text-[13px] text-[#757575] mb-1"
                >JPG, PNG. Max 2MB</span
              >

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

      <div
        v-if="activeTab === 'Security'"
        class="flex flex-col lg:flex-row gap-12 lg:justify-between items-start"
      >
        <div class="flex-1 w-full max-w-2xl flex flex-col gap-6">
          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800"
              >Current Password</label
            >
            <n-input
              v-model:value="securityData.currentPassword"
              type="password"
              show-password-on="click"
              placeholder="Enter current password"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800"
              >New Password</label
            >
            <n-input
              v-model:value="securityData.newPassword"
              type="password"
              show-password-on="click"
              placeholder="Enter new password"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800"
              >Confirm New Password</label
            >
            <n-input
              v-model:value="securityData.confirmPassword"
              type="password"
              show-password-on="click"
              placeholder="Confirm new password"
            />
          </div>

          <div class="flex flex-col gap-2 pt-1">
            <div class="flex items-center gap-1 text-[12px] font-bold">
              <span class="text-gray-800">Password Strength:</span>
              <span class="text-yellow-500">Medium</span>
            </div>
            <div class="w-full bg-gray-200 h-1 rounded-full">
              <div class="bg-yellow-500 h-1 rounded-full w-[50%]"></div>
            </div>
            <p class="text-[11px] text-gray-400 mt-1">
              Password must be at least 8 characters with uppercase, lowercase,
              and numbers
            </p>
          </div>

          <div class="pt-4">
            <n-button type="info" class="px-6" @click="handleSaveChanges">
              Save Changes
            </n-button>
          </div>
        </div>

        <div
          class="w-full lg:w-[400px] border-2 border-[#B1202A] bg-[#fff5f5] rounded-lg p-6 flex flex-col lg:mr-16"
        >
          <h3 class="font-['Inter'] font-bold text-[16px] text-[#B1202A] mb-2">
            Delete Account
          </h3>
          <p
            class="font-['Inter'] font-normal text-[14px] text-[#000000] mb-6 leading-relaxed"
          >
            Permanently delete your admin account and all associated data. This
            action cannot be undone.
          </p>
          <div class="flex justify-end mt-auto">
            <n-button
              color="#FF0000"
              text-color="#FFFFFF"
              class="font-bold font-['Inter']"
              @click="handleDeleteAccount"
            >
              Delete Account
            </n-button>
          </div>
        </div>
      </div>

      <div
        v-if="activeTab === 'Preferences'"
        class="flex flex-col md:flex-row gap-16"
      >
        <div class="flex-1 max-w-md flex flex-col gap-6">
          <h3 class="font-bold text-gray-800 text-[15px]">
            Notification Settings
          </h3>

          <div class="flex flex-col gap-6">
            <div
              class="flex items-center justify-between border-b border-gray-100 pb-4"
            >
              <div class="flex flex-col">
                <p class="text-[13px] font-bold text-gray-800">
                  New Document Requests
                </p>
                <p class="text-[11px] text-gray-500 mt-1">
                  Alert when new document requested
                </p>
              </div>
              <n-switch v-model:value="preferencesData.newDocumentRequests" />
            </div>

            <div
              class="flex items-center justify-between border-b border-gray-100 pb-4"
            >
              <div class="flex flex-col">
                <p class="text-[13px] font-bold text-gray-800">
                  Equipment Overdue
                </p>
                <p class="text-[11px] text-gray-500 mt-1">
                  Alert when equipment is overdue
                </p>
              </div>
              <n-switch v-model:value="preferencesData.equipmentOverdue" />
            </div>
          </div>

          <div class="pt-4">
            <n-button type="info" class="px-6" @click="handleSaveChanges">
              Save Changes
            </n-button>
          </div>
        </div>

        <div class="flex-1 max-w-md flex flex-col gap-6">
          <h3 class="font-bold text-gray-800 text-[15px]">
            Display Preferences
          </h3>

          <div class="flex flex-col gap-2">
            <label class="text-[12px] font-bold text-gray-800"
              >Default Landing Page</label
            >
            <n-select
              v-model:value="preferencesData.defaultLandingPage"
              :options="landingPageOptions"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
