<!-- PendingModal.vue — shown when a pending application already exists -->
<script setup>
import { useI18n } from "vue-i18n";
import Modal from "@/components/shared/Modal.vue";
const emit = defineEmits(["close"]);
const { t } = useI18n();
</script>
<template>
  <Transition name="fade-blur">
    <div
      class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-8 modal-backdrop"
    >
      <Modal
        :title="t('applicationAlreadyPending')"
        :message="t('applicationPendingMsg')"
        :show-reference-id="false"
        :show-primary-button="true"
        :show-secondary-button="false"
        :primary-button-text="t('close')"
        @primary-click="emit('close')"
      />
    </div>
  </Transition>
</template>
<style scoped>
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
