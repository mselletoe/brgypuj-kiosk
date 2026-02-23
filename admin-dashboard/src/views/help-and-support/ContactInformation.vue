<script setup>
/**
 * @file ContactInformation.vue
 * @description Admin interface for managing the barangay's contact information,
 * emergency hotlines, and technical support details displayed on the Kiosk.
 */
import { ref } from "vue";
import { useMessage, NButton, NInput, NForm, NFormItem, NCard } from "naive-ui";
import {
  PhoneIcon,
  ChatBubbleBottomCenterTextIcon,
  HomeIcon,
  InformationCircleIcon,
  CheckCircleIcon,
} from "@heroicons/vue/24/outline";

const message = useMessage();

// Reactive state containing the contact details shown on the Kiosk
const contactData = ref({
  emergency: "911",
  emergencyDesc: "For life-threatening emergencies",
  phone: "(046) 123-4567",
  email: "poblacion1.amadeo@gmail.com",
  officeHours: "Monday to Friday, 8:00 AM - 5:00 PM",
  address: "Brgy. Poblacion I, Amadeo, Cavite",
  techSupport:
    "If you're experiencing issues with the kiosk, please contact our office or visit during business hours for assistance.",
});

const isSaving = ref(false);

/**
 * Handles the form submission to save contact information.
 * Currently mocks an API call delay.
 */
const handleSave = async () => {
  isSaving.value = true;
  try {
    // TODO: Replace with actual backend API call using HTTP client
    await new Promise((resolve) => setTimeout(resolve, 800));
    message.success("Contact information updated successfully.");
  } catch (error) {
    console.error("Save error:", error);
    message.error("Failed to update contact information.");
  } finally {
    isSaving.value = false;
  }
};
</script>

<template>
  <div class="flex flex-col gap-6 p-6 h-full w-full">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Contact Information</h1>
        <p class="text-gray-500 text-sm mt-1">
          Manage the details displayed on the Kiosk's help screen.
        </p>
      </div>
      <n-button
        type="primary"
        size="large"
        :loading="isSaving"
        @click="handleSave"
      >
        <template #icon>
          <CheckCircleIcon class="w-5 h-5" />
        </template>
        Save Changes
      </n-button>
    </div>

    <div class="flex flex-col gap-6 max-w-4xl">
      <n-form :model="contactData" size="large">
        <n-card class="shadow-sm rounded-xl mb-4 border-t-4 border-t-[#D32F2F]">
          <div class="flex items-center gap-2 mb-4 text-[#D32F2F]">
            <PhoneIcon class="w-6 h-6" />
            <h2 class="text-lg font-bold">Emergency Contacts</h2>
          </div>
          <div class="flex flex-col gap-4 sm:flex-row">
            <div class="flex-1">
              <n-form-item label="Emergency Number">
                <n-input
                  v-model:value="contactData.emergency"
                  placeholder="e.g. 911"
                />
              </n-form-item>
            </div>
            <div class="flex-1">
              <n-form-item label="Description">
                <n-input
                  v-model:value="contactData.emergencyDesc"
                  placeholder="e.g. For life-threatening emergencies"
                />
              </n-form-item>
            </div>
          </div>
        </n-card>

        <n-card class="shadow-sm rounded-xl mb-4 border-t-4 border-t-[#013C6D]">
          <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
            <ChatBubbleBottomCenterTextIcon class="w-6 h-6" />
            <h2 class="text-lg font-bold">Barangay Office</h2>
          </div>
          <div class="flex flex-col gap-4">
            <div class="flex flex-col gap-4 sm:flex-row">
              <div class="flex-1">
                <n-form-item label="Phone Number">
                  <n-input
                    v-model:value="contactData.phone"
                    placeholder="Barangay phone number"
                  />
                </n-form-item>
              </div>
              <div class="flex-1">
                <n-form-item label="Email Address">
                  <n-input
                    v-model:value="contactData.email"
                    placeholder="Barangay email"
                  />
                </n-form-item>
              </div>
            </div>
            <n-form-item label="Office Hours">
              <n-input
                v-model:value="contactData.officeHours"
                placeholder="e.g. Monday to Friday, 8:00 AM - 5:00 PM"
              />
            </n-form-item>
          </div>
        </n-card>

        <n-card class="shadow-sm rounded-xl mb-4 border-t-4 border-t-[#013C6D]">
          <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
            <HomeIcon class="w-6 h-6" />
            <h2 class="text-lg font-bold">Visit Us</h2>
          </div>
          <n-form-item label="Physical Address">
            <n-input
              v-model:value="contactData.address"
              type="textarea"
              placeholder="Complete barangay address"
            />
          </n-form-item>
        </n-card>

        <n-card class="shadow-sm rounded-xl border-t-4 border-t-gray-500">
          <div class="flex items-center gap-2 mb-4 text-gray-700">
            <InformationCircleIcon class="w-6 h-6" />
            <h2 class="text-lg font-bold">Technical Support Prompt</h2>
          </div>
          <n-form-item label="Support Description">
            <n-input
              v-model:value="contactData.techSupport"
              type="textarea"
              placeholder="Instructions for kiosk technical issues"
              :autosize="{ minRows: 3 }"
            />
          </n-form-item>
        </n-card>
      </n-form>
    </div>
  </div>
</template>
