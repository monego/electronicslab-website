<template>
    <div>
        <q-input
        outlined
        v-model="localValue"
        :label="label"
        class="q-input"
        :error="!exists"
        :error-message="errorMessage"
        @blur="handleBlur"
        />
    </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'MatriculaButton',
});

import { ref } from 'vue';
import type { AxiosInstance, AxiosError } from 'axios';
import { axios, api } from 'boot/axios';

interface MatriculaButtonProps {
    label?: string
    errorMessage?: string
}

const props = withDefaults(defineProps<MatriculaButtonProps>(), {
  label: 'Matrícula',
  errorMessage: 'Matrícula não encontrada',
});

const { label, errorMessage } = props;

const localValue = ref<string>('');
const exists = ref<boolean>(true);

async function getPersonData(numeroMatricula: string) {
  try {
    const response = await (api as AxiosInstance).get('/root/pessoas', {
      params: {
        matricula: numeroMatricula,
      },
    });

    if (response.status === 200 && response.data.length > 0) {
      exists.value = true;
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

async function handleBlur() {
  await getPersonData(localValue.value);
}
</script>
