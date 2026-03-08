<script setup>
import { ref, onMounted } from "vue";
import {
  PhoneIcon,
  ChatBubbleBottomCenterTextIcon,
  HomeIcon,
  InformationCircleIcon,
} from "@heroicons/vue/24/outline";
import axios from "axios";

const contact = ref({
  emergency_number: "",
  emergency_desc: "",
  phone: "",
  email: "",
  office_hours: "",
  address: "",
  tech_support: "",
});

const isLoading = ref(true);

onMounted(async () => {
  try {
    const { data } = await axios.get("/kiosk/contact");
    contact.value = data;
  } catch (err) {
    console.error("Failed to load contact info:", err);
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div v-if="isLoading" class="grid grid-cols-2 gap-4">
    <div
      v-for="i in 4"
      :key="i"
      class="bg-white border border-gray-200 rounded-xl shadow px-6 py-3 h-40 animate-pulse"
    >
      <div class="h-4 bg-gray-100 rounded w-1/3 mb-4"></div>
      <div class="h-3 bg-gray-100 rounded w-2/3 mb-2"></div>
      <div class="h-3 bg-gray-100 rounded w-1/2"></div>
    </div>
  </div>

  <div v-else class="grid grid-cols-2 gap-4">
    <!-- Emergency -->
    <div
      class="bg-[#FFF0F1] border border-[#FFD5D8] rounded-xl shadow px-6 py-3 flex flex-col items-center pb-4 min-h-[180px] justify-center"
      :class="!contact.emergency_number ? 'text-gray-300' : 'text-[#D32F2F]'"
    >
      <div class="flex justify-center items-center gap-2 mb-2">
        <PhoneIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">Emergency</h3>
      </div>
      <p class="text-7xl font-bold mb-1">
        {{ contact.emergency_number || "—" }}
      </p>
      <p
        class="text-sm italic"
        :class="!contact.emergency_desc ? 'text-gray-300' : ''"
      >
        {{ contact.emergency_desc || "No description set yet" }}
      </p>
    </div>

    <!-- Barangay Office -->
    <div
      class="bg-white border border-gray-200 rounded-xl shadow px-6 py-3 min-h-[180px]"
    >
      <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
        <ChatBubbleBottomCenterTextIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">Barangay Office</h3>
      </div>
      <div class="space-y-2">
        <div>
          <span class="font-semibold block text-gray-700">Phone</span>
          <span
            :class="!contact.phone ? 'text-gray-300 italic' : 'text-gray-700'"
          >
            {{ contact.phone || "Not set yet" }}
          </span>
        </div>
        <div>
          <span class="font-semibold block text-gray-700">Email</span>
          <span
            :class="!contact.email ? 'text-gray-300 italic' : 'text-gray-700'"
          >
            {{ contact.email || "Not set yet" }}
          </span>
        </div>
        <div>
          <span class="font-semibold block text-gray-700">Office Hours</span>
          <span
            :class="
              !contact.office_hours ? 'text-gray-300 italic' : 'text-gray-700'
            "
          >
            {{ contact.office_hours || "Not set yet" }}
          </span>
        </div>
      </div>
    </div>

    <!-- Visit Us -->
    <div
      class="bg-white border border-gray-200 rounded-xl shadow px-6 py-3 col-span-1 min-h-[140px]"
    >
      <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
        <HomeIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">Visit Us</h3>
      </div>
      <div>
        <span class="font-semibold block text-gray-700">Address</span>
        <span
          :class="!contact.address ? 'text-gray-300 italic' : 'text-gray-700'"
        >
          {{ contact.address || "Not set yet" }}
        </span>
      </div>
    </div>

    <!-- Technical Support -->
    <div
      class="bg-white border border-gray-200 rounded-xl shadow px-6 py-3 col-span-1 min-h-[140px]"
    >
      <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
        <InformationCircleIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">Technical Support</h3>
      </div>
      <p
        :class="
          !contact.tech_support ? 'text-gray-300 italic' : 'text-gray-700'
        "
      >
        {{ contact.tech_support || "Not set yet" }}
      </p>
    </div>
  </div>
</template>
