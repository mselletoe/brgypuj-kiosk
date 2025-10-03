<template>
  <div class="flex h-screen">

    <!-- Sidebar -->
    <div class="w-72 flex flex-col">

      <div class="p-6 border-b">
        <h1>Logo</h1>
      </div>
      
      <Drawer />
    </div>

    <!-- Main content -->
    <div class="flex flex-col flex-1">
      <Header />

      <main class="flex-1 p-6 overflow-auto bg-white">
        <router-view />
      </main>
    </div>

  </div>
</template>

<script setup>
import Drawer from '@/components/Drawer.vue'
import Header from '@/components/Header.vue'
</script>