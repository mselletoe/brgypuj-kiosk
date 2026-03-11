<script setup>
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import Drawer from "@/components/Drawer.vue";
import Header from "@/components/Header.vue";
import logo from "@/assets/logo.svg";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/vue/24/solid";

const isSidebarOpen = ref(false);
const route = useRoute();

// Only the overview/dashboard page gets the edge-to-edge scroll treatment
const isOverview = computed(
  () =>
    route.path === "/" ||
    route.path === "/overview" ||
    route.name === "overview",
);
</script>

<template>
  <div class="flex h-screen bg-[#F4F7FB] overflow-hidden">
    <div
      class="flex flex-col bg-white border-r border-gray-200 transition-all duration-300 ease-in-out relative z-30 shadow-sm"
      :class="isSidebarOpen ? 'w-[250px]' : 'w-[80px]'"
    >
      <button
        @click="isSidebarOpen = !isSidebarOpen"
        class="absolute -right-[18px] top-[42px] w-9 h-9 bg-white border-2 border-gray-100 rounded-full flex items-center justify-center text-gray-500 hover:text-blue-600 hover:border-blue-500 shadow-md hover:shadow-lg transition-all duration-200 z-50 group"
      >
        <ChevronLeftIcon
          v-if="isSidebarOpen"
          class="w-5 h-5 transition-transform group-active:scale-90"
        />
        <ChevronRightIcon
          v-else
          class="w-5 h-5 transition-transform group-active:scale-90"
        />
      </button>

      <div
        class="h-[120px] flex items-center justify-center px-4 transition-all duration-300"
      >
        <img
          :src="logo"
          alt="Logo"
          class="object-contain transition-all duration-300 mt-3"
          :class="isSidebarOpen ? 'h-[130px] w-[130px]' : 'h-[40px] w-[40px]'"
        />
      </div>

      <div class="flex-1 overflow-visible px-3.5 pb-6">
        <Drawer :is-open="isSidebarOpen" />
      </div>
    </div>

    <!--
      Content wrapper:
      - Overview page: remove px padding so the scrollbar sits flush at the
        window edge. The overview content itself handles its own inner padding.
      - All other pages: keep original px-6/px-8 padding as before.
    -->
    <div
      class="flex flex-col flex-1 min-w-0 overflow-hidden relative z-10"
      :class="
        isOverview
          ? 'pt-4 lg:pt-5 pb-0'
          : 'pt-4 px-6 pb-6 lg:pt-5 lg:px-8 lg:pb-8'
      "
    >
      <!--
        Header: on overview we add back horizontal padding so it aligns
        with the rest of the header items, not the page edge.
      -->
      <div :class="isOverview ? 'px-6 lg:px-8' : ''">
        <Header />
      </div>

      <!--
        Main scroll area:
        - Overview: full-width scroll, no rounded clip, content adds own padding
        - Others: original rounded-2xl with hide-scrollbar
      -->
      <main
        class="flex-1 overflow-y-auto relative"
        :class="
          isOverview
            ? 'overview-scrollbar px-6 lg:px-8 pb-6 lg:pb-8'
            : 'rounded-2xl hide-scrollbar'
        "
      >
        <router-view />
      </main>
    </div>
  </div>
</template>

<style>
/* Original hide-scrollbar for non-overview pages */
.hide-scrollbar::-webkit-scrollbar {
  width: 0px;
  background: transparent;
}

/*
  Overview scrollbar: thin, styled, flush to the right edge.
  Only applied when .overview-scrollbar class is present.
*/
.overview-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.overview-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.overview-scrollbar::-webkit-scrollbar-thumb {
  background-color: #d1d5db;
  border-radius: 99px;
}
.overview-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #9ca3af;
}
</style>
