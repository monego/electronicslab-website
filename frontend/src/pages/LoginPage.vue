<template>
  <q-page class="flex flex-center">
    <q-card>
      <q-card-section class="text-center">
        <q-img src="/icons/logo-extenso.png" width="300px" />
      </q-card-section>
      <q-card-section>
        <q-form @submit="login">
          <q-input class="q-mt-md q-mb-md" filled v-model="username" label="Nome de usuário" />
          <q-input class="q-mt-md q-mb-md" filled v-model="password" label="Senha" type="password" />
          <q-btn class="q-mt-md q-mb-md full-width" type="submit" label="Login" color="primary" />
          <q-card flat>
            * para uso somente dos funcionários
          </q-card>
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import type { AxiosInstance } from 'axios';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/auth';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const username = ref('');
const password = ref('');
const router = useRouter();
const authStore = useAuthStore();

const login = async () => {
  try {
    const csrfResponse = await (api as AxiosInstance).get('/auth/csrf/');
    const csrfToken = csrfResponse.data.csrftoken;

    const response = await (api as AxiosInstance).post('/auth/login/', {
      username: username.value,
      password: password.value,
    }, {
      headers: {
        'x-csrftoken': csrfToken,
      },
    });

    if (response.status === 200) {
      if (response.data.authenticated) {
        authStore.login(response.data.username);
        router.push('/admin');
      } else {
        $q.notify({
          type: 'negative',
          message: 'Login ou senha incorretos. Tente novamente.',
          timeout: 1500,
        });
      }
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao tentar entrar.',
      timeout: 2500,
    });
  }
};
</script>
