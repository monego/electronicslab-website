<script setup lang="ts">
import { ref, onMounted, onUnmounted, provide, computed } from 'vue';
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

const formattedDate = computed(() => {
  let dateString = format(currentTime.value, "EEEE, d 'de' MMMM 'de' yyyy", { locale: ptBR });

  // Uppercase first letter of the day (e.g., "quarta-feira" -> "Quarta-feira")
  dateString = dateString.charAt(0).toUpperCase() + dateString.slice(1);

  // Uppercase first letter of the month (e.g., "março" -> "Março")
  const firstDeIndex = dateString.indexOf(' de ');
  const secondDeIndex = dateString.indexOf(' de ', firstDeIndex + 4);

  if (firstDeIndex !== -1 && secondDeIndex !== -1) {
    const preMonth = dateString.substring(0, firstDeIndex + 4); // "Quarta-feira, 4 de "
    let monthPart = dateString.substring(firstDeIndex + 4, secondDeIndex); // "março"
    const postMonth = dateString.substring(secondDeIndex); // " de 2026"

    monthPart = monthPart.charAt(0).toUpperCase() + monthPart.slice(1);
    dateString = preMonth + monthPart + postMonth;
  }
  return dateString;
});
</script>

<template>
  <q-layout view="hHh Lpr fFf" class="telao-layout">
    <q-header class="top-bar flex justify-between items-center q-px-xl">
      <div class="date-container text-h4 text-weight-medium col text-left">
        {{ formattedDate }}
      </div>
      <div class="logo-container flex justify-center items-center">
        <img src="logo-claro.png" alt="NUPEDEE" style="height: 5rem; object-fit: contain;">
      </div>
      <div class="clock-container text-h2 text-weight-bold col text-right">
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
