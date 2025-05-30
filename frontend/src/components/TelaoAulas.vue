<template>
  <div class="q-pa-md">
    <q-table :grid="$q.screen.xs" flat bordered :rows="rows" :columns="columns" row-key="startEnd"
      :filter="filter" :rows-per-page-options="[0]" wrap-cells hide-bottom :table-style="'background-color: #e0e1dd'">

      <template v-slot:body-cell-startEnd="props">
        <q-td :props="props">
          {{ props.row.start }} - {{ props.row.end }}
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'TelaoAulas',
});

import { ref, onMounted } from 'vue';
import type { AxiosInstance, AxiosError } from 'axios';
import { axios, api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { parseISO, format, minutesToMilliseconds } from 'date-fns';
import '@fontsource-variable/inter';
import '@fontsource/lato';

interface Aula {
  'title': string,
  'professor': string,
  'room': string,
  'level': number,
  'start': string,
  'end': string,
}

interface Column {
  name: string;
  label: string;
  field: ((row: Aula) => string);
  required?: boolean;
  align?: 'left' | 'right' | 'center';
  format?: (val: string) => string;
  headerStyle: string;
  style: (row: Aula) => string;
}

function capitalizeEachWord(str: string): string {
  return str
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

const propFontSize = '33px';
const propFontFamily = 'Lato, sans-serif';

function rowLevelBg(row: Aula, cellWidth: string) {
  let backgroundColor: string;
  if (row.level === 1) {
    backgroundColor = '#ccdad1';
  } else {
    backgroundColor = '#788585';
  }
  return [
    `font-size: ${propFontSize};`,
    `width: ${cellWidth};`,
    `font-family: ${propFontFamily};`,
    'font-weight: 900;',
    `background: ${backgroundColor};`,
  ].join(' ');
}

const $q = useQuasar();
const filter = ref<string>('');
const aulas = ref<Aula[]>([]);

const columns: Column[] = [
  {
    name: 'startEnd',
    required: true,
    label: 'Horário',
    align: 'left',
    field: (row) => `${row.start} - ${row.end}`,
    format: (val: string) => `${val}`,
    headerStyle: [
      `font-size: ${propFontSize};`,
      'width: 270px',
      `font-family: ${propFontFamily};`,
      'font-weight: bold',
    ].join(' '),
    style: (row: Aula) => rowLevelBg(row, '270px'),
  },
  {
    name: 'sala',
    align: 'left',
    label: 'Sala',
    field: (row) => row.room,
    headerStyle: [
      `font-size: ${propFontSize};`,
      'width: 85px',
      `font-family: ${propFontFamily};`,
      'font-weight: bold',
    ].join(' '),
    style: (row: Aula) => rowLevelBg(row, '85px'),
  },
  {
    name: 'title',
    label: 'Disciplina',
    field: (row) => row.title,
    format: (val: string) => capitalizeEachWord(`${val}`),
    align: 'left',
    headerStyle: [
      `font-size: ${propFontSize};`,
      'width: 525px',
      `font-family: ${propFontFamily};`,
      'font-weight: bold',
    ].join(' '),
    style: (row: Aula) => rowLevelBg(row, '525px'),
  },
  {
    name: 'professor',
    label: 'Professor',
    field: (row) => row.professor,
    format: (val: string) => capitalizeEachWord(`${val}`),
    align: 'left',
    headerStyle: [
      `font-size: ${propFontSize};`,
      'width: 425px',
      `font-family: ${propFontFamily};`,
      'font-weight: bold',
    ].join(' '),
    style: (row: Aula) => rowLevelBg(row, '425px'),
  },
];

const rows = ref<Aula[]>(aulas.value);

async function getUserList() {
  try {
    const response = await (api as AxiosInstance).get('/aulas/aulas/hoje', {
      withCredentials: false,
    });
    if (response.status === 200) {
      if (response.data.length !== 0) {
        response.data.forEach((aula: {
          titulo: string,
          sala_andar: number,
          sala_nome: string,
          sala_numero: string,
          disciplina: string,
          professor: string,
          inicio: string,
          fim: string
        }) => aulas.value.push({
          title: aula.disciplina,
          professor: aula.professor,
          room: aula.sala_numero,
          level: aula.sala_andar,
          start: format(parseISO(aula.inicio), 'HH:mm'),
          end: format(parseISO(aula.fim), 'HH:mm'),
        }));
      }
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error) {
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

onMounted(async () => {
  await getUserList();
  setInterval(async () => {
    await getUserList();
  }, minutesToMilliseconds(30));
});
</script>

<style>
@import url('@fontsource-variable/inter/index.css');

body {
  font-family: 'Inter, sans-serif';
}

.floor-level {
  background-color: '#050505';
}

.upper-level {
  background-color: '#f0f0f0f0';
}
</style>
