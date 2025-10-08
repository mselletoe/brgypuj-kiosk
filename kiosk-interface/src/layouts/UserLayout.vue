<script setup>
import Header from '@/components/Header.vue'
</script>

<template>
  <div class="flex h-screen">

    <!-- Sidebar -->
    <div class="w-72 flex flex-col">

      <div class="p-8 border-b">
        <h1>Logo</h1>
      </div>
      
      <Drawer />
    </div>

    <!-- Main content -->
    <div class="flex flex-col flex-1 p-8">
      <Header />

      <main class="flex-1 overflow-auto">
        <router-view />
      </main>
    </div>

  </div>
</template>