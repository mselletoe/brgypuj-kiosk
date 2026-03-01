<script setup>
import { ref } from "vue";
import Drawer from "@/components/Drawer.vue";
import Header from "@/components/Header.vue";
import logo from "@/assets/logo.svg";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/vue/24/solid";

const isSidebarOpen = ref(false);
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
          :class="isSidebarOpen ? 'h-[150px] w-[150px]' : 'h-[40px] w-[40px]'"
        />
      </div>

      <div class="flex-1 overflow-visible px-3.5 pb-6">
        <Drawer :is-open="isSidebarOpen" />
      </div>
    </div>

    <div
      class="flex flex-col flex-1 pt-4 px-6 pb-6 lg:pt-5 lg:px-8 lg:pb-8 min-w-0 overflow-hidden relative z-10"
    >
      <Header />

      <main class="flex-1 overflow-y-auto rounded-2xl relative hide-scrollbar">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style>
.hide-scrollbar::-webkit-scrollbar {
  width: 0px;
  background: transparent;
}
</style>
