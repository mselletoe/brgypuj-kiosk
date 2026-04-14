<script setup>
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { NTabs, NTabPane } from "naive-ui";
import PageTitle from "@/components/shared/PageTitle.vue";
import { useAdminAuthStore } from "@/stores/auth";

import General           from "@/views/settings/system-settings/General.vue";
import AdminAccounts     from "@/views/settings/system-settings/AdminAccounts.vue";
import Security          from "@/views/settings/system-settings/Security.vue";
import Backup            from "@/views/settings/system-settings/Backup.vue";
import SystemPreferences from "@/views/settings/system-settings/SystemPreferences.vue";
import Finance           from "@/views/settings/system-settings/Finance.vue";
import AuditLogs          from "@/views/settings/system-settings/AuditLogs.vue";

const route = useRoute();
const auth  = useAdminAuthStore();

const activeTab = ref("general");

// Sync tab from URL query param (e.g. ?tab=audit)
watch(
  () => route.query.tab,
  (newTab) => {
    if (newTab === "audit" && auth.isSuperAdmin) activeTab.value = "audit";
  },
  { immediate: true }
);
</script>

<template>
  <div class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden">

    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="System Settings" />
        <p class="text-sm text-gray-500 mt-1">Manage system-wide configurations and preferences</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <n-tabs v-model:value="activeTab" type="line" animated class="flex-grow">

        <n-tab-pane name="general" tab="General" display-directive="show">
          <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">
            <General />
          </div>
        </n-tab-pane>

        <n-tab-pane name="security" tab="Security" display-directive="show">
          <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">
            <Security />
          </div>
        </n-tab-pane>

        <n-tab-pane name="backup" tab="Backup Data" display-directive="show">
          <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">
            <Backup />
          </div>
        </n-tab-pane>

        <n-tab-pane name="preferences" tab="Preferences" display-directive="show">
          <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">
            <SystemPreferences />
          </div>
        </n-tab-pane>

        <!-- Superadmin-only tabs -->
        <n-tab-pane v-if="auth.isSuperAdmin" name="finance" tab="Finance" display-directive="show">
          <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">
            <Finance />
          </div>
        </n-tab-pane>

        <n-tab-pane v-if="auth.isSuperAdmin" name="admin" tab="Admin Accounts" display-directive="show">
          <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">
            <AdminAccounts />
          </div>
        </n-tab-pane>

        <n-tab-pane v-if="auth.isSuperAdmin" name="audit" tab="Audit Log" display-directive="show">
          <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">
            <AuditLogs />
          </div>
        </n-tab-pane>

      </n-tabs>
    </div>

  </div>
</template>