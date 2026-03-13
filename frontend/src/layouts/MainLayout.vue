<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import type { RouteLocationNormalized } from 'vue-router';

defineOptions({
  name: 'MainLayout',
});

const route = useRoute() as RouteLocationNormalized;
const leftDrawerOpen = ref(false);

const links = ref([
  { icon: 'mdi-calendar-clock', label: 'Calendário', to: '/calendario' },
  { icon: 'mdi-tools', label: 'Equipamentos', to: '/materiais' },
  { icon: 'mdi-chip', label: 'Componentes', to: '/componentes-list' },
  {
    icon: 'mdi-dots-grid',
    label: 'Utilidades',
    sublinks: [
      { icon: 'mdi-calculator', label: 'Calculador de Resistores', to: '/resistores' },
    ],
  },
  { icon: 'mdi-login', label: 'Entrar', to: '/login' },
]);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>

<template>
  <q-layout view="lHh Lpr lFf" class="main-layout">
    <q-header class="main-header">
      <q-toolbar class="q-px-md q-px-md-xl container">
        <q-btn
          flat
          dense
          round
          icon="mdi-menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
          class="lt-md q-mr-md"
          color="primary"
        />

        <q-item to="/" clickable flat class="brand-item q-pa-none">
          <q-avatar square size="40px">
            <img src="/Icone.png">
          </q-avatar>
          <div class="brand-text q-ml-md text-h5 text-weight-bolder text-uppercase tracking-tighter">
            NUPEDEE
          </div>
        </q-item>

        <q-space />

        <div class="nav-links flex items-center q-gutter-x-md gt-sm">
          <template v-for="link in links" :key="link.label">
            <q-btn-dropdown
              v-if="link.sublinks"
              flat
              no-caps
              rounded
              class="nav-btn"
              :class="{ 'active-link': link.sublinks.some(sub => route.path === sub.to) }"
            >
              <template v-slot:label>
                <div class="row items-center no-wrap">
                  <q-icon :name="link.icon" size="20px" class="q-mr-sm" />
                  <span class="text-weight-bold">{{ link.label }}</span>
                </div>
                <div class="active-indicator" v-if="link.sublinks.some(sub => route.path === sub.to)"></div>
              </template>

              <q-list class="q-py-sm dropdown-list">
                <q-item
                  v-for="sub in link.sublinks"
                  :key="sub.label"
                  clickable
                  v-close-popup
                  :to="sub.to"
                  class="dropdown-item"
                >
                  <q-item-section avatar>
                    <q-icon :name="sub.icon" size="20px" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-bold text-grey-9">{{ sub.label }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-btn-dropdown>

            <q-btn
              v-else
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
          </template>
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      side="left"
      bordered
      overlay
      behavior="mobile"
      class="bg-white"
    >
      <q-list padding>
        <q-item-label header class="text-weight-bolder text-primary text-uppercase tracking-wider q-pt-lg">
          Navegação
        </q-item-label>

        <template v-for="link in links" :key="link.label">
          <q-expansion-item
            v-if="link.sublinks"
            :icon="link.icon"
            :label="link.label"
            class="q-mx-md q-mb-sm rounded-borders nav-drawer-item"
            header-class="text-weight-bold"
            :default-opened="link.sublinks.some(sub => route.path === sub.to)"
          >
            <q-item
              v-for="sub in link.sublinks"
              :key="sub.label"
              clickable
              v-ripple
              :to="sub.to"
              class="q-ml-lg q-mr-md q-mb-sm rounded-borders nav-drawer-item"
              active-class="active-drawer-link"
            >
              <q-item-section avatar>
                <q-icon :name="sub.icon" size="20px" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-bold">{{ sub.label }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-expansion-item>

          <q-item
            v-else
            clickable
            v-ripple
            :to="link.to"
            class="q-mx-md q-mb-sm rounded-borders nav-drawer-item"
            active-class="active-drawer-link"
          >
            <q-item-section avatar>
              <q-icon :name="link.icon" size="24px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-weight-bold">{{ link.label }}</q-item-label>
            </q-item-section>
          </q-item>
        </template>
      </q-list>
    </q-drawer>

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

.nav-drawer-item {
  color: #64748b;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(59, 130, 246, 0.05);
  }
}

.active-drawer-link {
  color: var(--q-primary) !important;
  background: rgba(59, 130, 246, 0.08) !important;

  .q-icon {
    color: var(--q-primary);
  }
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
