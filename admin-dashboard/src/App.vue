<script setup>
import { NConfigProvider, NMessageProvider } from 'naive-ui'
import { blueThemeOverrides } from './assets/theme.js'
</script>

<template>
  <n-config-provider :theme-overrides="blueThemeOverrides">
    <n-message-provider>
      <router-view />
    </n-message-provider>
  </n-config-provider>
</template>