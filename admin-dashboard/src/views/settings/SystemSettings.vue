<script setup>
/**
 * @file SystemSettings.vue
 * @description Main view for managing system-wide configurations and Audit Logs.
 */

import { ref, onMounted, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { NTabs, NTabPane, NButton, NAvatar, useMessage } from "naive-ui";
import PageTitle from "@/components/shared/PageTitle.vue";

// Import real audit log API fetcher
import { getAuditLogs } from "@/api/auditService";

const router = useRouter();
const route = useRoute();
const message = useMessage();

// State management for form inputs, search, and active tab
const searchQuery = ref("");
const activeTab = ref("general");

const brgyName = ref("Brgy. Poblacion Uno");

// --- REAL AUDIT LOGS LOGIC ---
const auditLogs = ref([]);
const isLoadingLogs = ref(false);

const loadAuditLogs = async () => {
  isLoadingLogs.value = true;
  try {
    const rawLogs = await getAuditLogs();
    const logsData = rawLogs.data || rawLogs || [];

    let mappedLogs = logsData.map((log) => {
      const logDate = new Date(log.created_at);
      return {
        id: log.id,
        action: log.action,
        details: log.details,
        rawDate: logDate,
        date: logDate.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
        }),
        time: logDate.toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        }),
        type: log.entity_type || "system",
      };
    });

    mappedLogs.sort((a, b) => b.rawDate - a.rawDate);
    auditLogs.value = mappedLogs;
  } catch (err) {
    console.error(err);
    message.error("Failed to load audit logs.");
  } finally {
    isLoadingLogs.value = false;
  }
};

const filteredLogs = computed(() => {
  if (!searchQuery.value) return auditLogs.value;
  const q = searchQuery.value.toLowerCase();
  return auditLogs.value.filter(
    (log) =>
      log.action.toLowerCase().includes(q) ||
      log.details.toLowerCase().includes(q),
  );
});

// Navigate to the respective table
const navigateToLog = (log) => {
  if (log.type === "doc") router.push("/document-requests");
  else if (log.type === "equip") router.push("/equipment-requests");
  else if (log.type === "resident") router.push("/residents-management");
  else if (log.type === "blotter") router.push("/blotter-kp-logs");
};

onMounted(() => {
  loadAuditLogs();

  // Watch the URL for the "tab" query parameter and switch instantly
  watch(
    () => route.query.tab,
    (newTab) => {
      if (newTab === "audit") {
        activeTab.value = "audit";
      }
    },
    { immediate: true }, // This forces it to check the moment the page loads
  );
});

const handleUploadPhoto = () => message.success("Ready to upload a new photo.");
const handleRemovePhoto = () => message.error("Photo has been removed.");
</script>

<template>
  <div
    class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden"
  >
    <div class="flex justify-between items-center mb-4">
      <div>
        <PageTitle title="System Settings" />
        <p class="text-sm text-gray-500 mt-1">
          Manage system-wide configurations and preferences
        </p>
      </div>

      <div v-if="activeTab === 'audit'" class="flex items-center gap-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search audit logs..."
          class="border border-gray-200 text-gray-700 rounded-md py-2 px-3 w-[250px] focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-400"
        />
      </div>
    </div>

    <div class="flex justify-between items-center border-b border-gray-200">
      <n-tabs v-model:value="activeTab" type="line" animated class="flex-grow">
        <n-tab-pane name="general" tab="General" />
        <n-tab-pane name="admin" tab="Admin" />
        <n-tab-pane name="backup" tab="Backup Data" />
        <n-tab-pane name="audit" tab="Audit Log" />
      </n-tabs>
    </div>

    <div class="overflow-y-auto h-[calc(100vh-260px)] pr-2 pt-6">
      <div
        v-if="activeTab === 'general'"
        class="flex flex-row justify-between w-full gap-16"
      >
        <div class="flex flex-col w-1/2 gap-6">
          <span class="font-['Inter'] font-semibold text-[16px] text-[#373737]"
            >Barangay Information</span
          >
          <div class="flex flex-col gap-2">
            <label class="font-['Inter'] font-medium text-[13px] text-[#757575]"
              >Brgy. Name</label
            >
            <input
              v-model="brgyName"
              disabled
              class="bg-[#F8F8F8] border border-[#D9D9D9] font-['Inter'] font-medium text-[15px] text-gray-800 rounded-md px-3 py-2 outline-none cursor-default pointer-events-none w-full"
            />
          </div>
        </div>

        <div class="flex flex-col gap-6 items-end mr-12">
          <div class="flex flex-col w-[320px]">
            <span
              class="font-['Inter'] font-semibold text-[16px] text-[#373737] mb-6"
              >Barangay Logo</span
            >
            <div
              class="flex flex-col items-center justify-center w-[320px] h-[320px] p-8 border border-gray-200 rounded-md bg-white"
            >
              <n-avatar
                round
                :size="150"
                style="
                  background: linear-gradient(135deg, #0066d4, #011784);
                  color: white;
                  font-size: 48px;
                  font-weight: bold;
                "
                class="mb-6 ring-4 ring-blue-50 shadow-sm"
              >
                PU
              </n-avatar>
              <span
                class="font-['Inter'] font-medium text-[13px] text-[#757575] mb-1"
                >JPG, PNG. Max 2MB</span
              >
              <div class="flex flex-row gap-4 mt-1">
                <n-button
                  ghost
                  color="#0957FF"
                  class="font-['Inter'] font-medium text-[15px] rounded-md"
                  @click="handleUploadPhoto"
                  >Upload photo</n-button
                >
                <n-button
                  ghost
                  color="#FF2B3A"
                  class="font-['Inter'] font-medium text-[15px] rounded-md"
                  @click="handleRemovePhoto"
                  >Remove Photo</n-button
                >
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'admin'" class="flex flex-col">
        <span class="text-sm text-gray-500"
          >Admin settings content pending implementation.</span
        >
      </div>

      <div v-if="activeTab === 'backup'" class="flex flex-col">
        <span class="text-sm text-gray-500"
          >Backup configuration content pending implementation.</span
        >
      </div>

      <div v-if="activeTab === 'audit'" class="flex flex-col w-full">
        <div
          v-if="isLoadingLogs"
          class="py-12 flex justify-center items-center"
        >
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
        </div>

        <div v-else class="overflow-x-auto w-full">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-gray-200">
                <th
                  class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[25%]"
                >
                  Date & Time
                </th>
                <th
                  class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[25%]"
                >
                  Action
                </th>
                <th
                  class="py-3 px-4 text-[12px] font-bold text-gray-800 uppercase tracking-wider w-[50%]"
                >
                  Details
                </th>
              </tr>
              :
            </thead>
            <tbody>
              <tr
                v-for="(log, index) in filteredLogs"
                :key="index"
                @click="navigateToLog(log)"
                class="border-b border-gray-100 last:border-none hover:bg-gray-50 transition-colors cursor-pointer group"
              >
                <td class="py-4 px-4 whitespace-nowrap flex flex-col">
                  <span
                    class="text-[13px] text-gray-800 font-medium group-hover:text-blue-600 transition-colors"
                    >{{ log.date }}</span
                  >
                  <span class="text-[11px] text-gray-400 mt-0.5">{{
                    log.time
                  }}</span>
                </td>
                <td class="py-4 px-4 text-[13px] text-gray-800">
                  <span class="inline-flex items-center gap-1.5">
                    <span
                      class="w-2 h-2 rounded-full"
                      :class="{
                        'bg-[#D946EF]': log.type === 'doc',
                        'bg-[#F59E0B]': log.type === 'equip',
                        'bg-[#3B82F6]': log.type === 'resident',
                        'bg-[#10B981]': log.type === 'blotter',
                        'bg-gray-400': ![
                          'doc',
                          'equip',
                          'resident',
                          'blotter',
                        ].includes(log.type),
                      }"
                    ></span>
                    {{ log.action }}
                  </span>
                </td>
                <td class="py-4 px-4 text-[13px] text-gray-600">
                  {{ log.details }}
                </td>
              </tr>

              <tr v-if="filteredLogs.length === 0">
                <td colspan="3" class="py-8 text-center text-gray-500 text-sm">
                  No records found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
