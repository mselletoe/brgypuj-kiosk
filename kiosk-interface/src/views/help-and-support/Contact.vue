<script setup>
import { ref, onMounted } from "vue";
import {
  PhoneIcon,
  ChatBubbleBottomCenterTextIcon,
  HomeIcon,
  InformationCircleIcon,
} from "@heroicons/vue/24/outline";
import { useI18n } from "vue-i18n";
import contactService from "@/api/contactService";

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
const { t } = useI18n();

onMounted(async () => {
  try {
    contact.value = await contactService.getKioskContact();
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
    >
      <div class="flex justify-center items-center gap-2 mb-2 text-[#D32F2F]">
        <PhoneIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">{{ t('emergency') }}</h3>
      </div>

      <p
        class="text-7xl font-bold mb-1"
        :class="!contact.emergency_number ? 'text-[#FFF0F1]' : 'text-[#D32F2F]'"
      >
        {{ contact.emergency_number || "—" }}
      </p>

      <p
        class="text-sm"
        :class="
          !contact.emergency_desc ? 'text-gray-400 italic' : 'text-[#D32F2F]'
        "
      >
        {{ contact.emergency_desc || t('notSetYet') }}
      </p>
    </div>

    <!-- Barangay Office -->
    <div
      class="bg-white border border-gray-200 rounded-xl shadow px-6 py-3 min-h-[180px]"
    >
      <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
        <ChatBubbleBottomCenterTextIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">{{ t('barangayOffice') }}</h3>
      </div>
      <div class="space-y-2">
        <div>
          <span class="font-semibold block text-gray-700">{{ t('phone') }}</span>
          <span
            :class="!contact.phone ? 'text-gray-400 italic' : 'text-gray-700'"
          >
            {{ contact.phone || t('notSetYet') }}
          </span>
        </div>
        <div>
          <span class="font-semibold block text-gray-700">{{ t('email') }}</span>
          <span
            :class="!contact.email ? 'text-gray-400 italic' : 'text-gray-700'"
          >
            {{ contact.email || t('notSetYet') }}
          </span>
        </div>
        <div>
          <span class="font-semibold block text-gray-700">{{ t('officeHours') }}</span>
          <span
            :class="
              !contact.office_hours ? 'text-gray-400 italic' : 'text-gray-700'
            "
          >
            {{ contact.office_hours || t('notSetYet') }}
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
        <h3 class="text-xl font-bold">{{ t('visitUs') }}</h3>
      </div>
      <div>
        <span class="font-semibold block text-gray-700">{{ t('address') }}</span>
        <span
          :class="!contact.address ? 'text-gray-400 italic' : 'text-gray-700'"
        >
          {{ contact.address || t('notSetYet') }}
        </span>
      </div>
    </div>

    <!-- Technical Support -->
    <div
      class="bg-white border border-gray-200 rounded-xl shadow px-6 py-3 col-span-1 min-h-[140px]"
    >
      <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
        <InformationCircleIcon class="w-6 h-6" />
        <h3 class="text-xl font-bold">{{ t('technicalSupport') }}</h3>
      </div>
      <p
        :class="
          !contact.tech_support ? 'text-gray-400 italic' : 'text-gray-700'
        "
      >
        {{ contact.tech_support || t('notSetYet') }}
      </p>
    </div>
  </div>
</template>