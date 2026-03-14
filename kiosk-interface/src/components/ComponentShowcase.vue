<script setup>
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import Keyboard from '@/components/shared/Keyboard.vue'
import Keypad from '@/components/shared/Keypad.vue'
import Loading from '@/components/shared/Loading.vue'
import Modal from '@/components/shared/Modal.vue'
import Button from '@/components/shared/Button.vue'
import ServiceTitle from '@/components/shared/ServiceTitle.vue'
import Header from '@/layouts/Header.vue'
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Page Title -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-[#013C6D] mb-4">Component Documentation</h1>
        <p class="text-lg text-[#1B5886]">Visual reference for all components</p>
      </div>

      <!-- Components Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <!-- ArrowBackButton -->
        <div class="bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Arrow Back Button</h2>
            <p class="text-sm text-gray-600">Navigation back button with customizable colors</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <ArrowBackButton />
          </div>
        </div>

        <!-- Keypad -->
        <div class="bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Keypad</h2>
            <p class="text-sm text-gray-600">Numeric keypad for PIN/number entry</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <Keypad />
          </div>
        </div>

        <!-- Loading -->
        <div class="bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Loading</h2>
            <p class="text-sm text-gray-600">Animated loading dots indicator</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <Loading />
          </div>
        </div>

        <!-- ServiceTitle -->
        <div class="bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Service Title</h2>
            <p class="text-sm text-gray-600">Page title with optional subtitle</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <ServiceTitle title="Service Title" subtitle="This is a subtitle" />
          </div>
        </div>

        <!-- PrimaryButton (Full Width) -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">PrimaryButton</h2>
            <p class="text-sm text-gray-600">Button component with multiple variants and sizes</p>
          </div>
          <div class="flex flex-col items-center justify-center gap-6 min-h-[200px] bg-gray-50 rounded-xl p-6">
            <!-- Variants -->
            <div class="flex flex-wrap items-center justify-center gap-3">
              <Button variant="primary">Primary Button</Button>
              <Button variant="secondary">Secondary Button</Button>
              <Button variant="outline">Outline Button</Button>
              <Button variant="disabled">Disabled Button</Button>
            </div>
            
            <!-- Sizes -->
            <div class="flex flex-wrap items-center justify-center gap-3">
              <Button variant="primary" size="sm">Small</Button>
              <Button variant="primary" size="md">Medium</Button>
              <Button variant="primary" size="lg">Large</Button>
            </div>
          </div>
        </div>

        <!-- Keyboard (Full Width) -->
        <!-- <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Keyboard</h2>
            <p class="text-sm text-gray-600">Virtual keyboard with multiple layouts</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <Keyboard />
          </div>
        </div> -->

        <!-- Modal (Full Width) -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Modal</h2>
            <p class="text-sm text-gray-600">Success modal with action buttons</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <Modal />
          </div>
        </div>

        <!-- Header (Full Width) -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6 border-2 border-gray-200">
          <div class="mb-4 border-b border-gray-200 pb-3">
            <h2 class="text-2xl font-bold text-[#013C6D] mb-1">Header</h2>
            <p class="text-sm text-gray-600">Application header with logo, time, and user info</p>
          </div>
          <div class="flex items-center justify-center min-h-[200px] bg-gray-50 rounded-xl p-6">
            <Header />
          </div>
        </div>

      </div>

      <!-- Instructions -->
      <div class="mt-12 bg-white rounded-2xl shadow-lg p-8 border-2 border-[#1B5886]">
        <h2 class="text-3xl font-bold text-[#013C6D] mb-4">How to Add New Components</h2>
        <ol class="space-y-3 text-gray-700 list-decimal list-inside">
          <li>Import your component at the top: <code class="bg-gray-100 px-2 py-1 rounded">import YourComponent from '@/components/YourComponent.vue'</code></li>
          <li>Copy one of the card divs and paste it in the grid</li>
          <li>Update the title, description, and replace the component tag</li>
          <li>Add <code class="bg-gray-100 px-2 py-1 rounded">lg:col-span-2</code> class if you want it full-width</li>
        </ol>
      </div>
    </div>
  </div>
</template>