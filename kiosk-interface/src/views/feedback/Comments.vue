<script setup>
import { ref, onMounted, computed, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import commentSvg from "@/assets/vectors/Comment.svg?url";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Button from "@/components/shared/Button.vue";
import yellowStarSvg from "@/assets/vectors/YellowStar.svg?url";
import Modal from "@/components/shared/Modal.vue";
import Keyboard from "@/components/shared/Keyboard.vue";
import { submitFeedback } from "@/api/feedbackService";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { t } = useI18n();
const starCount = ref(0);
const ratingText = ref("");
const experienceCategory = ref("general");
const additionalComments = ref("");
const isSubmitting = ref(false);

const isModalVisible = ref(false);
const showKeyboard = ref(false);

const closeModal = () => {
  isModalVisible.value = false;
  router.push({ path: "/home" });
};

const handleNewRating = () => {
  isModalVisible.value = false;
  router.push({ path: "/feedback" });
};

onMounted(() => {
  if (route.query.stars) {
    starCount.value = Number(route.query.stars);
  }
  if (route.query.ratingText) {
    ratingText.value = route.query.ratingText;
  }
  if (route.query.category) {
    experienceCategory.value = route.query.category;
  }
});

const ratingTextColor = computed(() => {
  switch (starCount.value) {
    case 1:
      return "#E74C3C";
    case 2:
      return "#F16C14";
    case 3:
      return "#E69500";
    case 4:
      return "#13B3A1";
    case 5:
      return "#2C67E7";
    default:
      return "#003a6b";
  }
});

const goBackToRating = () => {
  router.push({
    path: "/rating",
    query: { category: experienceCategory.value },
  });
};

const handleCancel = () => {
  router.push({ path: "/feedback" });
};

const handleSubmit = async () => {
  if (isSubmitting.value) return;

  isSubmitting.value = true;

  try {
    const residentId = authStore.residentId;

    const payload = {
      resident_id: residentId,
      category: experienceCategory.value,
      rating: starCount.value,
      additional_comments: additionalComments.value || null,
    };

    await submitFeedback(payload);

    showKeyboard.value = false; 
    isModalVisible.value = true;
  } catch (error) {
    console.error("Failed to submit feedback:", error);
    alert("Failed to submit feedback. Please try again.");
  } finally {
    isSubmitting.value = false;
  }
};

const focusInput = () => {
  showKeyboard.value = true;
  nextTick(() => {
    const el = document.getElementById("comments-textarea");
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
};

const handleKeyboardKeyPress = (char) => {
  additionalComments.value += char;
};

const handleKeyboardDelete = () => {
  additionalComments.value = additionalComments.value.slice(0, -1);
};

const handleKeyboardEnter = () => {
  showKeyboard.value = false;
};

const handleKeyboardHide = () => {
  showKeyboard.value = false;
};
</script>

<template>
  <div
    class="flex flex-col w-full h-full"
    :class="{ 'content-with-keyboard': showKeyboard }"
  >
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBackToRating" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">{{ t('shareYourThoughts') }}</h1>
        <p class="text-[#03335C] -mt-2">{{ t('tellUsMore') }}</p>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div
        class="flex flex-wrap items-center justify-center w-full mb-[23px] text-xl"
      >
        <h2 class="font-bold mr-[5px] whitespace-nowrap">{{ t('yourRating') }}</h2>

        <template v-for="n in Number(starCount)" :key="n">
          <img
            :src="yellowStarSvg"
            alt="Yellow Star"
            class="w-[22px] h-[22px] mx-[1px]"
          />
        </template>

        <h2 class="font-bold ml-[5px]" :style="{ color: ratingTextColor }">
          {{ ratingText }}
        </h2>
      </div>

      <div class="flex items-center w-full mb-2">
        <img :src="commentSvg" alt="Comment Icon" class="w-6 h-6 mr-[5px]" />
        <h3 class="text-[13px] font-bold text-left text-[#003a6b]">{{ t('additionalComments') }}</h3>
      </div>

      <textarea
        id="comments-textarea"
        v-model="additionalComments"
        @focus="focusInput"
        class="w-full h-[200px] p-[15px] bg-white text-[13px] text-[#003a6b] border-2 border-[#003a6b] rounded-[10px] shadow-[3px_3px_6px_rgba(0,0,0,0.2)] resize-none outline-none box-border placeholder:text-[#003a6b]"
        :placeholder="t('commentsPlaceholder')"
      ></textarea>
    </div>

    <div
      class="flex gap-6 mt-6 justify-between items-center bottom-0 flex-shrink-0"
    >
      <Button variant="outline" @click="handleCancel" :disabled="isSubmitting">
        {{ t('cancel') }}
      </Button>
      <Button
        variant="secondary"
        @click="handleSubmit"
        :disabled="isSubmitting"
      >
        {{ isSubmitting ? t('submitting') : t('submit') }}
      </Button>
    </div>

    <Transition name="slide-up">
      <Keyboard
        v-if="showKeyboard"
        @key-press="handleKeyboardKeyPress"
        @delete="handleKeyboardDelete"
        @enter="handleKeyboardEnter"
        @hide-keyboard="handleKeyboardHide"
        active-input-type="text"
        class="fixed bottom-0 w-full z-40"
      />
    </Transition>

    <Transition name="fade-blur">
      <div
        v-if="isModalVisible"
        class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/40 p-8 modal-backdrop"
      >
        <Modal
          :title="t('feedbackSubmitted')"
          :message="t('thankYouFeedback')"
          :showSecondaryButton="true"
          :primaryButtonText="t('done')"
          :secondaryButtonText="t('newRating')"
          @primary-click="closeModal"
          @secondary-click="handleNewRating"
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