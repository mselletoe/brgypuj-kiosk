<script setup>
import { ref, computed, nextTick, onMounted } from "vue";
import { useRouter } from "vue-router";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Button from "@/components/shared/Button.vue";
import Modal from "@/components/shared/Modal.vue";
import { PlusIcon, MinusIcon } from "@heroicons/vue/24/solid";
import Keyboard from "@/components/shared/Keyboard.vue";
import { getAvailableEquipment } from "@/api/equipmentService";
import { useI18n } from 'vue-i18n';

const props = defineProps({
  selectedEquipment: Array,
  goNext: Function,
  hasStartedForm: Function,
});
const emit = defineEmits(["update:selected-equipment"]);
const router = useRouter();
const { t } = useI18n();

const allEquipment = ref([]);
const loading = ref(false);
const loadError = ref(null);
const showExitModal = ref(false);

const fetchEquipment = async () => {
  loading.value = true;
  loadError.value = null;

  try {
    const data = await getAvailableEquipment();

    allEquipment.value = data.map((item) => ({
      id: item.id,
      name: item.name,
      total: item.total_quantity,
      available: item.available_quantity,
      rate: Number(item.rate_per_day),
      ratePer: "day",
    }));
  } catch (err) {
    loadError.value = "Failed to load equipment inventory";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const showKeyboard = ref(false);
const activeEquipment = ref(null);
const quantityWarning = ref("");

const getSelectedItem = (equipment) =>
  props.selectedEquipment.find((item) => item.id === equipment.id);

const getItemQuantity = (equipment) => {
  const item = getSelectedItem(equipment);
  return item ? item.quantity : 0;
};

const formatCurrency = (value) => `₱${parseFloat(value).toLocaleString()}`;

const hasSelection = computed(() => props.selectedEquipment.length > 0);

const setQuantity = (equipment, newQuantity) => {
  if (newQuantity < 0) newQuantity = 0;
  if (newQuantity > equipment.available) {
    newQuantity = equipment.available;
    quantityWarning.value = `Max available: ${equipment.available}`;
  } else {
    quantityWarning.value = "";
  }

  let newSelection = [...props.selectedEquipment];
  const item = getSelectedItem(equipment);

  if (newQuantity > 0) {
    if (item) {
      newSelection.find((i) => i.id === item.id).quantity = newQuantity;
    } else {
      newSelection.push({
        id: equipment.id,
        name: equipment.name,
        rate: equipment.rate,
        ratePer: equipment.ratePer,
        quantity: newQuantity,
      });
    }
  } else if (item) {
    newSelection = newSelection.filter((i) => i.id !== equipment.id);
  }

  emit("update:selected-equipment", newSelection);
};

const increment = (equipment) =>
  setQuantity(equipment, getItemQuantity(equipment) + 1);
const decrement = (equipment) =>
  setQuantity(equipment, getItemQuantity(equipment) - 1);

const openKeyboard = (equipment) => {
  activeEquipment.value = equipment;
  showKeyboard.value = true;
  quantityWarning.value = "";
  nextTick(() => {
    const el = document.getElementById(`item-${equipment.id}`);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  });
};

const handleKeyboardKeyPress = (char) => {
  if (!activeEquipment.value) return;
  const item = activeEquipment.value;
  const newQty =
    parseInt(getItemQuantity(item).toString().replace(/^0/, "") + char, 10) ||
    0;
  setQuantity(item, newQty);
};

const handleKeyboardDelete = () => {
  if (!activeEquipment.value) return;
  const item = activeEquipment.value;
  let qtyStr = getItemQuantity(item).toString().slice(0, -1);
  setQuantity(item, parseInt(qtyStr || "0", 10));
};

const handleKeyboardHide = () => {
  showKeyboard.value = false;
  activeEquipment.value = null;
  quantityWarning.value = "";
};

const resetSelection = () => emit("update:selected-equipment", []);
const continueStep = () => props.goNext("dates");

const handleBackClick = () => {
  if (props.hasStartedForm && props.hasStartedForm()) {
    showExitModal.value = true;
  } else {
    router.push("/home");
  }
};

const confirmExit = () => {
  showExitModal.value = false;
  router.push("/home");
};

const cancelExit = () => {
  showExitModal.value = false;
};

onMounted(() => {
  fetchEquipment();
});
</script>

<template>
  <div
    class="flex flex-col w-full h-full"
    :class="{ 'content-with-keyboard': showKeyboard }"
  >
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="handleBackClick" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          {{ t('equipmentBorrowingTitle') }}
        </h1>
        <p class="text-[#03335C] -mt-2">
          {{ t('belowAvailableEquipment') }}
        </p>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div
        v-if="loading"
        class="flex flex-col justify-center items-center py-20"
      >
        <div class="loader-dots mb-4">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <p class="text-[#03335C] text-lg font-semibold">{{ t('loadingEquipment') }}</p>
      </div>

      <div v-else-if="loadError" class="text-center text-red-500 py-10">
        {{ loadError }}
      </div>

      <div
        v-else-if="allEquipment.length === 0"
        class="flex justify-center items-center py-20"
      >
        <p class="text-gray-400 text-xl font-medium">{{ t('noEquipmentAvailable') }}</p>
      </div>

      <div v-else class="grid grid-cols-4 gap-5">
        <div
          v-for="equipment in allEquipment"
          :key="equipment.id"
          :id="`item-${equipment.id}`"
          class="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 flex flex-col justify-between"
        >
          <div class="text-center">
            <h1 class="text-2xl font-bold text-[#003A6B] truncate">
              {{ equipment.name }}
            </h1>
            <div class="mt-2 text-sm">
              <div class="flex justify-between">
                <span>{{ t('available') }}</span>
                <span class="font-medium"
                  >{{ equipment.available }}/{{ equipment.total }}</span
                >
              </div>
              <div class="flex justify-between mt-1">
                <span>{{ t('rate') }}</span>
                <span class="font-bold text-green-600">
                  {{ formatCurrency(equipment.rate) }}/{{ t('day') }}
                </span>
              </div>
              <p
                v-if="activeEquipment?.id === equipment.id && quantityWarning"
                class="text-red-600 font-medium text-xs mt-1"
              >
                {{ quantityWarning }}
              </p>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between">
            <button
              @click="decrement(equipment)"
              :class="[
                'w-10 h-10 flex items-center justify-center rounded-lg transition-colors',
                getItemQuantity(equipment) === 0
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-red-100 text-red-600 hover:bg-red-200',
              ]"
              :disabled="getItemQuantity(equipment) === 0"
            >
              <MinusIcon class="w-6 h-6" />
            </button>

            <span
              class="text-2xl font-bold w-12 text-center cursor-pointer hover:bg-gray-100 rounded-md"
              @click="openKeyboard(equipment)"
            >
              {{ getItemQuantity(equipment) }}
            </span>

            <button
              @click="increment(equipment)"
              :class="[
                'w-10 h-10 flex items-center justify-center rounded-lg transition-colors',
                getItemQuantity(equipment) === equipment.available
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-green-100 text-green-600 hover:bg-green-200',
              ]"
              :disabled="getItemQuantity(equipment) === equipment.available"
            >
              <PlusIcon class="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0"
    >
      <Button
        :variant="hasSelection ? 'outline' : 'disabled'"
        size="md"
        :disabled="!hasSelection"
        @click="resetSelection"
      >
        {{ t('resetSelection') }}
      </Button>
      <Button
        :variant="hasSelection ? 'secondary' : 'disabled'"
        size="md"
        :disabled="!hasSelection"
        @click="continueStep"
      >
        {{ t('continueToDates') }}
      </Button>
    </div>

    <Transition name="slide-up">
      <Keyboard
        v-if="showKeyboard"
        @key-press="handleKeyboardKeyPress"
        @delete="handleKeyboardDelete"
        @enter="handleKeyboardHide"
        @hide-keyboard="handleKeyboardHide"
        active-input-type="tel"
        class="fixed bottom-0 w-full"
      />
    </Transition>

    <Transition name="fade-blur">
      <div
        v-if="showExitModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
      >
        <Modal
          :title="t('exitEquipmentRequest')"
          :message="t('unsavedChanges')"
          type="warning"
          :primaryButtonText="t('exit')"
          :secondaryButtonText="t('stay')"
          :showPrimaryButton="true"
          :showSecondaryButton="true"
          :showReferenceId="false"
          @primary-click="confirmExit"
          @secondary-click="cancelExit"
        />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.content-with-keyboard {
  padding-bottom: 210px;
  transition: padding-bottom 0.3s ease-out;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

.modal-backdrop {
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}
.fade-blur-enter-active,
.fade-blur-leave-active {
  transition:
    opacity 0.5s ease,
    -webkit-backdrop-filter 0.5s ease,
    backdrop-filter 0.5s ease;
}
.fade-blur-enter-from,
.fade-blur-leave-to {
  opacity: 0;
  -webkit-backdrop-filter: blur(0px);
  backdrop-filter: blur(0px);
}
.fade-blur-enter-to,
.fade-blur-leave-from {
  opacity: 1;
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}

/* Loader Dots CSS */
.loader-dots {
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 60px;
  height: 15px;
}

.dot {
  width: 12px;
  height: 12px;
  background-color: #03335c;
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes pulse {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>