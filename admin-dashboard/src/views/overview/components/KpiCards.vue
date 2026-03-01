<script setup>
import { useRouter } from "vue-router";

defineProps({
  stats: {
    type: Object,
    required: true,
  },
});

const router = useRouter();
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div @click="router.push('/residents-management')" class="kpi-card group">
      <div
        class="color-strip bg-gradient-to-r from-[#FFFFFF] to-[#CBFCFF]"
      ></div>
      <div class="relative z-10 flex flex-col h-full">
        <div class="flex items-center justify-between mb-4">
          <span class="kpi-label">Residents</span>
          <div class="kpi-icon text-cyan-500">
            <svg
              class="w-11 h-11"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </div>
        </div>
        <span class="kpi-value">{{ stats.residents }}</span>
        <span class="kpi-title">Registered Residents</span>
        <span class="kpi-subtext">In the barangay database</span>
      </div>
    </div>

    <div @click="router.push('/document-requests')" class="kpi-card group">
      <div
        class="color-strip bg-gradient-to-r from-[#FFFFFF] to-[#FCD6FF]"
      ></div>
      <div class="relative z-10 flex flex-col h-full">
        <div class="flex items-center justify-between mb-4">
          <span class="kpi-label">Documents</span>
          <div class="kpi-icon text-purple-400">
            <svg
              class="w-11 h-11"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
        </div>
        <span class="kpi-value">{{ stats.pendingDocs }}</span>
        <span class="kpi-title">Document Requests</span>
        <span class="kpi-subtext">Awaiting your approval</span>
      </div>
    </div>

    <div @click="router.push('/equipment-requests')" class="kpi-card group">
      <div
        class="color-strip bg-gradient-to-r from-[#FFFFFF] to-[#FFF5D3]"
      ></div>
      <div class="relative z-10 flex flex-col h-full">
        <div class="flex items-center justify-between mb-4">
          <span class="kpi-label">Equipment</span>
          <div class="kpi-icon text-yellow-500">
            <svg
              class="w-11 h-11"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
        </div>
        <span class="kpi-value">{{ stats.pendingEquip }}</span>
        <span class="kpi-title">Equipment Borrowed</span>
        <span class="kpi-subtext">Active borrow requests</span>
      </div>
    </div>

    <div @click="router.push('/blotter-kp-logs')" class="kpi-card group">
      <div
        class="color-strip bg-gradient-to-r from-[#FFFFFF] to-[#B6FFC2]"
      ></div>
      <div class="relative z-10 flex flex-col h-full">
        <div class="flex items-center justify-between mb-4">
          <span class="kpi-label">Blotters</span>
          <div class="kpi-icon text-green-500">
            <svg
              class="w-11 h-11"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        </div>
        <span class="kpi-value">{{ stats.activeBlotters }}</span>
        <span class="kpi-title">Blotter Cases</span>
        <span class="kpi-subtext">Active &amp; unresolved cases</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="postcss">
.kpi-card {
  @apply bg-white rounded-[20px] p-6 border border-gray-100 shadow-sm flex flex-col cursor-pointer relative overflow-hidden;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.kpi-card:hover {
  @apply shadow-lg border-transparent;
  transform: translateY(-4px);
}
.color-strip {
  @apply absolute right-0 top-0 h-full w-[15px] z-0;
  background-attachment: fixed;
  transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.kpi-card:hover .color-strip {
  @apply w-full;
}
.kpi-label {
  @apply text-[13px] font-black text-gray-400 uppercase tracking-widest;
}
.kpi-icon {
  @apply flex items-center justify-center transition-all duration-500;
}
.kpi-icon svg {
  transition: filter 0.2s ease;
}
.kpi-card:hover .kpi-icon {
  transform: scale(1.1);
}
.kpi-card:hover .kpi-icon svg {
  filter: brightness(0) invert(1) drop-shadow(0 2px 8px rgba(0, 0, 0, 0.5));
}
.kpi-value {
  @apply text-[42px] font-black text-gray-800 leading-none tracking-tighter;
}
.kpi-title {
  @apply text-[18px] font-bold text-gray-600 mt-2;
}
.kpi-subtext {
  @apply text-[12px] font-medium text-gray-400 mt-0 italic;
}
</style>
