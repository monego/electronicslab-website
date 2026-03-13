<template>
  <q-layout view="lHh Lpr lFf" class="admin-layout">
    <q-header class="glass-header text-grey-9">
      <q-toolbar class="q-px-lg">
        <q-btn
          flat
          dense
          round
          icon="mdi-menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
          class="menu-btn"
        />

        <q-toolbar-title class="flex items-center">
          <q-avatar square size="32px" class="q-mr-md shadow-1">
            <img src="/Icone.png">
          </q-avatar>
          <span class="text-weight-bolder text-uppercase tracking-wider">NUPEDEE</span>
          <q-badge color="primary" label="ADMIN" class="q-ml-sm q-px-sm" outline />
        </q-toolbar-title>

        <q-space />

        <div class="user-action">
          <q-btn-dropdown
            flat
            no-caps
            class="user-dropdown"
            icon="mdi-account-circle"
            :label="userName"
          >
            <div class="row no-wrap q-pa-md items-center">
              <div class="column items-center">
                <q-avatar size="72px">
                  <q-icon name="mdi-account" color="primary" size="64px" />
                </q-avatar>

                <div class="text-subtitle1 q-mt-md q-mb-xs">{{ userName }}</div>
                <div class="text-caption text-grey-7 q-mb-md font-mono">ID: SEC-255</div>

                <q-btn
                  color="negative"
                  label="Finalizar Sessão"
                  push
                  size="sm"
                  v-close-popup
                  icon="mdi-logout"
                  @click="logout"
                  class="full-width"
                />
              </div>
            </div>
          </q-btn-dropdown>
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      :width="280"
      class="admin-drawer"
    >
      <div class="drawer-header q-pa-lg">
        <div class="text-h6 text-weight-bold">Dashboard</div>
        <div class="text-caption text-grey-6">Gestão de Laboratórios</div>
      </div>

      <q-list class="q-px-md q-pb-xl">
        <div class="menu-group">
          <div class="menu-group-label q-px-md q-pb-sm">ATENDIMENTO</div>
          <EssentialLink v-for="link in publicList" :key="link.title" v-bind="link" />
        </div>

        <div class="menu-group q-mt-lg">
          <div class="menu-group-label q-px-md q-pb-sm">INTERNO</div>
          <EssentialLink v-for="link in privateList" :key="link.title" v-bind="link" />
        </div>
      </q-list>

      <div class="drawer-footer absolute-bottom q-pa-md text-center">
        <div class="text-caption text-grey-5">v2.1.0 • © 2026 NUPEDEE</div>
      </div>
    </q-drawer>

    <q-page-container class="admin-container">
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

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from 'stores/auth';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import Cookie from 'js-cookie';
import EssentialLink from 'components/EssentialLink.vue';
import type { EssentialLinkProps } from 'components/EssentialLink.vue';

defineOptions({
  name: 'AdminLayout',
});

const authStore = useAuthStore();
const { userName } = useAuthStore();
const router = useRouter();
const $q = useQuasar();

const publicList: EssentialLinkProps[] = [
  {
    title: 'Acesso',
    caption: 'Fluxo de alunos',
    icon: 'mdi-turnstile',
    link: '/#/acesso',
  },
  {
    title: 'Empréstimos',
    caption: 'Equipamentos',
    icon: 'mdi-package-variant-closed',
    link: '/#/emprestimo',
  },
];

const privateList: EssentialLinkProps[] = [
  {
    title: 'Equipamentos',
    caption: 'Gestão de Inventário',
    icon: 'mdi-tools',
    link: '/#/equipamentos',
  },
  {
    title: 'Componentes',
    caption: 'Estoque do Laboratório',
    icon: 'mdi-chip',
    link: '/#/componentes',
  },
  {
    title: 'Ocorrências',
    caption: 'Ponto e Registros',
    icon: 'mdi-calendar-check',
    link: '/#/ocorrencias',
  },
  {
    title: 'Compras',
    caption: 'Requisições',
    icon: 'mdi-cart-outline',
    link: '/#/compras',
  },
];

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

const logout = async () => {
  try {
    const csrfToken = Cookie.get('csrfToken');

    const response = await api.post('/auth/logout/', {
    }, {
      headers: {
        'x-csrftoken': csrfToken,
      },
    });

    if (response.status === 200) {
      authStore.logout();
      router.push('/login')
      .catch(err => console.error('Falhou ao deslogar:', err));
    }
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Erro ao encerrar a sessão.',
      timeout: 2500,
    });
  }
};

onMounted(() => {
  authStore.getAuthStatus()
  .catch(err => console.error('Falhou ao buscar estado de autenticação:', err));
});
</script>

<style lang="scss">
.admin-layout {
  background-color: #f4f7f9;
}

.glass-header {
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  height: 64px;
}

.tracking-wider {
  letter-spacing: 0.1em;
}

.user-dropdown {
  border-radius: 8px;
  background: rgba(25, 118, 210, 0.04);
  color: var(--q-primary);
  padding: 4px 12px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(25, 118, 210, 0.08);
  }
}

.admin-drawer {
  background: white;
  border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
}

.menu-group-label {
  font-size: 0.72rem;
  font-weight: 800;
  color: #94a3b8;
  letter-spacing: 0.12em;
  padding-top: 16px;
}

.admin-container {
  padding-top: 64px;
}

/* Transitions */
.fadeIn {
  animation: fadeIn 0.3s ease forwards;
}

.fadeOut {
  animation: fadeOut 0.3s ease forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeOut {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-10px); }
}
</style>
