<script setup>
/**
 * @file General.vue
 * @description Barangay Information — name, subtitle, and logo management.
 * Logo is fetched as a blob URL (same pattern as AccountSettings.vue admin photo).
 */
import { ref, onMounted, onUnmounted } from "vue";
import { NButton, NInput, NAvatar, NSpin, useMessage } from "naive-ui";
import {
  getSystemConfig,
  updateSystemConfig,
  uploadBrgyLogo,
  getBrgyLogoUrl,
  removeBrgyLogo,
} from "@/api/systemConfigService";

const message = useMessage();

const loading       = ref(true);
const saving        = ref(false);
const uploadingLogo = ref(false);

const brgyName     = ref("");
const brgySubtitle = ref("");
const logoUrl      = ref(null);
let   logoBlobUrl  = null;   // held separately so we can revoke it

// ── Load ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  const config = await getSystemConfig();
  if (config) {
    brgyName.value     = config.brgy_name    ?? "";
    brgySubtitle.value = config.brgy_subname ?? "";

    if (config.has_logo) {
      logoBlobUrl   = await getBrgyLogoUrl();
      logoUrl.value = logoBlobUrl;
    }
  }
  loading.value = false;
});

onUnmounted(() => {
  if (logoBlobUrl) URL.revokeObjectURL(logoBlobUrl);
});

// ── Save Info ─────────────────────────────────────────────────────────────────
const saveInfo = async () => {
  if (!brgyName.value.trim()) {
    message.warning("Barangay name cannot be empty.");
    return;
  }
  saving.value = true;
  try {
    await updateSystemConfig({
      brgy_name:    brgyName.value.trim(),
      brgy_subname: brgySubtitle.value.trim(),
    });
    message.success("Barangay information updated.");
  } catch {
    message.error("Failed to save. Please try again.");
  } finally {
    saving.value = false;
  }
};

// ── Logo Upload ───────────────────────────────────────────────────────────────
const handleUploadLogo = () => {
  const input = document.createElement("input");
  input.type   = "file";
  input.accept = "image/png,image/jpeg,image/webp,image/svg+xml";
  input.onchange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowedTypes = ["image/png", "image/jpeg", "image/webp", "image/svg+xml"];
    if (!allowedTypes.includes(file.type)) {
      message.error("Only PNG, JPG, WebP, or SVG files are allowed.");
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      message.error("File is too large. Maximum size is 2 MB.");
      return;
    }

    uploadingLogo.value = true;
    try {
      await uploadBrgyLogo(file);
      // Build a local blob URL immediately — no round-trip needed
      if (logoBlobUrl) URL.revokeObjectURL(logoBlobUrl);
      logoBlobUrl   = URL.createObjectURL(file);
      logoUrl.value = logoBlobUrl;
      message.success("Logo updated successfully.");
    } catch {
      message.error("Failed to upload logo. Please try again.");
    } finally {
      uploadingLogo.value = false;
    }
  };
  input.click();
};

const handleRemoveLogo = async () => {
  uploadingLogo.value = true;
  try {
    await removeBrgyLogo();
    if (logoBlobUrl) URL.revokeObjectURL(logoBlobUrl);
    logoBlobUrl   = null;
    logoUrl.value = null;
    message.warning("Logo has been removed.");
  } catch {
    message.error("Failed to remove logo.");
  } finally {
    uploadingLogo.value = false;
  }
};

// Derive initials for the avatar fallback
const initials = () => {
  const parts = brgyName.value.trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return "BR";
};
</script>

<template>
  <div v-if="loading" class="flex justify-center items-center py-16">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>

  <div v-else class="flex gap-8 items-start max-w-5xl">

    <!-- ── Left: Logo card ─────────────────────────────────────────────────── -->
    <div class="w-64 flex-shrink-0 flex flex-col items-center gap-4
                border border-gray-200 rounded-xl p-6 bg-gray-50">

      <n-spin :show="uploadingLogo">
        <n-avatar
          round
          :size="96"
          :src="logoUrl || undefined"
          :style="{ background: 'linear-gradient(135deg,#0066d4,#011784)', color: 'white', fontSize: '32px', fontWeight: '700' }"
          class="ring-4 ring-white shadow-md"
        >
          <span v-if="!logoUrl">{{ initials() }}</span>
        </n-avatar>
      </n-spin>

      <div class="text-center">
        <p class="text-[15px] font-semibold text-gray-800 leading-tight">{{ brgyName || "Barangay" }}</p>
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

      <p class="text-[11px] text-gray-400 text-center">JPG, PNG, WebP, SVG · Max 2 MB</p>
    </div>

    <!-- ── Right: Form ────────────────────────────────────────────────────── -->
    <div class="flex-1 flex flex-col gap-8">

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
            <n-input v-model:value="brgySubtitle" placeholder="e.g. Amadeo, Cavite" />
            <p class="text-[11px] text-gray-400">
              These details appear on printed documents, the kiosk welcome screen, and all official barangay forms.
            </p>
          </div>
        </div>
      </div>

      <div>
        <n-button type="primary" :loading="saving" @click="saveInfo">Save Changes</n-button>
      </div>

    </div>
  </div>
</template>