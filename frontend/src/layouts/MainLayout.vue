<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import type { RouteLocationNormalized } from 'vue-router';

defineOptions({
  name: 'MainLayout',
});

const route = useRoute() as RouteLocationNormalized;

const links = ref([
  { icon: 'mdi-calendar-clock', label: 'Calendário', to: '/calendario' },
  { icon: 'mdi-tools', label: 'Equipamentos', to: '/materiais' },
  { icon: 'mdi-login', label: 'Entrar', to: '/login' },
]);
</script>

<template>
  <q-layout view="lHh Lpr lFf" class="main-layout">
    <q-header class="main-header">
      <q-toolbar class="q-px-xl container">
        <q-item to="/" clickable flat class="brand-item q-pa-none">
          <q-avatar square size="40px">
            <img src="/Icone.png">
          </q-avatar>
          <div class="brand-text q-ml-md text-h5 text-weight-bolder text-uppercase tracking-tighter">
            NUPEDEE
          </div>
        </q-item>

        <q-space />

        <div class="nav-links flex items-center q-gutter-x-md">
          <q-btn
            v-for="link in links"
            :key="link.label"
            flat
            no-caps
            rounded
            :to="link.to"
            :class="{ 'active-link': route.path === link.to }"
            class="nav-btn"
          >
            <q-icon :name="link.icon" size="20px" class="q-mr-sm" />
            <span class="text-weight-bold">{{ link.label }}</span>
            <div class="active-indicator" v-if="route.path === link.to"></div>
          </q-btn>
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view v-slot="{ Component }">
        <transition
          appear
          enter-active-class="animated fadeIn"
          leave-active-class="animated fadeOut"
          mode="out-in"
        >
          <component :is="Component" />
        </transition>
      </router-view>
    </q-page-container>
  </q-layout>
</template>

<style lang="scss" scoped>
.main-layout {
  background-color: #fcfcfd;
}

.main-header {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  height: 80px;
  display: flex;
  align-items: center;
}

.brand-text {
  color: var(--q-primary);
  letter-spacing: -0.02em;
}

.nav-btn {
  color: #64748b;
  padding: 8px 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;

  &:hover {
    color: var(--q-primary);
    background: rgba(59, 130, 246, 0.05);
  }

  &.active-link {
    color: var(--q-primary);
    background: rgba(59, 130, 246, 0.08);
  }
}

.active-indicator {
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background: var(--q-primary);
  border-radius: 2px 2px 0 0;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(2px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Page Transitions */
.fadeIn {
  animation: fadeIn 0.4s ease forwards;
}

.fadeOut {
  animation: fadeOut 0.4s ease forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}
</style>
