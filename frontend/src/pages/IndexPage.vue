<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { AxiosInstance } from 'axios';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { parseISO, format } from 'date-fns';

interface Aula {
  'title': string,
  'professor': string,
  'room': string,
  'start': string,
  'end': string,
}

type ColumnType = {
  name: string;
  label: string;
  field: ((row: Aula) => string);
  required?: boolean;
  align?: 'left' | 'right' | 'center';
  format?: (val: string) => string;
  sortable: boolean;
};

function capitalizeEachWord(str: string): string {
  return str
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

const $q = useQuasar();
const filter = ref<string>('');
const aulas = ref<Aula[]>([]);

const columns: ColumnType[] = [
  {
    name: 'startEnd',
    required: true,
    label: 'Horário',
    align: 'left',
    field: (row) => `${row.start} - ${row.end}`,
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'sala',
    align: 'left',
    label: 'Sala',
    field: (row) => row.room,
    sortable: true,
  },
  {
    name: 'professor',
    label: 'Professor',
    field: (row) => row.professor,
    format: (val: string) => capitalizeEachWord(`${val}`),
    sortable: true,
  },
  {
    name: 'title',
    label: 'Disciplina',
    field: (row) => row.title,
    format: (val: string) => capitalizeEachWord(`${val}`),
    sortable: true,
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
          sala_nome: string,
          sala_numero: string,
          disciplina: string,
          professor: string,
          inicio: string,
          fim: string
        }) => aulas.value.push({
          title: aula.disciplina,
          professor: aula.professor,
          room: `[${aula.sala_numero}] ${aula.sala_nome}`,
          start: format(parseISO(aula.inicio), 'HH:mm'),
          end: format(parseISO(aula.fim), 'HH:mm'),
        }));
      }
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro na comunicação com o servidor. Consulte o desenvolvedor.',
      timeout: 2500,
    });
  }
}

onMounted(async () => {
  await getUserList();
});
</script>

<template>
  <div class="q-pa-md">
    <q-table :grid="$q.screen.xs" flat bordered title="Aulas de hoje" :rows="rows" :columns="columns" row-key="startEnd"
      :filter="filter" :rows-per-page-options="[0]">
      <template v-slot:top-right>
        <q-input borderless dense debounce="300" v-model="filter" placeholder="Pesquisar">
          <template v-slot:append>
            <q-icon name="mdi-table-search" />
          </template>
        </q-input>
      </template>

      <template v-slot:body-cell-startEnd="props">
        <q-td :props="props">
          {{ props.row.start }} - {{ props.row.end }}
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<style lang="scss">
body {
  background-color: #eeeeee;
  /* Cinza claro */
}
</style>
