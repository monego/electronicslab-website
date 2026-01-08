<script setup lang="ts">
defineOptions({
  name: 'MainLayout',
});

import { ref } from 'vue';
import { useRoute } from 'vue-router';
import type { RouteLocationNormalized } from 'vue-router';

const route = useRoute() as RouteLocationNormalized;

const links = ref([
  { icon: 'mdi-calendar-clock', label: 'Calendário', to: '/calendario' },
  { icon: 'mdi-tools', label: 'Equipamentos', to: '/materiais' },
  { icon: 'mdi-login', label: 'Entrar', to: '/login' },
]);
</script>

<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-item to="/">
          <q-avatar square>
            <img src="/Icone.png">
          </q-avatar>
        </q-item>
        <q-space />
        <q-btn v-for="link in links" :key="link.label" flat rounded :to="link.to"
        :label="link.label" :icon="link.icon"
        :class="{ 'active-link': route.path === link.to }" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<style lang="scss" scoped>
.q-toolbar {
  background-color: #212121;
}

.q-btn {
  color: #64B5F6;
  padding: 8px 16px;
}

.q-btn:hover {
  background-color: #1976D2;
  color: white;
}

.q-btn.active-link {
  background-color: #BBDEFB;
  color: #212121;
}
</style>
