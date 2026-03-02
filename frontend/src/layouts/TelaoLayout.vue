<script setup lang="ts">
import { ref, onMounted, onUnmounted, provide } from 'vue';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

defineOptions({
  name: 'TelaoLayout',
});

const currentTime = ref(new Date());

const updateClock = () => {
  currentTime.value = new Date();
};

let clockInterval: number;

onMounted(() => {
  updateClock();
  clockInterval = window.setInterval(updateClock, 1000);
});

onUnmounted(() => {
  clearInterval(clockInterval);
});

// Provide current time to all nested components
provide('currentTime', currentTime);
</script>

<template>
  <q-layout view="hHh Lpr fFf" class="telao-layout">
    <q-header class="top-bar flex justify-between items-center q-px-xl">
      <div class="date-container text-h4 text-weight-medium">
        {{ format(currentTime, "EEEE, d 'de' MMMM", { locale: ptBR }) }}
      </div>
      <div class="logo-container">
        <div class="text-h3 text-weight-bolder text-primary">NUPEDEE</div>
      </div>
      <div class="clock-container text-h2 text-weight-bold">
        {{ format(currentTime, 'HH:mm:ss') }}
      </div>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<style>
/* Global Telão Styles */
.telao-layout {
  background-color: #0b0e14;
  color: #e6edf3;
  width: 1920px;
  height: 1080px;
  overflow: hidden;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.top-bar {
  height: 100px;
  background: rgba(22, 27, 34, 0.8) !important;
  border-bottom: 2px solid #30363d;
  backdrop-filter: blur(10px);
  color: #e6edf3;
}

body {
  margin: 0;
  padding: 0;
  background-color: #0b0e14;
}

/* Common Scrollbar for all Telão pages */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #484f58;
}
</style>
