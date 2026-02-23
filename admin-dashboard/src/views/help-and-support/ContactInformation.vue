<script setup>
/**
 * @file ContactInformation.vue
 * @description Admin interface for managing the barangay's contact information,
 * emergency hotlines, and technical support details displayed on the Kiosk.
 */
import { ref } from "vue";
import { useMessage, NInput, NForm, NFormItem, NCard } from "naive-ui";
import {
  PhoneIcon,
  ChatBubbleBottomCenterTextIcon,
  HomeIcon,
  InformationCircleIcon,
} from "@heroicons/vue/24/outline";
import PageTitle from "@/components/shared/PageTitle.vue";

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
 */
const handleSave = async () => {
  isSaving.value = true;
  try {
    // Simulated API Call
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
  <div
    class="flex flex-col p-6 bg-white rounded-md w-full h-full overflow-hidden"
  >
    <div class="flex mb-6 items-center justify-between shrink-0">
      <div>
        <PageTitle title="Contact Information" />
        <p class="text-sm text-gray-500 mt-1">
          Manage the contact details, emergency lines, and support info
          displayed on the Kiosk.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <button
          @click="handleSave"
          :disabled="isSaving"
          class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium text-sm hover:bg-blue-700 transition flex items-center gap-2"
          :class="{ 'opacity-50 cursor-not-allowed': isSaving }"
        >
          <svg
            v-if="!isSaving"
            xmlns="http://www.w3.org/2000/svg"
            class="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
          <svg
            v-else
            class="animate-spin h-5 w-5 text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          {{ isSaving ? "Saving..." : "Save Changes" }}
        </button>
      </div>
    </div>

    <div class="overflow-y-auto flex-1 pr-2 pb-6">
      <n-form :model="contactData" size="large">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="flex flex-col gap-6">
            <n-card
              class="shadow-sm rounded-xl border-t-4 border-t-[#D32F2F] bg-[#FFF0F1]/20"
            >
              <div class="flex items-center gap-2 mb-4 text-[#D32F2F]">
                <PhoneIcon class="w-6 h-6" />
                <h2 class="text-lg font-bold">Emergency Contacts</h2>
              </div>
              <div class="flex flex-col gap-4 xl:flex-row">
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

            <n-card class="shadow-sm rounded-xl border-t-4 border-t-[#013C6D]">
              <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
                <ChatBubbleBottomCenterTextIcon class="w-6 h-6" />
                <h2 class="text-lg font-bold">Barangay Office</h2>
              </div>
              <div class="flex flex-col gap-4">
                <div class="flex flex-col gap-4 xl:flex-row">
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
          </div>

          <div class="flex flex-col gap-6">
            <n-card class="shadow-sm rounded-xl border-t-4 border-t-[#013C6D]">
              <div class="flex items-center gap-2 mb-4 text-[#013C6D]">
                <HomeIcon class="w-6 h-6" />
                <h2 class="text-lg font-bold">Visit Us</h2>
              </div>
              <n-form-item label="Physical Address">
                <n-input
                  v-model:value="contactData.address"
                  type="textarea"
                  placeholder="Complete barangay address"
                  :autosize="{ minRows: 2, maxRows: 4 }"
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
                  :autosize="{ minRows: 3, maxRows: 6 }"
                />
              </n-form-item>
            </n-card>
          </div>
        </div>
      </n-form>
    </div>
  </div>
</template>
