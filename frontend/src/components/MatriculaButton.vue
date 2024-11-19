<template>
    <div>
        <q-input
        outlined
        v-model="modelValue"
        :label="label"
        class="q-input"
        :error="!exists"
        :error-message="errorMessage"
        @blur="handleBlur"
        />
    </div>

    <q-dialog v-model="prompt" persistent>
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Verificação</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input filled v-model="nomePessoa" hint="Nome" disable readonly />
          <q-input filled v-model="matriculaPessoa" hint="Matrícula" disable readonly />
          <q-input v-model="emailPessoa" hint="Email" />
          <q-input v-model="telefonePessoa" hint="Telefone" />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="OK" v-close-popup />
          <q-btn flat label="Atualizar" @click="patchPersonData(matriculaPessoa)" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { AxiosInstance, AxiosError } from 'axios';
import { axios, api } from 'boot/axios';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const notifTimeout = 30;
const prompt = ref<boolean>(false);

const modelValue = defineModel<string>();

defineOptions({
  name: 'MatriculaButton',
});

defineProps({
  label: {
    type: String,
    default: 'Matrícula',
  },
  errorMessage: {
    type: String,
    default: 'Matrícula não encontrada',
  },
});

const exists = ref<boolean>(true);
const nomePessoa = ref<string>('');
const matriculaPessoa = ref<string>('');
const emailPessoa = ref<string>('');
const telefonePessoa = ref<string>('');

async function getPersonData(numeroMatricula: string) {
  try {
    const response = await (api as AxiosInstance).get('/root/pessoas', {
      params: {
        matricula: numeroMatricula,
      },
    });

    if (response.status === 200 && response.data.length > 0) {
      nomePessoa.value = response.data[0].nome;
      matriculaPessoa.value = response.data[0].matricula;
      emailPessoa.value = response.data[0].email;
      telefonePessoa.value = response.data[0].telefone;
      exists.value = true;
      prompt.value = true;
    } else {
      exists.value = false;
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        throw error;
      }
    } else {
      throw error;
    }
    throw error;
  }
}

async function patchPersonData(numeroMatricula: string) {
  try {
    const response = await (api as AxiosInstance).patch('/root/pessoas/mailphone/', {
      matricula: numeroMatricula,
      email: emailPessoa.value,
      telefone: telefonePessoa.value,
    });

    if (response.status === 200) {
      $q.notify({
        type: 'positive',
        message: 'Cadastro atualizado com sucesso.',
        timeout: notifTimeout,
      });

      return response.data;
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao atualizar cadastro.',
      timeout: notifTimeout,
    });
  }
  return null;
}

async function handleBlur() {
  await getPersonData(modelValue.value ?? '');
}
</script>
