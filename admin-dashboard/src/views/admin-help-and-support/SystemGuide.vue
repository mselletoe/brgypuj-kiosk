<script setup>
import { ref } from "vue";
import PageTitle from "@/components/shared/PageTitle.vue";
import {
  InformationCircleIcon,
  BookOpenIcon,
  CodeBracketIcon,
  ShieldCheckIcon,
} from "@heroicons/vue/24/outline";

import AboutProjectTab from "./subtabs/AboutProjectTab.vue";
import AdminUserGuideTab from "./subtabs/AdminUserGuideTab.vue";
import DocumentPlaceholderTab from "./subtabs/DocumentPlaceholderTab.vue";
import PrivacyTermsTab from "./subtabs/Privacy&TermsTab.vue";

const activeSection = ref("about");

const sections = [
  { id: "about", label: "About the Project", icon: InformationCircleIcon },
  { id: "guide", label: "Admin User Guide", icon: BookOpenIcon },
  { id: "placeholders", label: "Document Placeholders", icon: CodeBracketIcon },
  { id: "privacy", label: "Privacy & Terms", icon: ShieldCheckIcon },
];
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">
    <div class="flex-shrink-0 mb-5 section-row" style="animation-delay: 0s">
      <PageTitle title="System Guide" />
      <p class="text-sm text-gray-500 mt-1">
        System reference guide for the Barangay Kiosk System.
      </p>
    </div>

    <div class="flex-shrink-0 flex gap-1 border-b border-gray-200 mb-5 section-row" style="animation-delay: 0.08s">
      <button
        v-for="section in sections"
        :key="section.id"
        @click="activeSection = section.id"
        :class="[
          'flex items-center gap-2 px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition-colors',
          activeSection === section.id
            ? 'border-blue-600 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
        ]"
      >
        <component :is="section.icon" class="w-4 h-4" />
        {{ section.label }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto section-row" style="animation-delay: 0.16s">
      <div class="max-w-4xl mx-auto space-y-4 animate-fade-in" :key="activeSection">
        <AboutProjectTab v-if="activeSection === 'about'" />
        <AdminUserGuideTab v-if="activeSection === 'guide'" />
        <DocumentPlaceholderTab v-if="activeSection === 'placeholders'" />
        <PrivacyTermsTab v-if="activeSection === 'privacy'" />
      </div>
    </div>
  </div>
</template>
<!-- 
<style scoped>
/* Uniform animations adopted from Overview.vue */
.section-row {
  opacity: 0;
  animation: sectionUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes sectionUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}
</style> -->