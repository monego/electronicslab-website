<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { format } from 'date-fns';
import { AxiosInstance } from 'axios';
import { axios, api } from 'boot/axios';

const $q = useQuasar();

const notifTimeout = 30;

const salaa = ref();
const showError = ref(false);
const errorMessage = ref('');

const matricula = ref<string>();
const tab = ref<string>('entrada');
const options = ref();

const columns = [
  {
    name: 'accessID',
    required: true,
    hidden: true,
    field: 'id',
  },
  {
    name: 'nome',
    required: true,
    label: 'Nome',
    align: 'left',
    field: (row: { nome: string }) => row.nome,
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'matricula',
    required: true,
    label: 'Matrícula',
    align: 'left',
    field: (row: { matricula: string }) => row.matricula,
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'salaa',
    required: true,
    label: 'Sala',
    align: 'left',
    field: (row: { numero: string }) => row.numero,
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'entrada',
    required: true,
    label: 'Entrada',
    align: 'left',
    field: (row: { hora_entrada: string }) => row.hora_entrada,
    format: (val: string) => `${val}`,
    sortable: true,
  },
];

interface Registro {
  'id': number,
  'pessoa': number,
  'sala': number,
  'hora_entrada': string
  'hora_saida': string
}

interface Turnstile {
  nome: string,
  matricula: string,
  numero: string,
  hora_entrada: string,
  hora_saida?: string,
}

interface Row {
  'id': number,
  'nome': string,
  'matricula': string,
  'numero': string,
  'hora_entrada': string,
}

const selected = ref <Row[]>([]);

const rows = ref<Turnstile[]>([]);

function displayError(error: unknown) {
  errorMessage.value = (error as Error).message;
  showError.value = true;
}

async function getSalas() {
  try {
    const response = await (api as AxiosInstance).get('/root/salas');

    if (response.status === 200) {
      options.value = response.data.map((item: { nome: string, numero: string }) => ({
        label: `[${item.numero}] ${item.nome}`,
        value: item.numero,
      }));
    } else {
      // connError.value = !connError.value;
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      displayError(error);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`);
      }
    } else {
      displayError(error);
    }
    throw error; // Rethrow the error
  }
}

async function getRow(apiUrl: string) {
  try {
    const response = await (api as AxiosInstance).get(apiUrl);
    if (response.status === 200) {
      return response.data[0].id;
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      displayError(error);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`);
      }
    } else {
      displayError(error);
    }
    throw error;
  }
  return null;
}

async function getFromPk(id: number, apiPart: string) {
  try {
    const response = await (api as AxiosInstance).get(`/root/${apiPart}/${id}`);
    if (response.status === 200) {
      const responseData = response.data;
      return responseData;
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      displayError(error);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`);
      }
    } else {
      displayError(error);
    }
    throw error;
  }
  return null;
}

async function getRegistered() {
  try {
    const response = await (api as AxiosInstance).get('/controle/registros/');

    if (response.status === 200) {
      const accessList = response.data
        .filter((item: Registro) => item.hora_saida == null)
        .map(async (item: Registro) => {
          const studentData = await getFromPk(item.pessoa, 'pessoas');
          const salaData = await getFromPk(item.sala, 'salas');
          return {
            id: item.id,
            nome: studentData.nome,
            matricula: studentData.matricula,
            numero: salaData.numero,
            hora_entrada: format(item.hora_entrada, 'yyyy-MM-dd HH:mm:ss'),
          };
        });
      rows.value = await Promise.all(accessList);
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      displayError(error);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`);
      }
    } else {
      displayError(error);
    }
    throw error;
  }
}
async function registerAccess() {
  try {
    const now = new Date();
    const isoString = now.toISOString();
    const requestBody = {
      pessoa: await getRow(`/root/pessoas/?matricula=${matricula.value}`),
      sala: await getRow(`/root/salas/?numero=${salaa.value.value}`),
      hora_entrada: isoString,
    };

    const response = await (api as AxiosInstance).post(
      '/controle/registros/',
      requestBody,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      },
    );

    if (response.status === 201) {
      $q.notify({
        type: 'positive',
        message: 'Acesso registrado com successo.',
        timeout: notifTimeout,
      });

      (async () => {
        try {
          await getRegistered();
        } catch (error: unknown) {
          displayError(error);
        }
      })();

      return response.data;
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      displayError(error);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`);
      }
    } else {
      displayError(error);
    }
    throw error;
  }
  return null;
}

async function releaseStudent(rowId: number) {
  try {
    const now = new Date();
    const isoString = now.toISOString();

    const response = await (api as AxiosInstance).patch(`/controle/registros/${rowId}/`, {
      hora_saida: isoString,
    });

    if (response.status === 200) {
      $q.notify({
        type: 'positive',
        message: 'Acesso liberado com successo.',
        timeout: notifTimeout,
      });

      selected.value = [];

      (async () => {
        try {
          await getRegistered();
        } catch (error: unknown) {
          displayError(error);
        }
      })();

      return response.data;
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      displayError(error);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`);
      }
    } else {
      displayError(error);
    }
    throw error;
  }
  return null;
}

function releaseStudents(studentList: Row[]) {
  studentList.forEach((student: Row) => {
    releaseStudent(student.id);
  });
}

onMounted(() => {
  (async () => {
    try {
      await getSalas();
      await getRegistered();
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        displayError(error);
        if (error.response) {
          console.error(`Status: ${error.response.status}`);
          console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`);
        }
      } else {
        displayError(error);
      }
      throw error;
    }
  })();
});
</script>

<template>
  <q-page>
    <div class="q-pa-md">
      <q-card>
        <q-tabs v-model="tab" dense class="text-grey q-mb-lg" active-color="primary"
        indicator-color="primary" align="justify" narrow-indicator>
          <q-tab class="text-purple" name="entrada" icon="mdi-clock-in" label="Entrada" />
          <q-tab class="text-orange" name="saida" icon="mdi-clock-out" label="Saída" />
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="tab" animated>
          <q-tab-panel name="entrada">
            <q-dialog v-model="showError">
              <q-card>
                <q-card-section>
                  <div class="text-h6">Erro</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                  {{ errorMessage }}
                </q-card-section>

                <q-card-actions align="right">
                  <q-btn flat label="OK" color="primary" v-close-popup />
                </q-card-actions>
              </q-card>
            </q-dialog>

            <div class="q-gutter-md">
              <q-input outlined v-model="matricula" label="Matrícula" />
              <q-select outlined v-model="salaa" :options="options" label="Sala" />
              <q-btn @click="registerAccess" color="white" text-color="black" label="Registrar" />
            </div>

          </q-tab-panel>

          <q-tab-panel name="saida">
            <div class="q-gutter-md">
              <q-table
              title="Registros"
              selection="multiple"
              :rows="rows"
              :columns="columns"
              row-key="id"
              v-model:selected="selected"
              />
              <q-btn @click="releaseStudents(selected)">Liberar</q-btn>
            </div>
          </q-tab-panel>
        </q-tab-panels>
      </q-card>
    </div>
  </q-page>
</template>
