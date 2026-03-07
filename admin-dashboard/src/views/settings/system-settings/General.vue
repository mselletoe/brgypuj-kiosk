<script setup>
/**
 * @file General.vue
 * @description Barangay Information — name, subtitle, and logo management.
 */
import { ref } from "vue";
import { NButton, NAvatar, useMessage } from "naive-ui";

const message = useMessage();

const brgyName     = ref("Brgy. Poblacion Uno");
const brgySubtitle = ref("Municipality of San Jose, Bulacan");
const isEditing    = ref(false);

// Temp values while editing
const editName     = ref("");
const editSubtitle = ref("");

const startEdit = () => {
  editName.value     = brgyName.value;
  editSubtitle.value = brgySubtitle.value;
  isEditing.value    = true;
};

const cancelEdit = () => { isEditing.value = false; };

const saveInfo = () => {
  if (!editName.value.trim()) {
    message.warning("Barangay name cannot be empty.");
    return;
  }
  brgyName.value     = editName.value.trim();
  brgySubtitle.value = editSubtitle.value.trim();
  isEditing.value    = false;
  message.success("Barangay information updated.");
};

const handleUploadPhoto = () => message.success("Ready to upload a new logo.");
const handleRemovePhoto = () => message.warning("Logo has been removed.");
</script>

<template>
  <div class="flex flex-row justify-between w-full gap-16">

    <!-- Left: Info Form -->
    <div class="flex flex-col w-1/2 gap-6">
      <div class="flex items-center justify-between">
        <span class="font-semibold text-[16px] text-[#373737]">Barangay Information</span>
        <n-button v-if="!isEditing" size="small" ghost color="#0957FF" @click="startEdit">
          Edit
        </n-button>
      </div>

      <!-- Brgy Name -->
      <div class="flex flex-col gap-2">
        <label class="font-medium text-[13px] text-[#757575]">Brgy. Name</label>
        <input
          v-if="isEditing"
          v-model="editName"
          class="border border-blue-400 font-medium text-[15px] text-gray-800 rounded-md px-3 py-2 outline-none focus:ring-2 focus:ring-blue-200 w-full transition"
          placeholder="Enter barangay name"
        />
        <input
          v-else
          :value="brgyName"
          disabled
          class="bg-[#F8F8F8] border border-[#D9D9D9] font-medium text-[15px] text-gray-800 rounded-md px-3 py-2 outline-none cursor-default pointer-events-none w-full"
        />
      </div>

      <!-- Subtitle -->
      <div class="flex flex-col gap-2">
        <label class="font-medium text-[13px] text-[#757575]">Subtitle / Municipality</label>
        <input
          v-if="isEditing"
          v-model="editSubtitle"
          class="border border-blue-400 font-medium text-[15px] text-gray-800 rounded-md px-3 py-2 outline-none focus:ring-2 focus:ring-blue-200 w-full transition"
          placeholder="e.g. Municipality of San Jose, Bulacan"
        />
        <input
          v-else
          :value="brgySubtitle"
          disabled
          class="bg-[#F8F8F8] border border-[#D9D9D9] font-medium text-[15px] text-gray-800 rounded-md px-3 py-2 outline-none cursor-default pointer-events-none w-full"
        />
      </div>

      <!-- Save / Cancel -->
      <div v-if="isEditing" class="flex gap-3 mt-2">
        <n-button type="primary" @click="saveInfo">Save Changes</n-button>
        <n-button @click="cancelEdit">Cancel</n-button>
      </div>

      <!-- Info note -->
      <p class="text-[12px] text-gray-400 mt-2 leading-relaxed">
        These details appear on printed documents, the kiosk welcome screen, and all official barangay forms.
      </p>
    </div>

    <!-- Right: Logo -->
    <div class="flex flex-col gap-6 items-end mr-12">
      <div class="flex flex-col w-[320px]">
        <span class="font-semibold text-[16px] text-[#373737] mb-6">Barangay Logo</span>
        <div class="flex flex-col items-center justify-center w-[320px] h-[320px] p-8 border border-gray-200 rounded-md bg-white">
          <n-avatar
            round
            :size="150"
            style="background: linear-gradient(135deg, #0066d4, #011784); color: white; font-size: 48px; font-weight: bold;"
            class="mb-6 ring-4 ring-blue-50 shadow-sm"
          >
            PU
          </n-avatar>
          <span class="font-medium text-[13px] text-[#757575] mb-1">JPG, PNG. Max 2MB</span>
          <div class="flex flex-row gap-4 mt-1">
            <n-button ghost color="#0957FF" @click="handleUploadPhoto">Upload Photo</n-button>
            <n-button ghost color="#FF2B3A" @click="handleRemovePhoto">Remove Photo</n-button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>