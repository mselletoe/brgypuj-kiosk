<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  stats: {
    type: Object,
    required: true,
  },
});

const router = useRouter();

const timeInterval = ref(null);
const currentDate = ref("");
const greeting = ref("");
const bannerVisible = ref(false);

const hasPendingActions = computed(
  () => props.stats.pendingDocs > 0 || props.stats.pendingEquip > 0,
);

const updateClock = () => {
  const now = new Date();
  currentDate.value = now.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
  const hour = now.getHours();
  if (hour < 12) greeting.value = "Good Morning";
  else if (hour < 18) greeting.value = "Good Afternoon";
  else greeting.value = "Good Evening";
};

watch(
  hasPendingActions,
  (newVal) => {
    if (newVal) {
      setTimeout(() => {
        bannerVisible.value = true;
      }, 300);
    } else {
      bannerVisible.value = false;
    }
  },
  { immediate: true },
);

onMounted(() => {
  updateClock();
  timeInterval.value = setInterval(updateClock, 60000);
});

onUnmounted(() => clearInterval(timeInterval.value));
</script>

<template>
  <div class="flex items-center justify-between gap-6 px-1">
    <div class="flex flex-col gap-1">
      <h1
        class="text-[32px] font-bold text-gray-800 tracking-tight leading-tight"
      >
        {{ greeting }}, <span class="text-blue-600">Admin</span>
      </h1>
      <p
        class="text-[14px] font-semibold text-gray-400 tracking-wide uppercase"
      >
        System Overview &bull; {{ currentDate }}
      </p>
    </div>

    <div
      v-if="hasPendingActions"
      class="banner-wrap"
      :class="bannerVisible ? 'banner-visible' : 'banner-hidden'"
    >
      <div
        class="bg-amber-50 border-l-4 border-amber-500 px-5 py-3 rounded-r-xl shadow-sm flex items-center gap-4 group"
      >
        <svg
          class="w-5 h-5 text-amber-500 shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77-1.333.192 3 1.732 3z"
          />
        </svg>
        <div>
          <h3 class="text-amber-800 font-bold text-sm">Action Required</h3>
          <p class="text-amber-700 text-xs mt-0.5">
            <span v-if="stats.pendingDocs > 0" class="font-bold">
              {{ stats.pendingDocs }} pending doc{{
                stats.pendingDocs > 1 ? "s" : ""
              }}
            </span>
            <span v-if="stats.pendingDocs > 0 && stats.pendingEquip > 0">
              &amp;
            </span>
            <span v-if="stats.pendingEquip > 0" class="font-bold">
              {{ stats.pendingEquip }} equipment request{{
                stats.pendingEquip > 1 ? "s" : ""
              }}
            </span>
            need your attention.
          </p>
        </div>
        <div class="banner-buttons">
          <button
            v-if="stats.pendingDocs > 0"
            @click="router.push('/document-requests')"
            class="px-3 py-1.5 bg-white text-amber-700 font-semibold text-xs rounded-lg shadow-sm border border-amber-200 hover:bg-amber-100 transition whitespace-nowrap"
          >
            Review Docs
          </button>
          <button
            v-if="stats.pendingEquip > 0"
            @click="router.push('/equipment-requests')"
            class="px-3 py-1.5 bg-white text-amber-700 font-semibold text-xs rounded-lg shadow-sm border border-amber-200 hover:bg-amber-100 transition whitespace-nowrap"
          >
            Review Equipment
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.banner-wrap {
  transition:
    opacity 0.5s ease,
    transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.banner-hidden {
  opacity: 0;
  /* Changed from translateX(40px) to translateY(-10px) */
  transform: translateY(-10px);
  pointer-events: none;
}

.banner-visible {
  opacity: 1;
  /* Changed to match the Y axis */
  transform: translateY(0);
  pointer-events: auto;
}
.banner-buttons {
  display: flex;
  gap: 8px;
  overflow: hidden;
  max-width: 0;
  opacity: 0;
  transition:
    max-width 0.4s cubic-bezier(0.16, 1, 0.3, 1),
    opacity 0.3s ease;
}
.group:hover .banner-buttons {
  max-width: 300px;
  opacity: 1;
}
</style>
