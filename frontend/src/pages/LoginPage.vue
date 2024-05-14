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

const username = ref('');
const password = ref('');
const router = useRouter();

const login = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/auth/login/', {
      username: username.value,
      password: password.value,
    });

    if (response.status === 200) {
      console.log("Login success");
      localStorage.setItem('token', response.data.token);
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
