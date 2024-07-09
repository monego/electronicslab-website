<template>
    <q-page class="flex flex-center">
        <q-card>
            <q-card-section>
                <q-form @submit="login">
                    <q-input v-model="username" label="Nome de usuário" outlined />
                    <q-input v-model="password" label="Senha" type="password" outlined />
                    <q-btn type="submit" label="Login" color="primary" class="full-width" />
                </q-form>
            </q-card-section>
        </q-card>
    </q-page>
</template>

<script setup lang="ts">
import axios from 'axios';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from 'stores/auth';

const username = ref('');
const password = ref('');
const router = useRouter();
const authStore = useAuthStore();

const login = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
      username: username.value,
      password: password.value,
    });

    if (response.status === 200) {
      authStore.setUsername(response.data.username);
      router.push('/admin');
    }
    else {
      console.log('Login failed');
    }
  } catch (error) {
    console.log(error);
  }
};
</script>
