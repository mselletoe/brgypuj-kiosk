<script setup>
import { useI18n } from "vue-i18n";
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  InformationCircleIcon,
} from "@heroicons/vue/24/outline";
import Button from "@/components/shared/Button.vue";

defineProps({
  selectedResident: Object,
  requirementsChecks: Array,
  isEligible: Boolean,
  isCheckingRequirements: Boolean,
});

const emit = defineEmits(["proceed", "close"]);
const { t } = useI18n();
</script>

<template>
  <Transition name="fade-blur">
    <div
      class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
    >
      <div
        class="bg-white rounded-[28px] p-10 max-w-[560px] w-full shadow-2xl relative"
      >
        <!-- Loading -->
        <div
          v-if="isCheckingRequirements"
          class="flex flex-col items-center py-8 gap-4"
        >
          <div
            class="animate-spin rounded-full h-10 w-10 border-b-2 border-[#03335C]"
          ></div>
          <p class="text-[#03335C] font-medium">
            {{ t("checkingRequirements") }}
          </p>
        </div>

        <template v-else>
          <h2 class="text-2xl font-bold text-[#03335C] mb-1">
            {{ t("applicationRequirements") }}
          </h2>
          <p class="text-gray-500 text-sm mb-6">
            {{ t("requirementsCheckedFor") }}
            <strong
              >{{ selectedResident?.first_name }}
              {{ selectedResident?.last_name }}</strong
            >.
          </p>

          <!-- No requirements configured -->
          <div
            v-if="requirementsChecks.length === 0"
            class="flex items-center gap-3 py-4 px-4 bg-blue-50 rounded-2xl mb-6"
          >
            <InformationCircleIcon
              class="w-6 h-6 text-blue-500 flex-shrink-0"
            />
            <p class="text-sm text-blue-700">
              {{ t("noRequirementsConfigured") }}
            </p>
          </div>

          <!-- Requirements list -->
          <div
            v-else
            class="flex flex-col gap-3 mb-6 max-h-64 overflow-y-auto custom-scroll pr-1"
          >
            <div
              v-for="check in requirementsChecks"
              :key="check.id"
              class="flex items-start gap-3 p-4 rounded-2xl border"
              :class="{
                'bg-green-50 border-green-200': check.passed === true,
                'bg-red-50 border-red-200': check.passed === false,
                'bg-amber-50 border-amber-200':
                  check.passed === null && check.type === 'system_check',
                'bg-blue-50 border-blue-200': check.type === 'document',
              }"
            >
              <div class="flex-shrink-0 mt-0.5">
                <CheckCircleIcon
                  v-if="check.passed === true"
                  class="w-5 h-5 text-green-500"
                />
                <XCircleIcon
                  v-else-if="check.passed === false"
                  class="w-5 h-5 text-red-500"
                />
                <ClockIcon
                  v-else-if="
                    check.passed === null && check.type === 'system_check'
                  "
                  class="w-5 h-5 text-amber-500"
                />
                <InformationCircleIcon v-else class="w-5 h-5 text-blue-500" />
              </div>
              <div class="flex-1 min-w-0">
                <p
                  class="font-bold text-sm"
                  :class="{
                    'text-green-800': check.passed === true,
                    'text-red-800': check.passed === false,
                    'text-amber-800':
                      check.passed === null && check.type === 'system_check',
                    'text-blue-800': check.type === 'document',
                  }"
                >
                  {{ check.label }}
                </p>
                <p
                  class="text-xs mt-0.5"
                  :class="{
                    'text-green-600': check.passed === true,
                    'text-red-600': check.passed === false,
                    'text-amber-600':
                      check.passed === null && check.type === 'system_check',
                    'text-blue-600': check.type === 'document',
                  }"
                >
                  {{ check.message }}
                </p>
              </div>
              <span
                class="flex-shrink-0 text-[10px] font-bold uppercase px-2 py-1 rounded-full"
                :class="{
                  'bg-green-100 text-green-700': check.passed === true,
                  'bg-red-100 text-red-700': check.passed === false,
                  'bg-amber-100 text-amber-700':
                    check.passed === null && check.type === 'system_check',
                  'bg-blue-100 text-blue-700': check.type === 'document',
                }"
              >
                {{
                  check.passed === true
                    ? t("passed")
                    : check.passed === false
                      ? t("failed")
                      : check.type === "document"
                        ? t("bringThis")
                        : t("pending")
                }}
              </span>
            </div>
          </div>

          <!-- Ineligible warning -->
          <div
            v-if="!isEligible"
            class="flex items-start gap-3 p-4 bg-red-50 rounded-2xl border border-red-200 mb-6"
          >
            <XCircleIcon class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <p class="text-sm text-red-700 font-medium">
              {{ t("ineligibleWarning") }}
            </p>
          </div>

          <div class="flex gap-4 mt-2">
            <Button variant="outline" class="flex-1" @click="emit('close')">{{
              t("cancel")
            }}</Button>
            <Button
              v-if="isEligible"
              variant="secondary"
              class="flex-1"
              @click="emit('proceed')"
              >{{ t("proceedToApplication") }}</Button
            >
            <Button v-else variant="disabled" class="flex-1" disabled>{{
              t("cannotProceed")
            }}</Button>
          </div>
        </template>
      </div>
    </div>
  </Transition>
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
.modal-backdrop {
  backdrop-filter: blur(8px);
}
.fade-blur-enter-active,
.fade-blur-leave-active {
  transition:
    opacity 0.5s ease,
    backdrop-filter 0.5s ease;
}
.fade-blur-enter-from,
.fade-blur-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}
.fade-blur-enter-to,
.fade-blur-leave-from {
  opacity: 1;
  backdrop-filter: blur(8px);
}
</style>
