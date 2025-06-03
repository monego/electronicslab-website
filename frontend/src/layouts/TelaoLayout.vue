<script setup lang="ts">
defineOptions({
  name: 'TelaoLayout',
});

import { format, minutesToMilliseconds } from 'date-fns';
import { pt } from 'date-fns/locale';
import { ref, onMounted } from 'vue';

const currentTime = ref(new Date());
const formattedTime = ref('');

function getAndFormatTime() {
  currentTime.value = new Date();
  formattedTime.value = format(currentTime.value, 'HH:mm EEEE yyyy-MM-dd', { locale: pt });
}

onMounted(() => {
  getAndFormatTime();
  const now = new Date();
  const nextMinute = new Date(now.getTime() + (60 - now.getSeconds()) * 1000);
  const delay = nextMinute.getTime() - now.getTime();
  setTimeout(() => {
    getAndFormatTime();
    setInterval(() => {
      getAndFormatTime();
    }, minutesToMilliseconds(1));
  }, delay);
});
</script>

<template>
<q-layout view="lHh Lpr lFf">
  <q-page-container>
    <div class="row" style="justify-content: center;">
      <div class="col-auto">
        <q-chip color="#e7e393" dense dark square outline size="60px">
          {{ formattedTime }}
        </q-chip>
      </div>
    </div>
    <router-view />
  </q-page-container>
</q-layout>
</template>

<style>
body {
  background: #38302e;
}
</style>
