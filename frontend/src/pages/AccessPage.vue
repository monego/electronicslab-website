<script setup lang="ts">
import { ref } from 'vue';
import { useQuasar } from 'quasar';

import axios from 'axios';

const $q = useQuasar();

const notifTimeout = 30;

const salaa = ref();
const connError = ref(false);

const matricula = ref();
const tab = ref('entrada');
const options = ref();

const djangoServer: string = 'http://127.0.0.1:8000';

axios.get(`${djangoServer}/api/salas`, {
  params: {
    username: '',
    password: '',
  },
})
  .then((response) => {
    options.value = response.data.map((item: { nome: string, numero: string }) => ({
      label: `[${item.numero}] ${item.nome}`,
      value: item.numero,
    }));
  })
  .catch((error) => {
    connError.value = !connError.value;
  })
  .finally(() => {
    // always executed
  });

async function getRow(apiUrl: string) {
  try {
    const { data } = await axios.get(
      apiUrl,
      {
        auth: {
          username: '',
          password: '',
        },

        headers: {
          'Content-Type': 'application/json',
        },
      },
    );

    return data[0].id;
  } catch (err) {
    if (axios.isAxiosError(err)) {
      console.log(err.message);
      console.log(err.response?.status);
    }
  }
  return null;
}

async function registerAccess() {
  try {
    const now = new Date();
    const isoString = now.toISOString();
    const requestBody = {
      pessoa: await getRow(`${djangoServer}/api/pessoas/?matricula=${matricula.value}`),
      sala: await getRow(`${djangoServer}/api/salas/?numero=${salaa.value.value}`),
      hora_entrada: isoString,
    };

    const response = await axios.post(
      `${djangoServer}/api/registros/`,
      requestBody,
      {
        auth: {
          username: '',
          password: '',
        },

        headers: {
          'Content-Type': 'application/json',
        },
      },
    );

    $q.notify({
      type: 'positive',
      message: 'Acesso registrado com successo.',
      timeout: notifTimeout,
    });

    return response.data;
  } catch (err) {
    if (axios.isAxiosError(err)) {
      $q.notify({
        type: 'negative',
        message: 'Houve algum erro ao registrar ao acesso.',
        timeout: notifTimeout,
      });
      console.log(err.message);
      console.log(err.response?.status);
    }
  }
  return null;
}

const columns = [
  {
    name: 'name',
    required: true,
    label: 'Nome',
    align: 'left',
    field: (row: { name: string }) => row.name,
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'matricula', align: 'center', label: 'Matrícula', field: 'matricula', sortable: true,
  },
  {
    name: 'entrada', label: 'Entrada', field: 'entrada', sortable: true,
  },
  { name: 'saida', label: 'Saída', field: 'saida' },
  { name: 'sala', label: 'Sala', field: 'sala' },
];

const rows = [
  {
    name: 'Student 1',
    matricula: 159,
    entrada: 6.0,
    saida: 24,
    sala: 4.0,
  },
  {
    name: 'Student 2',
    matricula: 237,
    entrada: 9.0,
    saida: 37,
    sala: 4.3,
  },
  {
    name: 'Student 3',
    matricula: 262,
    entrada: 16.0,
    saida: 23,
    sala: 6.0,
  },
];
</script>

<template>
  <q-page>
    <div class="q-pa-md">

      <q-card>
        <q-tabs v-model="tab" dense class="text-grey" active-color="primary" indicator-color="primary" align="justify"
          narrow-indicator>
          <q-tab class="text-purple" name="entrada" icon="mdi-clock-in" label="Entrada" />
          <q-tab class="text-orange" name="saida" icon="mdi-clock-out" label="Saída" />
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="tab" animated>
          <q-tab-panel name="entrada">
            <q-dialog v-model="connError">
              <q-card>
                <q-card-section>
                  <div class="text-h6">Erro</div>
                </q-card-section>

                <q-card-section class="q-pt-none">
                  Não foi possível buscar as salas no banco de dados. Verifique a conexão.
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
            <q-table title="Registros" selection="multiple" :rows="rows" :columns="columns" row-key="name" />
          </q-tab-panel>
        </q-tab-panels>
      </q-card>
    </div>
  </q-page>
</template>
