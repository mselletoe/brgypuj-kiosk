<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import { CameraIcon } from "@heroicons/vue/24/outline";
import Button from "@/components/shared/Button.vue";

const props = defineProps({
  selectedResident: Object,
  brgyIdNumber: String,
  isSubmitting: Boolean,
});

const emit = defineEmits(["submit", "counting-down"]);
const { t } = useI18n();

const videoRef = ref(null);
const canvasRef = ref(null);
const photoData = ref(null);
const cameraError = ref("");
const countdown = ref(0);
const isCountingDown = ref(false);
let countdownInterval = null;
let mediaStream = null;

// ─── Camera start ─────────────────────────────────────────────────────────
// Simplified: single getUserMedia call directly targeting video0 via V4L2 label.
// Avoids double getUserMedia (permission + real) which was freezing the Pi.
async function startCamera() {
  cameraError.value = "";
  try {
    // Single call — Firefox on Linux already has permission from prior use.
    // Use low resolution to reduce CPU load on Pi (640x480 is plenty for ID photo).
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 15, max: 20 },
      },
      audio: false,
    });

    const video = videoRef.value;
    if (!video) return;

    video.srcObject = mediaStream;
    video.muted = true;
    video.playsInline = true;

    // Play immediately — don't wait for onloadedmetadata on Linux/Firefox
    try {
      await video.play();
    } catch (e) {
      // Retry once after short delay
      await new Promise((r) => setTimeout(r, 500));
      await video.play();
    }

    console.log("Camera started");
  } catch (err) {
    console.error("Camera error:", err);
    cameraError.value =
      err.name === "NotAllowedError"
        ? "Camera access denied. Please allow camera permissions."
        : err.name === "NotFoundError"
          ? "No camera found. Make sure the USB webcam is connected."
          : `Camera error: ${err.message}`;
  }
}

// ─── Camera stop ──────────────────────────────────────────────────────────
function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((t) => t.stop());
    mediaStream = null;
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null;
  }
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
  isCountingDown.value = false;
}

// ─── Countdown ────────────────────────────────────────────────────────────
function startCountdown() {
  if (isCountingDown.value) return;
  isCountingDown.value = true;
  countdown.value = 5;
  emit("counting-down", true);
  countdownInterval = setInterval(() => {
    countdown.value -= 1;
    if (countdown.value === 0) {
      clearInterval(countdownInterval);
      countdownInterval = null;
      isCountingDown.value = false;
      emit("counting-down", false);
      executeCapture();
    }
  }, 1000);
}

// ─── Capture ──────────────────────────────────────────────────────────────
function executeCapture() {
  const video = videoRef.value;
  const canvas = canvasRef.value;
  if (!video || !canvas) return;

  const vw = video.videoWidth;
  const vh = video.videoHeight;

  if (!vw || !vh) {
    setTimeout(executeCapture, 300);
    return;
  }

  const size = Math.min(vw, vh);
  const startX = (vw - size) / 2;
  const startY = (vh - size) / 2;
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, startX, startY, size, size, 0, 0, size, size);
  photoData.value = canvas.toDataURL("image/jpeg", 0.85);
}

function retakePhoto() {
  photoData.value = null;
}

// ─── Submit ───────────────────────────────────────────────────────────────
async function handleSubmit() {
  if (!photoData.value) return;
  stopCamera();
  try {
    await emit("submit", photoData.value);
  } catch {
    photoData.value = null;
    await startCamera();
  }
}

onMounted(startCamera);
onUnmounted(stopCamera);
defineExpose({ stopCamera });
</script>

<template>
  <div
    class="flex w-full h-[340px] gap-20 items-center justify-center animate-fadeIn"
  >
    <!-- Video preview -->
    <div class="flex-shrink-0 h-full relative">
      <div
        class="h-full aspect-square bg-black rounded-3xl overflow-hidden relative flex items-center justify-center"
      >
        <!-- Error state -->
        <div
          v-if="cameraError"
          class="flex flex-col items-center justify-center gap-3 p-6 text-center"
        >
          <span class="text-white text-sm font-medium">{{ cameraError }}</span>
          <button
            @click="startCamera"
            class="mt-2 px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl text-sm font-bold"
          >
            Retry
          </button>
        </div>

        <template v-else>
          <video
            v-show="!photoData"
            ref="videoRef"
            autoplay
            playsinline
            muted
            class="w-full h-full object-cover"
            style="transform: scaleX(-1)"
          ></video>

          <img
            v-show="photoData"
            :src="photoData"
            alt="Captured photo"
            class="w-full h-full object-cover"
            style="transform: scaleX(-1)"
          />

          <canvas ref="canvasRef" class="hidden"></canvas>

          <div
            v-if="!photoData"
            class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none"
          >
            <template v-if="isCountingDown">
              <span
                class="text-[80px] font-black text-white drop-shadow-[0_4px_10px_rgba(0,0,0,0.8)] leading-none"
              >
                {{ countdown }}
              </span>
              <div
                class="bg-black/60 text-white px-5 py-1.5 rounded-full text-sm tracking-widest uppercase font-bold mt-3 animate-pulse backdrop-blur-sm"
              >
                {{ t("lookAtCamera") }}
              </div>
            </template>
            <div
              v-else
              class="absolute bottom-6 bg-black/60 backdrop-blur-md text-white px-4 py-1.5 rounded-full text-xs font-bold tracking-widest uppercase"
            >
              {{ t("alignFace") }}
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Controls -->
    <div class="w-[380px] flex flex-col justify-center h-full flex-shrink-0">
      <div class="flex-1 flex flex-col justify-center">
        <h2 class="text-3xl font-bold text-[#03335C] mb-1">
          {{ t("captureIDPhoto") }}
        </h2>
        <p class="text-gray-500 italic text-sm mb-4">
          {{ t("takeClearPhoto") }}
        </p>
        <div
          class="bg-[#EAF6FB] rounded-2xl p-6 border border-[#BDE0EF] flex flex-col gap-3"
        >
          <div>
            <p
              class="text-[#03335C] text-xs uppercase font-bold tracking-wider opacity-60 mb-1"
            >
              {{ t("applyingFor") }}
            </p>
            <p class="font-black text-[#03335C] text-xl truncate">
              {{ selectedResident?.first_name }}
              {{ selectedResident?.last_name }}
            </p>
          </div>
          <div class="border-t border-[#BDE0EF] pt-3">
            <p
              class="text-[#03335C] text-xs uppercase font-bold tracking-wider opacity-60 mb-1"
            >
              {{ t("barangayIDNo") }}
            </p>
            <p
              v-if="brgyIdNumber"
              class="font-black text-[#03335C] text-xl tracking-widest font-mono"
            >
              {{ brgyIdNumber }}
            </p>
            <p v-else class="text-gray-400 text-sm italic">
              {{ t("generating") }}
            </p>
          </div>
        </div>
      </div>

      <div class="flex gap-3 mt-4">
        <template v-if="!photoData">
          <Button
            :variant="isCountingDown ? 'disabled' : 'primary'"
            size="md"
            class="w-full justify-center text-lg py-4"
            :disabled="isCountingDown || !!cameraError"
            @click="startCountdown"
          >
            <span class="flex items-center justify-center gap-2 w-full">
              <CameraIcon v-if="!isCountingDown" class="w-6 h-6" />
              {{ isCountingDown ? t("getReady") : t("capturePhoto") }}
            </span>
          </Button>
        </template>
        <template v-else>
          <Button
            variant="outline"
            size="md"
            class="w-full justify-center text-lg py-3"
            :disabled="isSubmitting"
            @click="retakePhoto"
          >
            {{ t("retake") }}
          </Button>
          <Button
            :variant="isSubmitting ? 'disabled' : 'secondary'"
            size="md"
            class="w-full justify-center text-lg py-4"
            :disabled="isSubmitting"
            @click="handleSubmit"
          >
            {{ isSubmitting ? t("processing") : t("submit") }}
          </Button>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
