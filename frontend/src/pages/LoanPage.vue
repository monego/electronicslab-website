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
const $q = useQuasar();
const notifTimeout = 30;
let allLoans: string;

interface LoanItem {
  name: string;
  returned: boolean;
}

const loanItems = ref<LoanItem[]>([{
  name: '',
  returned: false,
}]);

interface Loan {
  identificador: string;
  responsavel_nome: string;
  funcionario_nome: string;
  local: string;
  retirada: string;
  items: string[];
  devolucao: string;
  statusClass: string;
}

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
  field?: string;
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
    field: 'identificador',
    format: (val: Loan) => `${val}`,
    sortable: true,
  },
  {
    name: 'responsavel',
    align: 'center',
    label: 'Responsável',
    field: 'responsavel',
    format: (val: Loan) => capitalizeEachWord(`${val}`),
    sortable: true,
  },
  {
    name: 'funcionario',
    label: 'Funcionário',
    field: 'funcionario',
    sortable: true,
  },
  {
    name: 'local',
    label: 'Local',
    field: 'local',
  },
  {
    name: 'retirada',
    label: 'Retirada',
    field: 'retirada',
    format: (val: Loan) => format(`${val}`, 'yyyy-MM-dd HH:mm:ss'),
  },
  {
    name: 'devolucao',
    label: 'Devolução',
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
        responsavel: loan.responsavel_nome,
        funcionario: loan.funcionario_nome,
        items: loan.items.map((itemName: string) => ({
          name: itemName,
          returned: false,
        })) as LoanItem[],
        local: loan.local,
        retirada: loan.retirada,
        statusClass: loan.devolucao === null ? 'q-row-active' : 'q-row-inactive',
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
    throw error; // Rethrow the error
  }
}

async function registerLoan() {
  const payload = {
    identificador: loanId.value,
    matricula: matricula.value,
    obs: obs.value,
    items: loanItems.value.map((item) => item.name),
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
    throw error; // Rethrow the error
  }
}

async function returnLoan(id: string) {
  try {
    const response = await (api as AxiosInstance).patch('/controle/emprestimos/byidentifier/', {
      identificador: id,
    });

    if (response.status === 200) {
      $q.notify({
        type: 'positive',
        message: 'Devolvido com successo.',
        timeout: notifTimeout,
      });

      await getLoans();

      return response.data;
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

function addItem() {
  loanItems.value.push({
    name: '',
    returned: false,
  });
}

function removeItem(index: number) {
  loanItems.value.splice(index, 1);
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
                <q-btn color="primary" @click="addItem">Acrescentar equipamento</q-btn>
                <q-list bordered separator>
                  <q-item v-for="(item, index) in loanItems" :key="index">
                    <q-item-section>
                      <q-input v-model="item.name" label="Equipamento"
                      :class="{ 'strikethrough': item.returned }" />
                    </q-item-section>
                    <q-item-section side>
                      <q-btn flat icon="delete" @click="removeItem(index)" />
                    </q-item-section>
                  </q-item>
                </q-list>

                <q-card class="pad">
                  <q-btn @click="registerLoan" color="white" text-color="black" label="Registrar" />
                </q-card>
              </q-card>
            </q-card>
          </q-tab-panel>

          <q-tab-panel name="devolucao">

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
            :row-key="identificador">

              <template v-slot:top-right>
                <q-input borderless dense debounce="300" v-model="filter" placeholder="Pesquisar">
                  <template v-slot:append>
                    <q-icon name="mdi-magnify" />
                  </template>
                </q-input>
              </template>

              <template v-slot:header="props">
                <q-tr :props="props">
                  <q-th auto-width />
                  <q-th v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.label }}
                  </q-th>
                </q-tr>
              </template>

              <template v-slot:body="props">
                <q-tr :props="props">
                  <q-td auto-width>
                    <q-btn size="sm" color="accent" round dense
                    @click="props.expand = !props.expand"
                      :icon="props.expand ? 'remove' : 'add'" />
                  </q-td>
                  <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    <template v-if="col.name === 'devolucao'">
                        <q-btn color="primary" label="Total"
                        @click="returnLoan(props.row.identificador)" />
                    </template>
                    <template v-else>
                      {{ col.value }}
                    </template>
                  </q-td>
                </q-tr>
                <q-tr v-show="props.expand" :props="props">
                  <q-td colspan="100%">
                    <div class="text-left">
                      <li v-for="(item, index) in props.row.items" :key=index>
                        <q-item-section>{{ item.name }}</q-item-section>
                      </li>
                    </div>
                  </q-td>
                </q-tr>
              </template>

            </q-table>
          </q-tab-panel>
        </q-tab-panels>
      </q-card>
    </q-card>
  </q-card>
</template>

<style scoped>
.q-row-inactive {
  background-color: #0000f0; /* Light gray background for rows with null hora_devolucao */
  color: #a0a0a0; /* Gray text color for rows with null hora_devolucao */
}

.q-row-active {
  background-color: #ffffff; /* White background for rows with non-null hora_devolucao */
  color: #000000; /* Black text color for rows with non-null hora_devolucao */
}
</style>
