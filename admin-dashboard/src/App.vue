<script setup>
import { NConfigProvider } from 'naive-ui'
import { blueThemeOverrides } from './assets/theme.js'
</script>

<template>
  <n-config-provider :theme-overrides="blueThemeOverrides">
    <router-view />
  </n-config-provider>
</template>