<script setup lang="ts">
defineOptions({
  name: 'MainLayout',
});

import { ref } from 'vue';
import { useRoute, RouteLocationNormalized } from 'vue-router';

const route = useRoute() as RouteLocationNormalized;

const links = ref([
  { label: 'Laboratórios', to: '/laboratorios' },
  { label: 'Calendário', to: '/calendario' },
  { label: 'Equipamentos', to: '/materiais' },
  { label: 'Sobre', to: '/sobre' },
]);
</script>

<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
          <q-avatar square>
            <img src="/Icone.ico">
          </q-avatar>
        <q-space />
        <q-btn
        v-for="link in links"
        :key="link.label"
        flat
        rounded
        :to="link.to"
        :label="link.label"
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
