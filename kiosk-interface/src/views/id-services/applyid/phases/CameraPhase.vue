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

// ─── Refs ─────────────────────────────────────────────────────────────────
const videoRef = ref(null);
const canvasRef = ref(null);
const photoData = ref(null);
const cameraError = ref("");

const countdown = ref(0);
const isCountingDown = ref(false);
let countdownInterval = null;
let mediaStream = null;

// ─── Camera: start ────────────────────────────────────────────────────────
// Enumerates all video input devices and picks the first real capture device.
// USB webcams on Linux register two entries: the real capture device and a
// metadata/control-only device. We skip the metadata one and fall back if
// the chosen device produces no frames after 1 second.
async function startCamera() {
  cameraError.value = "";
  try {
    // Step 1: trigger permission prompt so labels are populated
    const permStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: false,
    });
    permStream.getTracks().forEach((t) => t.stop());

    // Step 2: enumerate and pick the real capture device
    // "HDR webcam (V4L2)" = /dev/video0 = real ✅
    // "HDR webcam"        = /dev/video1 = metadata only ❌
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter((d) => d.kind === "videoinput");
    console.log(
      "Available cameras:",
      videoDevices.map((d) => `${d.label} [${d.deviceId}]`),
    );

    const v4l2Device =
      videoDevices.find((d) => d.label.includes("(V4L2)")) ||
      videoDevices.find((d) => d.label.toLowerCase().includes("v4l2")) ||
      [...videoDevices].sort((a, b) => b.label.length - a.label.length)[0] ||
      videoDevices[0];

    const chosenDeviceId = v4l2Device?.deviceId ?? null;
    console.log("Chosen camera:", v4l2Device?.label, chosenDeviceId);

    // Step 3: get the stream
    const constraints = {
      video: chosenDeviceId
        ? {
            deviceId: { exact: chosenDeviceId },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          }
        : { width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false,
    };
    mediaStream = await navigator.mediaDevices.getUserMedia(constraints);

    // Step 4: attach stream and force play — do NOT await onloadedmetadata
    // because on Linux/Firefox it can fire late or not at all before play()
    const video = videoRef.value;
    if (!video) return;

    video.srcObject = mediaStream;
    video.muted = true;
    video.playsInline = true;

    // Try to play immediately, retry up to 5 times if it fails
    let played = false;
    for (let i = 0; i < 5; i++) {
      try {
        await video.play();
        played = true;
        console.log("Camera playing on attempt", i + 1);
        break;
      } catch (playErr) {
        console.warn(`Play attempt ${i + 1} failed:`, playErr.message);
        await new Promise((r) => setTimeout(r, 300));
      }
    }

    if (!played) {
      cameraError.value = "Could not start camera playback. Please try again.";
      return;
    }

    // Step 5: poll for actual frames (videoWidth > 0 means frames are flowing)
    let attempts = 0;
    while (video.videoWidth === 0 && attempts < 30) {
      await new Promise((r) => setTimeout(r, 200));
      attempts++;
    }

    if (video.videoWidth === 0) {
      console.warn("No frames after 6s — stream may be wrong device");
      cameraError.value =
        "Camera connected but not producing frames. Please replug the webcam.";
    } else {
      console.log(`Camera ready: ${video.videoWidth}x${video.videoHeight}`);
    }
  } catch (err) {
    console.error("Camera error:", err);
    cameraError.value =
      err.name === "NotAllowedError"
        ? "Camera access was denied. Please allow camera permissions."
        : err.name === "NotFoundError"
          ? "No camera found. Make sure the USB webcam is connected."
          : `Camera error: ${err.message}`;
  }
}

// ─── Camera: stop ─────────────────────────────────────────────────────────
function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
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

// ─── Countdown → capture ──────────────────────────────────────────────────
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
// Key fix: draw the RAW (non-mirrored) frame onto the canvas.
// The <video> is CSS-mirrored for a natural preview, but the saved image
// must NOT be mirrored — we draw it straight.
function executeCapture() {
  const video = videoRef.value;
  const canvas = canvasRef.value;
  if (!video || !canvas) return;

  const vw = video.videoWidth;
  const vh = video.videoHeight;

  if (!vw || !vh) {
    // Stream not ready — try once more after a short delay
    setTimeout(executeCapture, 200);
    return;
  }

  // Square crop from the center
  const size = Math.min(vw, vh);
  const startX = (vw - size) / 2;
  const startY = (vh - size) / 2;

  canvas.width = size;
  canvas.height = size;

  const ctx = canvas.getContext("2d");
  // Draw straight (not mirrored) — the canvas save is the real image
  ctx.drawImage(video, startX, startY, size, size, 0, 0, size, size);

  photoData.value = canvas.toDataURL("image/jpeg", 0.92);
}

// ─── Retake ───────────────────────────────────────────────────────────────
function retakePhoto() {
  photoData.value = null;
  // Camera stream is still running — no need to restart
}

// ─── Submit ───────────────────────────────────────────────────────────────
async function handleSubmit() {
  if (!photoData.value) return;
  stopCamera();
  try {
    await emit("submit", photoData.value);
  } catch {
    // Parent failed — restart camera so user can retake
    photoData.value = null;
    await startCamera();
  }
}

// ─── Lifecycle ────────────────────────────────────────────────────────────
onMounted(startCamera);
onUnmounted(stopCamera);

// Expose stopCamera so parent (ApplyID) can stop it on back-navigation
defineExpose({ stopCamera });
</script>

<template>
  <div
    class="flex w-full h-[340px] gap-20 items-center justify-center animate-fadeIn"
  >
    <!-- Video / Photo preview -->
    <div class="flex-shrink-0 h-full relative">
      <div
        class="h-full aspect-square bg-black rounded-3xl overflow-hidden relative flex items-center justify-center"
      >
        <!-- Camera error state -->
        <div
          v-if="cameraError"
          class="flex flex-col items-center justify-center gap-3 p-6 text-center"
        >
          <span class="text-white text-sm font-medium">{{ cameraError }}</span>
          <button
            @click="startCamera"
            class="mt-2 px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl text-sm font-bold transition-colors"
          >
            Retry
          </button>
        </div>

        <template v-else>
          <!-- Live video — CSS mirror for natural selfie preview only -->
          <video
            v-show="!photoData"
            ref="videoRef"
            autoplay
            playsinline
            muted
            class="w-full h-full object-cover"
            style="transform: scaleX(-1)"
          ></video>

          <!-- Captured photo — also mirrored to match what user saw -->
          <img
            v-show="photoData"
            :src="photoData"
            alt="Captured ID photo"
            class="w-full h-full object-cover"
            style="transform: scaleX(-1)"
          />

          <!-- Hidden canvas for capture (no CSS transform — real pixels) -->
          <canvas ref="canvasRef" class="hidden"></canvas>

          <!-- Overlay: countdown / align hint -->
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

    <!-- Controls panel -->
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
        <!-- No photo yet -->
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

        <!-- Photo captured -->
        <template v-else>
          <Button
            variant="outline"
            size="md"
            class="w-full justify-center text-lg py-3"
            :disabled="isSubmitting"
            @click="retakePhoto"
            >{{ t("retake") }}</Button
          >

          <Button
            :variant="isSubmitting ? 'disabled' : 'secondary'"
            size="md"
            class="w-full justify-center text-lg py-4"
            :disabled="isSubmitting"
            @click="handleSubmit"
            >{{ isSubmitting ? t("processing") : t("submit") }}</Button
          >
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
