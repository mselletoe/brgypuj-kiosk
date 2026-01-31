<template>
  <div class="loader-dots">
    <div class="dot"></div>
    <div class="dot"></div>
    <div class="dot"></div>
  </div>
</template>

<script>
export default {
  name: 'LoadingDots',
  // Props are not strictly necessary here, but keep them for flexibility
  props: {
    color: { type: String, default: '#003A6B' }, // Dark Blue
    size: { type: String, default: '10px' },
    spacing: { type: String, default: '40px' } // Increased width for better visibility
  }
};
</script>

<style scoped>
.loader-dots {
    display: flex;
    justify-content: space-around;
    align-items: center;
    width: v-bind(spacing); /* Use v-bind for dynamic width */
    height: 15px; 
}

.dot {
    width: v-bind(size); /* Use v-bind for dynamic size */
    height: v-bind(size);
    background-color: v-bind(color); /* Use v-bind for dynamic color */
    border-radius: 50%;
    animation: pulse 1.4s infinite ease-in-out both;
}

/* Staggered animation start */
.dot:nth-child(1) {
    animation-delay: -0.32s;
}

.dot:nth-child(2) {
    animation-delay: -0.16s;
}

@keyframes pulse {
    0%, 80%, 100% { 
        transform: scale(0); 
        opacity: 0.3; /* Subtle transparency */
    }
    40% { 
        transform: scale(1); 
        opacity: 1;
    }
}
</style>