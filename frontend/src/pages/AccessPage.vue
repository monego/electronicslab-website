<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Ref } from 'vue';
import { useQuasar } from 'quasar';
import { format } from 'date-fns';
import type { AxiosInstance } from 'axios';
import { api } from 'boot/axios';
import MatriculaButton from 'components/MatriculaButton.vue';

const $q = useQuasar();

const notifTimeout = 30;

const sala = ref();
const matricula = ref<string>('');
const tab: Ref<string> = ref<string>('entrada');
const options = ref();

function capitalizeEachWord(str: string): string {
  return str
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

interface Row {
  'pessoa_nome': string,
  'pessoa_matricula': string,
  'sala_numero': string,
  'hora_entrada': string,
}

interface Column {
  name: string;
  label: string;
  field: ((row: Row) => string);
  required?: boolean;
  align?: 'left' | 'right' | 'center';
  format: (val: string) => string;
  sortable?: boolean;
}

const columns: Column[] = [
  {
    name: 'nome',
    required: true,
    label: 'Nome',
    align: 'left',
    field: (row: Row) => row.pessoa_nome,
    format: (val: string) => capitalizeEachWord(`${val}`),
    sortable: true,
  },
  {
    name: 'matricula',
    required: true,
    label: 'Matrícula',
    align: 'left',
    field: (row: Row) => row.pessoa_matricula,
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'sala',
    required: true,
    label: 'Sala',
    align: 'left',
    field: (row: Row) => row.sala_numero,
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'entrada',
    required: true,
    label: 'Entrada',
    align: 'left',
    field: (row: Row) => row.hora_entrada,
    format: (val: string) => format(`${val}`, 'yyyy-MM-dd HH:mm:ss'),
    sortable: true,
  },
];

interface Turnstile {
  nome: string,
  matricula: string,
  numero: string,
  hora_entrada: string,
  hora_saida?: string,
}

const selected = ref<Row[]>([]);

const rows = ref<Turnstile[]>([]);

async function getSalas() {
  try {
    const response = await (api as AxiosInstance).get('/root/salas');

    if (response.status === 200) {
      options.value = response.data.map((item: { nome: string, numero: string }) => ({
        label: `[${item.numero}] ${item.nome}`,
        value: item.numero,
      }));
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao buscar salas no servidor.',
      timeout: 2500,
    });
  }
}

async function getRegistered() {
  try {
    const response = await (api as AxiosInstance).get('/controle/registros/');

    if (response.status === 200) {
      const accessList = response.data
        .map(async (item: Row) => ({
          pessoa_nome: item.pessoa_nome,
          pessoa_matricula: item.pessoa_matricula,
          sala_numero: item.sala_numero,
          hora_entrada: item.hora_entrada,
        }));
      rows.value = await Promise.all(accessList);
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao buscar acessos registrados.',
      timeout: 2500,
    });
  }
}

async function registerAccess() {
  const payload = {
    matricula: matricula.value,
    sala: sala.value.value,
  };

  try {
    const response = await (api as AxiosInstance).post('/controle/registros/', payload);

    if (response.status === 201) {
      $q.notify({
        type: 'positive',
        message: 'Acesso registrado com successo.',
        timeout: notifTimeout,
      });

      await getRegistered();

      return response.data;
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro na comunicação com servidor ao registrar acesso.',
      timeout: 2500,
    });
  }
  return null;
}

async function releaseStudent(numeroMatricula: string) {
  try {
    const response = await (api as AxiosInstance).patch('/controle/registros/bymatricula/', {
      matricula: numeroMatricula,
    });

    if (response.status === 200) {
      $q.notify({
        type: 'positive',
        message: 'Acesso liberado com successo.',
        timeout: notifTimeout,
      });

      selected.value = [];

      await getRegistered();

      return response.data;
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao liberar acesso.',
      timeout: 2500,
    });
  }
  return null;
}

function releaseStudents(studentList: Row[]) {
  studentList.forEach((student: Row) => {
    releaseStudent(student.pessoa_matricula);
  });
}

onMounted(() => {
  (async () => {
    try {
      await getSalas();
      await getRegistered();
    } catch (error: unknown) {
      $q.notify({
        type: 'negative',
        message: 'Erro ao buscar salas ou registros no servidor.',
        timeout: 2500,
      });
    }
  })();
});
</script>

<template>
  <q-page>
    <q-card class="q-pa-md no-shadow">
      <q-tabs v-model="tab" dense class="text-grey q-mb-lg" active-color="primary" indicator-color="primary"
        align="justify" narrow-indicator>
        <q-tab class="text-purple" name="entrada" icon="mdi-clock-in" label="Entrada" />
        <q-tab class="text-orange" name="saida" icon="mdi-clock-out" label="Saída" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="entrada">
          <MatriculaButton v-model="matricula" />
          <q-select outlined v-model="sala" :options="options" label="Sala" class="q-input" />
          <q-btn @click="registerAccess" label="Registrar" type="submit" color="positive"
            icon="mdi-turnstile-outline" />
        </q-tab-panel>

        <q-tab-panel name="saida">
          <q-table flat bordered title="Registros" selection="multiple" :rows="rows" :columns="columns"
            row-key="pessoa_matricula" v-model:selected="selected" />
          <div style="padding-top: 20px;">
            <q-btn @click="releaseStudents(selected)" label="Liberar" type="submit" color="positive"
              icon="mdi-turnstile-outline" />
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </q-page>
</template>
