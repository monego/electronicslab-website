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
import { ref } from 'vue';
import { useAuthStore } from 'stores/auth';
import { useRouter } from 'vue-router';
import { AxiosInstance } from 'axios';
import { axios, api } from 'boot/axios';
import EssentialLink, { EssentialLinkProps } from 'components/EssentialLink.vue';

defineOptions({
  name: 'AdminLayout',
});

const { userName } = useAuthStore();
const router = useRouter();

const publicList: EssentialLinkProps[] = [
  {
    title: 'Acesso',
    caption: 'Registro de acesso',
    icon: 'mdi-turnstile',
    link: '/#/acesso',
  },
  {
    title: 'Empréstimos',
    caption: 'Empréstimos e Devoluções',
    icon: 'mdi-arrow-collapse',
    link: '/#/emprestimo',
  },
];

const privateList: EssentialLinkProps[] = [
  {
    title: 'Atividades',
    caption: 'Criar atividades',
    icon: 'mdi-calendar-check',
    link: '/#/atividades',
  },
  {
    title: 'Equipamentos',
    caption: 'Cadastrar e consultar equipamentos',
    icon: 'mdi-hammer-screwdriver',
    link: '/#/equipamentos',
  },
];

const leftDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

const logout = async () => {
  try {
    await (api as AxiosInstance).post('/auth/logout/');
    router.push('/login');
  } catch (error) {
    console.error("Erro ao fazer logout:", error);
  }
};
</script>
