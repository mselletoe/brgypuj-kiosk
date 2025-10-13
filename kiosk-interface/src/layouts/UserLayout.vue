<script setup>
import Header from '@/components/Header.vue'
</script>

<template>
  <div class="flex h-screen flex-col items-center p-16">

    <Header />

    <main class="flex-1 overflow-auto pt-[2.5em] w-full">
      <router-view />
    </main>

  </div>
</template>