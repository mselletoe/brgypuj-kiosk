<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import commentSvg from "@/assets/vectors/Comment.svg?url";
import ArrowBackButton from "@/components/shared/ArrowBackButton.vue";
import Button from "@/components/shared/Button.vue";
import yellowStarSvg from "@/assets/vectors/YellowStar.svg?url";
import Modal from "@/components/shared/Modal.vue";
import { submitFeedback } from "@/api/feedbackService";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const starCount = ref(0);
const ratingText = ref("");
const experienceCategory = ref("general");
const additionalComments = ref("");
const isSubmitting = ref(false);

const isModalVisible = ref(false);

const closeModal = () => {
  isModalVisible.value = false;
  router.push({ path: "feedback" });
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
      return "#CF1331";
    case 2:
      return "#D36F28";
    case 3:
      return "#FFCE0A";
    case 4:
      return "#97B13B";
    case 5:
      return "#21C05C";
    default:
      return "#003a6b";
  }
});

const goBackToRating = () => {
  router.go(-1);
};
</script>

<style scoped>
/* --- LAYOUT CHANGES: Locked screen, no scrollbar, padding for header --- */
.feedback-layout {
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100vh;
  overflow: hidden !important;
  background-color: #ffffff;
  font-family: "Poppins";
  color: #003a6b;
  box-sizing: border-box;
  /* Padding top 110px pushes content below the Global Header */
  padding: 110px 2rem 2rem 2rem;
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Hide scrollbar for Chrome/Safari */
.feedback-layout::-webkit-scrollbar {
  display: none;
}

/* TYPOGRAPHY */
.title-text {
  font-size: 40px;
  font-weight: 700;
  line-height: 50px;
  letter-spacing: -0.03em;
  color: #003a6b;
  margin: 0 0 3px 0;
  text-align: center;
  width: auto;
  max-width: 100%;
}
.subtitle-text {
  font-size: 13px;
  text-align: center;
  margin-bottom: 10px;
  color: #003a6b;
  font-weight: 500;
  max-width: 100%;
}

/* RATING DISPLAY */
.rating-display-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 23px;
  width: 100%;
  flex-wrap: wrap;
}
.new-title-prefix {
  font-size: 13px;
  margin: 0 5px 0 0;
  color: #003a6b;
  font-weight: bold;
  white-space: nowrap;
}
.new-title-text {
  font-size: 13px;
  margin: 0 0 0 5px;
  font-weight: bold;
  max-width: 100%;
}
.yellow-star-icon {
  width: 22px;
  height: 22px;
  margin: 0 1px;
}

/* INPUT & LABELS */
.additional-title-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 816px;
  margin-bottom: 10px;
}
.comment-icon {
  width: 24px;
  height: 24px;
  margin-right: 5px;
}
.additional-title-text {
  font-size: 13px;
  margin: 0;
  text-align: left;
  color: #003a6b;
  font-weight: bold;
}

.comments-input {
  width: 100%;
  max-width: 816px;
  height: 200px;
  background-color: #ffffff;
  border: 2px solid #003a6b;
  border-radius: 10px;
  box-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);
  font-family: "Poppins";
  font-size: 13px;
  font-weight: 400;
  color: #003a6b;
  padding: 15px;
  resize: none;
  outline: none;
  flex-shrink: 0;
  margin-bottom: 30px;
  box-sizing: border-box;
}
.comments-input::placeholder {
  color: #003a6b;
  opacity: 1;
}

/* BUTTONS */
.buttons-container {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 816px;
}
.back-button,
.submit-button {
  height: 40px;
  padding: 0 25px;
  border-radius: 10px;
  box-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);
  font-family: "Poppins";
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background-color 0.2s,
    color 0.2s,
    border-color 0.2s;
}

.back-button {
  background-color: #ffffff;
  border: 1px solid #003a6b;
  color: #003a6b;
}
.back-button:hover {
  background-color: #f0f0f0;
}

.submit-button {
  background-color: #003a6b;
  border: 1px solid #003a6b;
  color: #ffffff;
}
.submit-button:hover {
  background-color: #002a4b;
}

/* MODAL OVERLAY */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
</style>
