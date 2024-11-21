<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat dense round icon="mdi-menu-close" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          NUPEDEE
        </q-toolbar-title>

        <div>
          <q-btn-dropdown class="glossy" :label=userName>
            <q-btn color="primary" label="Logout" push size="sm" v-close-popup @click="logout" />
          </q-btn-dropdown>
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header>
          Atendimento
        </q-item-label>

        <EssentialLink v-for="link in publicList" :key="link.title" v-bind="link" />

        <q-item-label header>
          Interno
        </q-item-label>

        <EssentialLink v-for="link in privateList" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from 'stores/auth';
import { useRouter } from 'vue-router';
import type { AxiosInstance, AxiosError } from 'axios';
import { api, axios } from 'boot/axios';
import Cookie from 'js-cookie';
import EssentialLink from 'components/EssentialLink.vue';
import type { EssentialLinkProps } from 'components/EssentialLink.vue';

defineOptions({
  name: 'AdminLayout',
});

const authStore = useAuthStore();
const { userName } = useAuthStore();
const router = useRouter();

const showError = ref(false);
const errorMessage = ref<string>('');

function displayError(message: string) {
  errorMessage.value = message;
  showError.value = true;
}

const publicList: EssentialLinkProps[] = [
  {
    title: 'Acesso',
    caption: 'Registrar acesso de alunos às salas',
    icon: 'mdi-turnstile',
    link: '/#/acesso',
  },
  {
    title: 'Empréstimos',
    caption: 'Empréstimos e devoluções',
    icon: 'mdi-arrow-collapse',
    link: '/#/emprestimo',
  },
];

const privateList: EssentialLinkProps[] = [
  {
    title: 'Equipamentos',
    caption: 'Cadastrar e consultar equipamentos',
    icon: 'mdi-hammer-screwdriver',
    link: '/#/equipamentos',
  },
  {
    title: 'Ocorrências',
    caption: 'Jornada e Ocorrências',
    icon: 'mdi-clock-edit-outline',
    link: '/#/ocorrencias',
  },
  {
    title: 'Estatísticas',
    caption: 'Estatísticas do banco de dados',
    icon: 'mdi-chart-line',
    link: '/#/estatisticas',
  },
];

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

const logout = async () => {
  try {
    const csrfToken = Cookie.get('csrfToken');

    const response = await (api as AxiosInstance).post('/auth/logout/', {
    }, {
      headers: {
        'x-csrftoken': csrfToken,
      },
    });

    if (response.status === 200) {
      authStore.logout();
      router.push('/login');
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        const errorData = axiosError.response.data as { detail?: string };
        const errorDetail = errorData.detail ?? 'Erro desconhecido!';
        displayError(errorDetail);
      }
    } else {
      displayError('Erro desconhecido!');
    }
  }
};

onMounted(() => {
  authStore.getAuthStatus();
});
</script>
