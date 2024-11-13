<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { AxiosInstance, AxiosError } from 'axios';
import { axios, api } from 'boot/axios';
import { useQuasar } from 'quasar';

interface Sala {
  'label': string,
  'code': string
}

interface SalaResponse {
  'id': number,
  'predio': number,
  'nome': string,
  'numero': string,
  'codigo': string,
}

interface Aula {
  'title': string,
  'professor': string,
  'sala': string,
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
const salas = ref<Sala[]>([]);
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
    field: (row) => row.sala,
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

function extractData(lab: string, title: string, startTime: string, endTime: string): Aula {
  /* Function to process the response and generate the Aula object. */

  const titleSplit = title.split(' - ');

  // Extract 'title' from 'title' (code)
  const titleDisciplina: string = titleSplit[0];

  // Extract 'professor' from 'title' for the Aula object
  const professorUpperCase = titleSplit[titleSplit.length - 1];
  // input.charAt(0).toUpperCase() + input.slice(1);

  return {
    start: startTime,
    end: endTime,
    sala: lab,
    title: titleDisciplina,
    professor: professorUpperCase,
  };
}

async function getSalas() {
  try {
    const response = await (api as AxiosInstance).get('/root/salas');

    if (response.status === 200) {
      salas.value = response.data.map((obj: SalaResponse) => ({
        label: `[${obj.numero}] ${obj.nome}`,
        code: obj.codigo,
      }));
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
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

async function getUserList(sala: Sala) {
  try {
    const response = await axios.post('https://oca.ctism.ufsm.br/ensalamento/getAulasAgora', {
      withCredentials: false,
      espaco: sala.code,
      apenasDeferidos: true,
    });
    if (response.status === 200) {
      if (response.data.length !== 0) {
        response.data.forEach((aula: { titulo: string, inicio: string, fim: string }) => {
          aulas.value.push(extractData(sala.label, aula.titulo, aula.inicio, aula.fim));
        });
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
  await getSalas();
  const promises = salas.value.map((sala) => getUserList(sala));
  await Promise.all(promises);
});
</script>

<template>
  <div class="q-pa-md">
    <q-table
      :grid="$q.screen.xs"
      flat bordered
      title="Aulas de hoje"
      :rows="rows"
      :columns="columns"
      row-key="startEnd"
      :filter="filter"
      :rows-per-page-options="[0]"
    >
      <template v-slot:top-right>
        <q-input borderless dense debounce="300" v-model="filter" placeholder="Pesquisar">
          <template v-slot:append>
            <q-icon name="search" />
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
  background-color: #eeeeee; /* Cinza claro */
}
</style>
