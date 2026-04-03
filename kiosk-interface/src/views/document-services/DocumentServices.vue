<script setup>
/**
 * @file views/document-services/DocumentServices.vue
 * @description Kiosk document services listing view.
 * Acts as a parent route that displays all available document types as
 * selectable cards. When a document type is selected, the router renders
 * the child route (DocumentFormWrapper) in place of the card grid.
 */

import { useRoute, useRouter } from "vue-router";
import { computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import { useDocumentTypesStore } from "@/stores/documentTypes";

const route = useRoute();
const router = useRouter();
const { t } = useI18n();

const isParent = () => !route.params.docType;
const goBack = () => router.push("/home");

// =============================================================================
// STORE
// =============================================================================
const documentTypesStore = useDocumentTypesStore();

const documents = computed(() =>
  documentTypesStore.types.map((doc) => ({
    request_type_name: doc.doctype_name,
    description: doc.description,
    price: doc.price,
  }))
);
const loading = computed(() => documentTypesStore.loading);
const error   = computed(() => documentTypesStore.error);

// =============================================================================
// LIFECYCLE
// =============================================================================
onMounted(() => documentTypesStore.fetchTypes());
</script>

<template>
  <div class="flex flex-col w-full h-full">

    <!-- ─ HEADER ─────────────────────────────────────────────── -->
    <div v-if="isParent()" class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          {{ t('documentServicesTitle') }}
        </h1>
        <p class="text-[#03335C] -mt-2">
          {{ t('documentServicesSubtitle') }}
        </p>
      </div>
    </div>

    <!-- ─ LOADING ─────────────────────────────────────────────── -->
    <div
      v-if="loading"
      class="flex flex-col justify-center items-center py-20 flex-1"
    >
      <div class="loader-dots mb-4">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
      <p class="text-[#03335C] text-lg font-semibold">{{ t('loadingServices') }}</p>
    </div>

    <!-- ─ ERROR STATE ─────────────────────────────────────────────── -->
    <div v-if="error" class="text-center text-red-500 py-10">{{ error }}</div>

    <!-- ─ DOCUMENT OPTIONS ─────────────────────────────────────────────── -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="isParent() && !loading && !error">
        <div
          v-if="documents.length === 0"
          class="flex justify-center items-center py-20"
        >
          <p class="text-gray-400 text-xl font-medium">{{ t('noDocumentServices') }}</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
          <router-link
            v-for="doc in documents"
            :key="doc.request_type_name"
            :to="`/document-services/${doc.request_type_name.toLowerCase().replace(/\s+/g, '-')}`"
            class="group flex flex-col p-6 rounded-2xl border border-gray-200 shadow-lg bg-white hover:bg-[#003A6B] hover:text-white transition-all duration-300 ease-in-out"
          >
            <h2
              class="text-[30px] text-[#003A6B] font-bold mb-2 group-hover:text-white transition-all duration-300 ease-in-out"
            >
              {{ doc.request_type_name }}
            </h2>

            <p
              class="text-gray-500 group-hover:text-gray-100 text-sm mb-6 transition-all duration-300 ease-in-out"
            >
              {{ doc.description }}
            </p>

            <div
              class="mt-auto flex justify-between items-center font-semibold text-[#003A6B] group-hover:text-white transition-all duration-300 ease-in-out"
            >
              <span>{{ t('fee') }}</span>
              <span class="text-[#09AA44] group-hover:text-white transition-all"
                >₱{{ doc.price || 0 }}</span
              >
            </div>
          </router-link>
        </div>
      </div>
    </div>

    <!-- ─ DOCUMENT TYPE WRAPPER ─────────────────────────────────────────────── -->
    <router-view v-if="!isParent()" />
  </div>
</template>

<style scoped>
.loader-dots {
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 60px;
  height: 15px;
}

.dot {
  width: 12px;
  height: 12px;
  background-color: #03335c;
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes pulse {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>