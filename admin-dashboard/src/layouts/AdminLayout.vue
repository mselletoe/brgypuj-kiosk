<script setup>
import Drawer from '@/components/Drawer.vue'
import Header from '@/components/Header.vue'
import logo from '@/assets/logo.svg'
</script>

<template>
  <div class="flex h-screen">

    <!-- Sidebar -->
    <div class="w-72 flex flex-col p-8">

      <div class="mb-8 border-b">
        <img :src="logo" alt="Logo" class="h-100 object-contain" />
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