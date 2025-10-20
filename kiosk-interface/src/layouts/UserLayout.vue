<script setup>
import Header from '@/components/Header.vue'
</script>

<template>
  <div class="flex h-screen flex-col">

    <Header />

    <main class="flex-1 overflow-auto pt-20 px-8">
      <router-view />
    </main>

  </div>
</template>