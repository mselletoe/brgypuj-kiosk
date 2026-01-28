<script setup>
import Header from '@/layouts/Header.vue'
</script>

<template>
  <div class="flex h-screen flex-col items-center p-8">

    <Header />

    <main class="flex-1 overflow-auto pt-12 w-full">
      <router-view />
    </main>

  </div>
</template>