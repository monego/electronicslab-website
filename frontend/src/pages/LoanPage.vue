<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import type { AxiosInstance } from 'axios';
import { api } from 'boot/axios';
import { format } from 'date-fns';
import { useQuasar } from 'quasar';
import MatriculaButton from 'components/MatriculaButton.vue';

const loanId = ref();
const matricula = ref();
const obs = ref();
const loanStatus = ref('pending');
const startCode = ref<number | undefined>();
const pages = ref<number | undefined>();
const tab = ref('retirada');
const idExists = ref<boolean>(false);
const obsTooLong = ref<boolean>(false);
const filter = ref<string>();
const dialog = ref<boolean>(false);
const $q = useQuasar();
const notifTimeout = 30;
let allLoans: string;

interface Loan {
  identificador: string;
  responsavel_nome: string;
  responsavel_matricula: string;
  funcionario_nome: string;
  items_nomes: string;
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
const selectedMatricula = ref<string>('');
const selectedEncerrado = ref<boolean>(false);

function capitalizeEachWord(str: string): string {
  return str
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

interface Column {
  name: string;
  label: string;
  field: string | ((row: Loan) => string);
  required?: boolean;
  align?: 'left' | 'right' | 'center';
  format?: (val: Loan) => string;
  sortable?: boolean;
}

const columns: Column[] = [
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
    name: 'matricula',
    align: 'center',
    label: 'Matrícula',
    field: ((row: Loan) => row.responsavel_matricula),
    format: (val: Loan) => `${val}`,
    sortable: false,
  },
  {
    name: 'items_nomes',
    align: 'center',
    label: 'Items',
    field: ((row: Loan) => row.items_nomes),
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
    sortable: true,
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
        responsavel_matricula: loan.responsavel_matricula,
        responsavel_nome: loan.responsavel_nome,
        funcionario_nome: loan.funcionario_nome,
        items_nomes: loan.items_nomes,
        local: loan.local,
        retirada: loan.retirada,
      }));
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao buscar empréstimos.',
      timeout: 2500,
    });
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

      /* Clear all fields after loan is succesfully registered. */
      loanId.value = null;
      matricula.value = null;
      obs.value = null;
      newItems.value = [''];

      await getLoans();
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao registrar empréstimo.',
      timeout: 2500,
    });
  }
}

async function returnItem(loan: string, name: string, index: number) {
  try {
    const response = await (api as AxiosInstance).patch('/controle/items/return/', {
      emprestimo: loan,
      nome: name,
    });

    if (response.status === 200) {
      if (loanItems.value[index]) {
        loanItems.value[index].devolvido = true;
      }
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao registrar devolução do item.',
      timeout: 2500,
    });
  }
  return null;
}

async function returnLoan(loan: string) {
  try {
    const response = await (api as AxiosInstance).patch('/controle/emprestimos/byidentifier/', {
      identificador: loan,
    });

    if (response.status === 200) {
      await getLoans();

      $q.notify({
        type: 'positive',
        message: 'Devolvido com successo.',
        timeout: notifTimeout,
      });
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao registrar devolução.',
      timeout: 2500,
    });
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

async function getItems(identifier: string, taker: string, takerMatricula: string) {
  selectedId.value = identifier;
  selectedResponsavel.value = taker;
  selectedMatricula.value = takerMatricula;

  try {
    const responseItems = await (api as AxiosInstance).get('/controle/items/', {
      params: {
        emprestimo: identifier,
      },
    });
    const responseEmprestimo = await (api as AxiosInstance).get('/controle/emprestimos/?all=true', {
      params: {
        identificador: identifier,
      },
    });

    if (responseItems.status === 200 && responseEmprestimo.status === 200) {
      loanItems.value = responseItems.data;
      const [{ encerrado }] = responseEmprestimo.data;
      selectedEncerrado.value = encerrado;
    } else {
      throw new Error('Request failed');
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao buscar itens.',
      timeout: 2500,
    });
  }
  dialog.value = true;
}

async function printCodes(start: number | undefined, nPages: number | undefined) {
  try {
    const response = await (api as AxiosInstance).get('/controle/emprestimos/printsheet', {
      params: {
        inicio: start,
        paginas: nPages,
      },
      responseType: 'blob',
    });

    if (response.status === 200) {
      const blob = response.data;
      const fileURL = URL.createObjectURL(blob);
      window.open(fileURL, '_blank');
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao calcular códigos de empréstimo.',
      timeout: 2500,
    });
  }
}

async function identificadorExists() {
  try {
    const response = await (api as AxiosInstance).get('/controle/emprestimos', {
      params: {
        identificador: loanId.value,
      },
    });

    if (response.status === 200 && response.data.length > 0) {
      idExists.value = true;
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro no servidor ao registrar empréstimo.',
      timeout: 2500,
    });
  }
}

function validatePlace() {
  if (obs.value.length > 20) {
    obsTooLong.value = true;
  } else {
    obsTooLong.value = false;
  }
}

watch(loanStatus, () => {
  getLoans();
});

onMounted(() => {
  getLoans();
});
</script>

<template>
  <q-page>
    <q-card class="q-pa-md no-shadow">
      <q-tabs v-model="tab" dense class="text-grey q-mb-lg" active-color="primary" indicator-color="primary"
        align="justify" narrow-indicator>
        <q-tab class="text-purple" name="retirada" icon="mdi-arrow-top-right-thin" label="Retirada" />
        <q-tab class="text-orange" name="devolucao" icon="mdi-arrow-bottom-left-thin" label="Devolução" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="retirada">
          <div class="row full-width">
            <div class="col-6 bg-light q-pa-md">
              <q-card>
                <q-card-section>
                  <q-input outlined v-model="loanId" class="q-input" label="Identificador" :error="idExists"
                    error-message="Este identificador já foi cadastrado" @blur="identificadorExists" />
                  <MatriculaButton v-model="matricula" />
                  <q-input outlined v-model="obs" class="q-input" label="Observação/Local" :error="obsTooLong"
                    error-message="O local excede 20 caracteres" @blur="validatePlace" />
                  <q-form @submit="registerLoan">
                    <div v-for="(_, index) in newItems" :key="index" class="q-mb-md">
                      <div class="flex">
                        <q-input v-model="newItems[index]" label="Item" filled lazy-rules
                          :rules="[val => !!val || 'Field cannot be empty']" />
                        <q-btn icon="mdi-delete-circle" color="negative" @click="removeItem(index)" flat round />
                      </div>
                    </div>

                    <q-btn label="Adicionar" color="primary" @click="addItem" icon="mdi-plus" class="q-mb-md" />

                    <div class="flex">
                      <q-btn label="Registrar" type="submit" color="positive" icon="mdi-content-save" />
                    </div>
                  </q-form>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-6 bg-light q-pa-md">
              <q-card>
                <q-card-section>
                  <q-input outlined v-model="startCode" type="number" class="q-input" label="Início" />
                  <q-input outlined v-model="pages" type="number" class="q-input" label="Páginas" />
                  <q-btn label="Gerar folha" @click="printCodes(startCode, pages)" type="submit" color="positive"
                    icon="mdi-content-save" />
                </q-card-section>
              </q-card>
            </div>
          </div>

        </q-tab-panel>

        <q-tab-panel name="devolucao">

          <q-dialog v-model="dialog">
            <q-card>
              <q-toolbar>
                <q-avatar>
                  <img src="https://cdn.quasar.dev/logo-v2/svg/logo.svg">
                </q-avatar>

                <q-toolbar-title>
                  <b>Empréstimo</b> {{ selectedId }}
                </q-toolbar-title>

                <q-btn flat round dense icon="close" v-close-popup />
              </q-toolbar>

              <q-card-section>

                <p><b>Solicitante</b>: {{ selectedResponsavel }}</p>
                <p><b>Matrícula</b>: {{ selectedMatricula }}</p>

                <div v-for="(item, index) in loanItems" :key="index" class="q-gutter-md row items-center">
                  <span class="col">
                    {{ getNome(item) }}
                  </span>
                  <div class="col-auto">
                    <q-btn @click="returnItem(item.emprestimo, getPatrOrNome(item), index)" :disable="item.devolvido"
                      label="Devolver" color="primary" />
                  </div>
                  <div v-if="item.devolvido" class="col-auto">
                    {{ item.recebente_nome }} -- {{ formatReturn(item) }}
                  </div>
                </div>
              </q-card-section>

              <q-card-section>
                <q-btn label="Quitar" color="primary" :disable="selectedEncerrado"
                  @click="returnAllItems(selectedId)" />
              </q-card-section>
            </q-card>
          </q-dialog>

          <q-option-group v-model="loanStatus" inline class="q-mb-md" :options="[
            { label: 'Pendentes', value: 'pending' },
            { label: 'Todos', value: 'all' },
          ]" />

          <q-table flat bordered title="Empréstimos" :rows="rows" :columns="columns" :filter=filter
            row-key="identificador" :rows-per-page-options="[50, 100, 150, 0]">

            <template v-slot:top-right>
              <q-input borderless dense debounce="300" v-model="filter" placeholder="Pesquisar">
                <template v-slot:append>
                  <q-icon name="mdi-magnify" />
                </template>
              </q-input>
            </template>

            <template v-slot:body-cell-devolucao="props">
              <q-td :props="props">
                <q-btn label="Visualizar" color="primary"
                  @click="getItems(
                    props.row.identificador,
                    props.row.responsavel_nome,
                    props.row.responsavel_matricula
                  )" />
              </q-td>
            </template>

          </q-table>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </q-page>
</template>

<style>
.q-input {
  padding-top: 10px;
  padding-bottom: 20px;
}
</style>
