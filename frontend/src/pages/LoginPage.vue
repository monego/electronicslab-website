<template>
  <q-page class="flex flex-center login-page">
    <transition appear enter-active-class="animated zoomIn">
      <q-card class="login-card glass-card shadow-24">
        <q-card-section class="q-pt-xl text-center">
          <q-img
            src="/icons/logo-extenso.png"
            width="280px"
            class="q-mb-md filter-drop-shadow"
          />
          <div class="text-h5 text-weight-bold text-primary q-mt-sm">Portal Interno</div>
          <div class="text-caption text-grey-6">Autenticação de Colaboradores</div>
        </q-card-section>

        <q-card-section class="q-px-xl q-pb-xl">
          <q-form @submit="login" class="q-gutter-md">
            <q-input
              v-model="username"
              label="Nome de usuário"
              filled
              rounded
              bg-color="white"
              color="primary"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-account-outline" />
              </template>
            </q-input>

            <q-input
              v-model="password"
              label="Senha"
              type="password"
              filled
              rounded
              bg-color="white"
              color="primary"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-lock-outline" />
              </template>
            </q-input>

            <div class="q-mt-xl">
              <q-btn
                label="Acessar Sistema"
                color="primary"
                rounded
                unelevated
                type="submit"
                class="full-width login-btn"
                padding="12px"
              />
            </div>

            <div class="q-mt-md text-center">
              <div class="text-caption text-grey-5 flex items-center justify-center">
                <q-icon name="mdi-information-outline" class="q-mr-xs" />
                <span>Uso exclusivo para funcionários autorizados</span>
              </div>
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </transition>
  </q-page>
</template>

<script setup lang="ts">
import { api } from 'boot/axios';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/auth';
import { useQuasar, Loading } from 'quasar';

const $q = useQuasar();
const username = ref('');
const password = ref('');
const router = useRouter();
const authStore = useAuthStore();

const login = async () => {
  Loading.show({
    message: 'Autenticando...',
    boxClass: 'bg-white text-primary shadow-2',
    spinnerColor: 'primary'
  });

  try {
    const csrfResponse = await api.get('/auth/csrf/');
    const csrfToken = csrfResponse.data.csrftoken;

    const response = await api.post('/auth/login/', {
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
        router.push('/admin')
        .catch(err => console.error('Falhou ao fazer login:', err));
      } else {
        $q.notify({
          type: 'negative',
          message: 'Credenciais inválidas. Verifique e tente novamente.',
          position: 'top',
          timeout: 2000,
        });
      }
    }
  } catch (error) {
    console.error('Login error:', error);
    $q.notify({
      type: 'negative',
      message: 'Erro de conexão com o servidor.',
      position: 'top',
      timeout: 3000,
    });
  } finally {
    Loading.hide();
  }
};
</script>

<style lang="scss" scoped>
.login-page {
  background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent),
              radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.03), transparent),
              #f8fafc;
}

.login-card {
  width: 100%;
  max-width: 450px;
  border-radius: 24px;
}

.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05) !important;
}

.login-btn {
  font-weight: 700;
  letter-spacing: 0.05em;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(25, 118, 210, 0.2);
  }
}

.filter-drop-shadow {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.05));
}
</style>
