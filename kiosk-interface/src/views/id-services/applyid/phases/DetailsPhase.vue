<script setup>
import { useI18n } from "vue-i18n";
import { useAuthStore } from "@/stores/auth";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import { DocumentTextIcon } from "@heroicons/vue/24/outline";

const props = defineProps({
  idFields: Array,
  detailsForm: Object,
  detailsErrors: Object,
  useManualEntry: Boolean,
  isFetchingAutofill: Boolean,
  isSubmitting: Boolean,
  autofillMap: Object,
});

const emit = defineEmits(["update:detailsForm", "update:useManualEntry"]);

const { t } = useI18n();
const authStore = useAuthStore();

function updateField(fieldName, value) {
  emit("update:detailsForm", { ...props.detailsForm, [fieldName]: value });
}
</script>

<template>
  <div
    class="flex w-full h-full items-start justify-start animate-fadeIn overflow-hidden"
  >
    <div class="w-full h-full flex flex-col px-2">
      <h2
        class="text-2xl font-bold text-[#03335C] flex items-center gap-2 mb-1 flex-shrink-0"
      >
        <DocumentTextIcon class="w-8 h-8" />{{ t("idCardDetails") }}
      </h2>
      <p class="text-gray-500 italic text-xs mb-6 text-left flex-shrink-0">
        {{ t("reviewIDInfo") }}
      </p>

      <div class="flex-1 overflow-y-auto pr-1 min-h-0 custom-scroll px-1 pt-1">
        <!-- Loading autofill -->
        <div
          v-if="isFetchingAutofill"
          class="flex items-center gap-3 py-6 text-[#03335C]"
        >
          <div
            class="animate-spin rounded-full h-5 w-5 border-b-2 border-[#03335C]"
          ></div>
          <span class="text-sm font-medium">{{
            t("loadingResidentData")
          }}</span>
        </div>

        <template v-else>
          <!-- Manual override toggle (RFID users only) -->
          <div v-if="authStore.rfidUid" class="mb-5 flex items-center gap-3">
            <input
              id="manualEntry"
              type="checkbox"
              :checked="useManualEntry"
              @change="emit('update:useManualEntry', $event.target.checked)"
              class="h-5 w-5 text-[#013C6D]"
            />
            <label
              for="manualEntry"
              class="text-sm text-gray-700 italic cursor-pointer select-none"
            >
              {{ t("enterManually") }}
            </label>
          </div>

          <div
            v-if="idFields.length === 0"
            class="text-sm text-gray-400 italic py-4"
          >
            {{ t("noFieldsConfigured") }}
          </div>

          <div v-else class="grid grid-cols-2 gap-x-6 gap-y-4 pb-2">
            <div
              v-for="field in idFields"
              :key="field.id || field.name"
              :class="field.type === 'textarea' ? 'col-span-2' : 'col-span-1'"
              class="flex flex-col"
            >
              <label class="block text-base font-bold text-[#003A6B] mb-2">
                {{ field.label }}
                <span v-if="field.required" class="text-red-600">*</span>
              </label>

              <textarea
                v-if="field.type === 'textarea'"
                :value="detailsForm[field.name]"
                @input="updateField(field.name, $event.target.value)"
                :disabled="!useManualEntry && !!autofillMap[field.name]"
                :placeholder="field.label"
                class="w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D] disabled:bg-gray-50 disabled:text-gray-400 resize-none"
                rows="2"
              ></textarea>

              <VueDatePicker
                v-else-if="field.type === 'date'"
                :model-value="detailsForm[field.name]"
                @update:model-value="updateField(field.name, $event)"
                :enable-time-picker="false"
                :disabled="
                  (!useManualEntry && !!autofillMap[field.name]) || isSubmitting
                "
                auto-apply
                teleport-center
                format="MM/dd/yyyy"
                :max-date="new Date()"
                :placeholder="field.label"
                :ui="{ input: 'dp-match-input' }"
              />

              <input
                v-else
                :value="detailsForm[field.name]"
                @input="updateField(field.name, $event.target.value)"
                :disabled="!useManualEntry && !!autofillMap[field.name]"
                :type="field.type === 'number' ? 'number' : 'text'"
                :placeholder="field.label"
                class="w-full h-[48px] px-4 py-3 border border-gray-300 rounded-xl shadow-sm transition-shadow focus:outline-none focus:ring-2 focus:ring-[#013C6D] disabled:bg-gray-50 disabled:text-gray-400"
              />

              <p
                v-if="detailsErrors[field.name]"
                class="text-red-500 text-xs italic mt-1"
              >
                {{ detailsErrors[field.name] }}
              </p>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar {
  width: 6px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background-color: #bde0ef;
  border-radius: 20px;
}
.animate-fadeIn {
  animation: fadeIn 0.4s ease-out forwards;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>

<style>
.dp-match-input.dp__input {
  height: 48px !important;
  border-radius: 0.75rem !important;
  border: 1px solid #d1d5db !important;
  padding: 0.75rem 1rem 0.75rem 2.5rem !important;
  font-size: 1rem !important;
  color: #111827 !important;
  background-color: #ffffff !important;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05) !important;
  line-height: normal !important;
}
.dp-match-input.dp__input:focus {
  border-color: #013c6d !important;
  box-shadow: 0 0 0 2px #013c6d !important;
}
.dp-match-input.dp__input_readonly,
.dp-match-input.dp__input:disabled {
  background-color: #f3f4f6 !important;
  color: #374151 !important;
  cursor: not-allowed !important;
}
</style>
