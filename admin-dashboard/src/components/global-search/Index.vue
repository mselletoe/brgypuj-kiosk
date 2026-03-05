<script setup>
import { ref } from "vue";
import { MagnifyingGlassIcon } from "@heroicons/vue/24/solid";
import GlobalSearchModal from "./GlobalSearchModal.vue";

const isOpen = ref(false);
</script>

<template>
  <button
    @click="isOpen = true"
    class="w-11 h-11 flex items-center justify-center text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all"
  >
    <MagnifyingGlassIcon class="h-6 w-6" />
  </button>

  <GlobalSearchModal v-model="isOpen" />
</template>
