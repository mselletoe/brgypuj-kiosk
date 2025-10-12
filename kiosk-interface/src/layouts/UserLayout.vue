<script setup>
import Header from '@/components/Header.vue'
</script>

<template>
  <div class="flex h-screen flex-col items-center p-8">

    <Header />

    <main class="flex-1 overflow-auto pt-[95px] w-full">
      <router-view />
    </main>

  </div>
</template>