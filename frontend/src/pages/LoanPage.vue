<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { AxiosInstance, AxiosError } from 'axios';
import { axios, api } from 'boot/axios';
import { format } from 'date-fns';
import { useQuasar } from 'quasar';

const loanId = ref();
const matricula = ref();
const obs = ref();
const loanStatus = ref('pending');
const tab = ref('retirada');
const filter = ref<string>();
const dialog = ref<boolean>(false);
const $q = useQuasar();
const notifTimeout = 30;
let allLoans: string;

interface Loan {
  identificador: string;
  responsavel_nome: string;
  funcionario_nome: string;
  local: string;
  retirada: string;
  devolucao: string;
}

interface LoanItem {
  emprestimo: string,
  equipamento: number | string,
  equipamento_patrimonio: string,
  nome: string,
  recebente_nome: string,
  devolvido: boolean,
  devolucao: string,
}

const loanItems = ref<LoanItem[]>([]);
const newItems = ref<string[]>([]);

const selectedId = ref<string>('');
const selectedResponsavel = ref<string>('');
const selectedEncerrado = ref<boolean>(false);

function capitalizeEachWord(str: string): string {
  return str
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

const showError = ref(false);
const errorMessage = ref<string>('');

function displayError(message: string) {
  errorMessage.value = message;
  showError.value = true;
}

type ColumnType = {
  name: string;
  label: string;
  field: string | ((row: Loan) => string);
  required?: boolean;
  align?: 'left' | 'right' | 'center';
  format?: (val: Loan) => string;
  sortable?: boolean;
};

const columns: ColumnType[] = [
  {
    name: 'identificador',
    required: true,
    label: 'Identificador',
    align: 'left',
    field: ((row: Loan) => row.identificador),
    format: (val: Loan) => `${val}`,
    sortable: true,
  },
  {
    name: 'responsavel',
    align: 'center',
    label: 'Responsável',
    field: ((row: Loan) => row.responsavel_nome),
    format: (val: Loan) => capitalizeEachWord(`${val}`),
    sortable: true,
  },
  {
    name: 'funcionario',
    label: 'Funcionário',
    field: ((row: Loan) => row.funcionario_nome),
    sortable: true,
  },
  {
    name: 'local',
    label: 'Local',
    field: ((row: Loan) => row.local),
  },
  {
    name: 'retirada',
    label: 'Retirada',
    field: ((row: Loan) => row.retirada),
    format: (val: Loan) => format(`${val}`, 'yyyy-MM-dd HH:mm:ss'),
  },
  {
    name: 'devolucao',
    label: 'Devolução',
    field: '',
  },
];

const rows = ref<Loan[]>([]);

async function getLoans() {
  try {
    if (loanStatus.value === 'pending') {
      allLoans = '';
    } else if (loanStatus.value === 'all') {
      allLoans = '?all=true';
    }

    const response = await (api as AxiosInstance).get(`/controle/emprestimos${allLoans}`);

    if (response.status === 200) {
      rows.value = response.data.map((loan: Loan) => ({
        identificador: loan.identificador,
        responsavel_nome: loan.responsavel_nome,
        funcionario_nome: loan.funcionario_nome,
        local: loan.local,
        retirada: loan.retirada,
      }));
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        const axiosError = error as AxiosError;
        if (axiosError.response) {
          const errorData = axiosError.response.data as { detail?: string };
          const errorDetail = errorData.detail ?? 'Erro desconhecido!';
          displayError(errorDetail);
        }
      }
    } else {
      displayError('Erro desconhecido!');
    }
    throw error;
  }
}

async function registerLoan() {
  const payload = {
    identificador: loanId.value,
    matricula: matricula.value,
    obs: obs.value,
    items: newItems.value,
  };

  try {
    const response = await (api as AxiosInstance).post('/controle/emprestimos/', payload);

    if (response.status === 201) {
      $q.notify({
        type: 'positive',
        message: 'Empréstimo registrado com successo.',
        timeout: notifTimeout,
      });
      await getLoans();
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        const errorData = axiosError.response.data as { detail?: string };
        const errorDetail = errorData.detail ?? 'Erro desconhecido!';
        displayError(errorDetail);
      }
    } else {
      displayError('Erro desconhecido!');
    }
    throw error;
  }
}

async function returnItem(loan: string, name: string, index: number) {
  try {
    const response = await (api as AxiosInstance).patch('/controle/items/return/', {
      emprestimo: loan,
      nome: name,
    });

    if (response.status === 200) {
      loanItems.value[index].devolvido = true;
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        const errorData = axiosError.response.data as { detail?: string };
        const errorDetail = errorData.detail ?? 'Erro desconhecido!';
        displayError(errorDetail);
      }
    } else {
      displayError('Erro desconhecido!');
    }
  }
  return null;
}

async function returnLoan(loan: string) {
  try {
    const response = await (api as AxiosInstance).patch('/controle/emprestimos/byidentifier/', {
      identificador: loan,
    });

    if (response.status === 200) {
      $q.notify({
        type: 'positive',
        message: 'Devolvido com successo.',
        timeout: notifTimeout,
      });
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        const errorData = axiosError.response.data as { detail?: string };
        const errorDetail = errorData.detail ?? 'Erro desconhecido!';
        displayError(errorDetail);
      }
    } else {
      displayError('Erro desconhecido!');
    }
  }
  return null;
}

function returnAllItems(id: string) {
  loanItems.value.forEach((item, index) => {
    if (!item.devolvido) {
      returnItem(
        item.emprestimo,
        item.equipamento ? item.equipamento_patrimonio : item.nome,
        index,
      );
    }
  });
  returnLoan(id);
  dialog.value = false;
  getLoans();
}

function addItem() {
  newItems.value.push('');
}

function removeItem(index: number) {
  newItems.value.splice(index, 1);
}

function getNome(item: LoanItem) {
  let nome: string;
  if ('equipamento_nome' in item) {
    nome = `${item.equipamento_nome} (${item.equipamento_patrimonio})`;
  } else {
    nome = item.nome;
  }
  return nome;
}

function formatReturn(item: LoanItem) {
  return format(item.devolucao, 'yyyy-MM-dd HH:mm:ss');
}

function getPatrOrNome(item: LoanItem) {
  let patrOrNome: string;
  if (item.equipamento) {
    patrOrNome = item.equipamento_patrimonio;
  } else {
    patrOrNome = item.nome;
  }
  return patrOrNome;
}

async function getItems(identifier: string, taker: string) {
  selectedId.value = identifier;
  selectedResponsavel.value = taker;
  try {
    const responseItems = await (api as AxiosInstance).get('/controle/items/', { params: { emprestimo: identifier } });
    const responseEmprestimo = await (api as AxiosInstance).get('/controle/emprestimos/?all=true', { params: { identificador: identifier } });

    if (responseItems.status === 200 && responseEmprestimo.status === 200) {
      loanItems.value = responseItems.data;
      const [{ encerrado }] = responseEmprestimo.data;
      selectedEncerrado.value = encerrado;
    } else {
      throw new Error('Request failed');
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        const axiosError = error as AxiosError;
        if (axiosError.response) {
          const errorData = axiosError.response.data as { detail?: string };
          const errorDetail = errorData.detail ?? 'Erro desconhecido!';
          displayError(errorDetail);
        }
      }
    } else {
      displayError('Erro desconhecido!');
    }
    throw error;
  }
  dialog.value = true;
}

watch(loanStatus, () => {
  getLoans();
});

onMounted(() => {
  getLoans();
});
</script>

<template>
  <q-card class="q-pa-md">
    <q-card class="q-gutter-md">
      <q-card>
        <q-tabs
        v-model="tab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator>
          <q-tab
          class="text-purple"
          name="retirada"
          icon="mdi-arrow-top-right-thin"
          label="Retirada" />
          <q-tab
          class="text-orange"
          name="devolucao"
          icon="mdi-arrow-bottom-left-thin"
          label="Devolução" />
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="tab" animated>
            <q-tab-panel name="retirada">

            <q-card class="flex-container">
              <q-card class="pad">
                <q-input outlined v-model="loanId" class="pad" label="Identificador" />
                <q-input outlined v-model="matricula" class="pad" label="Matrícula" />
                <q-input outlined v-model="obs" class="pad" label="Observação" />
                <q-form @submit="registerLoan">
                  <div v-for="index in newItems.length" :key="index" class="q-mb-md">
                    <q-input
                      v-model="newItems[index]"
                      label="Item"
                      filled
                      lazy-rules
                      :rules="[val => !!val || 'Field cannot be empty']"
                    />
                    <q-btn
                      icon="remove_circle"
                      color="negative"
                      @click="removeItem(index)"
                      class="col-2"
                      flat
                      round
                    />
                  </div>

                  <!-- Button to Add a New Item -->
                  <q-btn
                    label="Adicionar"
                    color="primary"
                    @click="addItem"
                    icon="add"
                    class="q-mb-md"
                  />

                  <!-- Submit Button to Save the List -->
                  <q-btn
                    label="Registrar"
                    type="submit"
                    color="positive"
                    icon="save"
                  />
                </q-form>
              </q-card>
            </q-card>
          </q-tab-panel>

          <q-tab-panel name="devolucao">

            <q-dialog v-model="dialog">
              <q-card>
                <q-toolbar>
                  <q-avatar>
                    <img src="https://cdn.quasar.dev/logo-v2/svg/logo.svg">
                  </q-avatar>

                  <q-toolbar-title>
                    Empréstimo {{ selectedId }} ({{ selectedResponsavel }})
                  </q-toolbar-title>

                  <q-btn flat round dense icon="close" v-close-popup />
                </q-toolbar>

                <q-card-section>
                  <div v-for="(item, index) in loanItems" :key="index"
                  class="q-gutter-md row items-center">
                    <span class="col">
                      {{ getNome(item) }}
                    </span>
                    <div class="col-auto">
                      <q-btn
                        @click="returnItem(item.emprestimo, getPatrOrNome(item), index)"
                        :disable="item.devolvido"
                        label="Devolver"
                        color="primary"
                      />
                    </div>
                    <div v-if="item.devolvido" class="col-auto">
                      {{ item.recebente_nome }} -- {{ formatReturn(item) }}
                    </div>
                  </div>
                </q-card-section>

                <q-card-section>
                <q-btn
                    label="Quitar"
                    color="primary"
                    :disable="selectedEncerrado"
                    @click="returnAllItems(selectedId)"
                  />
                </q-card-section>
              </q-card>
            </q-dialog>

            <q-option-group
              v-model="loanStatus"
              inline
              class="q-mb-md"
              :options="[
                { label: 'Pendentes', value: 'pending' },
                { label: 'Todos', value: 'all' },
              ]"
            />

            <q-table
            flat bordered title="Empréstimos" :rows="rows" :columns="columns" :filter=filter
            row-key="identificador">

              <template v-slot:top-right>
                <q-input borderless dense debounce="300" v-model="filter" placeholder="Pesquisar">
                  <template v-slot:append>
                    <q-icon name="mdi-magnify" />
                  </template>
                </q-input>
              </template>

              <template v-slot:body-cell-devolucao="props">
                <q-td :props="props">
                  <q-btn
                    label="Visualizar"
                    color="primary"
                    @click="getItems(props.row.identificador, props.row.responsavel_nome)"
                  />
                </q-td>
                </template>

            </q-table>
          </q-tab-panel>
        </q-tab-panels>
      </q-card>
    </q-card>
  </q-card>
</template>

<style>
.q-row-inactive {
  background-color: #0000f0; /* Light gray background for rows with null hora_devolucao */
  color: #a0a0a0; /* Gray text color for rows with null hora_devolucao */
}

.q-row-active {
  background-color: #ffffff; /* White background for rows with non-null hora_devolucao */
  color: #000000; /* Black text color for rows with non-null hora_devolucao */
}
</style>
