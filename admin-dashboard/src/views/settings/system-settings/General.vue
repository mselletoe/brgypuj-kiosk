<script setup>
/**
 * @file GeneralSettings.vue
 * @description Barangay Information — name, subtitle, and logo management.
 */
import { ref } from "vue";
import { NButton, NInput, NAvatar, NSpin, useMessage } from "naive-ui";

const message = useMessage();

const brgyName     = ref("Brgy. Poblacion Uno");
const brgySubtitle = ref("Municipality of San Jose, Bulacan");
const uploadingLogo = ref(false);
const logoUrl       = ref(null);

const saveInfo = () => {
  if (!brgyName.value.trim()) {
    message.warning("Barangay name cannot be empty.");
    return;
  }
  message.success("Barangay information updated.");
};

const handleUploadLogo = () => message.success("Ready to upload a new logo.");
const handleRemoveLogo = () => {
  logoUrl.value = null;
  message.warning("Logo has been removed.");
};
</script>

<template>
  <div class="flex gap-8 items-start max-w-5xl">

    <!-- ── Left: Logo card (mirrors AccountSettings profile card) ─────────── -->
    <div class="w-64 flex-shrink-0 flex flex-col items-center gap-4
                border border-gray-200 rounded-xl p-6 bg-gray-50">

      <n-spin :show="uploadingLogo">
        <n-avatar
          round
          :size="96"
          :src="logoUrl || undefined"
          style="background: linear-gradient(135deg, #0066d4, #011784); color: white; font-size: 32px; font-weight: 700;"
          class="ring-4 ring-white shadow-md"
        >
          <span v-if="!logoUrl">PU</span>
        </n-avatar>
      </n-spin>

      <div class="text-center">
        <p class="text-[15px] font-semibold text-gray-800 leading-tight">{{ brgyName }}</p>
        <p class="text-[12px] text-gray-400 mt-0.5">{{ brgySubtitle }}</p>
      </div>

      <div class="w-full border-t border-gray-200 pt-4 flex flex-col gap-2">
        <button
          @click="handleUploadLogo"
          :disabled="uploadingLogo"
          class="w-full text-[13px] font-medium text-[#0957FF] border border-[#0957FF]
                 rounded-md py-1.5 hover:bg-blue-50 transition-colors disabled:opacity-50"
        >
          {{ logoUrl ? 'Change Logo' : 'Upload Logo' }}
        </button>
        <button
          v-if="logoUrl"
          @click="handleRemoveLogo"
          :disabled="uploadingLogo"
          class="w-full text-[13px] font-medium text-red-500 border border-red-300
                 rounded-md py-1.5 hover:bg-red-50 transition-colors disabled:opacity-50"
        >
          Remove Logo
        </button>
      </div>

      <p class="text-[11px] text-gray-400 text-center">JPG, PNG · Max 2 MB</p>
    </div>

    <!-- ── Right: Form (mirrors AccountSettings form sections) ───────────── -->
    <div class="flex-1 flex flex-col gap-8">

      <!-- Section: Barangay Information -->
      <div class="border-b border-gray-100">
        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">
          Barangay Information
        </h3>

        <div class="flex flex-col gap-5 max-w-lg">
          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] font-semibold text-gray-700">Brgy. Name</label>
            <n-input v-model:value="brgyName" placeholder="Enter barangay name" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-[13px] font-semibold text-gray-700">Subtitle / Municipality</label>
            <n-input v-model:value="brgySubtitle" placeholder="e.g. Municipality of San Jose, Bulacan" />
            <p class="text-[11px] text-gray-400">
              These details appear on printed documents, the kiosk welcome screen, and all official barangay forms.
            </p>
          </div>
        </div>
      </div>

      <!-- Save -->
      <div>
        <n-button type="primary" @click="saveInfo">Save Changes</n-button>
      </div>

    </div>
  </div>
</template>