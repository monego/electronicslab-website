<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { AxiosInstance } from 'axios';
import { axios, api } from 'boot/axios';
import internal from 'stream';
import { getLeadingCommentRanges } from 'typescript';
import { getOverlappingDaysInIntervals } from 'date-fns';

const loanId = ref();
const matricula = ref();
const obs = ref();
const tab = ref('retirada');
const filter = ref<string>();

interface Loan {
  identificador: string;
  responsavel: string;
  funcionario: string;
  local: string;
  retirada: string;
  items: string[];
  devolucao: string;
}

const columns = [
  {
    name: 'identificador',
    required: true,
    label: 'Identificador',
    align: 'left',
    field: (row: Loan) => row.identificador,
    format: (val: Loan) => `${val}`,
    sortable: true,
  },
  { name: 'responsavel', align: 'center', label: 'Responsável', field: 'responsavel', sortable: true },
  { name: 'funcionario', label: 'Funcionário', field: 'funcionario', sortable: true },
  { name: 'local', label: 'Local', field: 'local' },
  { name: 'retirada', label: 'Retirada', field: 'retirada' },
  { name: 'actions', label: 'Ações' },
];

interface LoanItem {
  name: string;
}

const loanItems = ref<LoanItem[]>([
  { name: '' },
]);

const rows = ref<Loan[]>([]);

async function getLoans() {
  try {
    const response = await (api as AxiosInstance).get('/controle/emprestimos');

    if (response.status === 200) {
      console.log(response.data);
      rows.value = response.data.map((loan: Loan) => ({
        identificador: loan.identificador,
        responsavel: loan.responsavel.nome,
        funcionario: loan.funcionario.username,
        items: loan.items,
        local: loan.local,
        retirada: loan.retirada,
      }));
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      console.error(`Axios Error: ${error.message}`);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`); // Formatted JSON
      }
    } else {
      console.error(`Error: ${error.message}`);
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

    if (response.status === 200) {
      console.log("Sucesso");
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      console.error(`Axios Error: ${error.message}`);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`); // Formatted JSON
      }
    } else {
      console.error(`Error: ${error.message}`);
    }
    throw error; // Rethrow the error
  }
}

function addItem() {
  loanItems.value.push({ name: '' });
}

function removeItem(index: number) {
  loanItems.value.splice(index, 1);
}

onMounted(() => {
  getLoans();
});
</script>

<template>
  <q-card class="q-pa-md">
    <q-card class="q-gutter-md">
      <q-card>
        <q-tabs v-model="tab" dense class="text-grey" active-color="primary" indicator-color="primary" align="justify"
          narrow-indicator>
          <q-tab class="text-purple" name="retirada" icon="mdi-arrow-top-right-thin" label="Retirada" />
          <q-tab class="text-orange" name="devolucao" icon="mdi-arrow-bottom-left-thin" label="Devolução" />
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
                      <q-input v-model="item.name" label="Equipamento" />
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
            <q-table flat bordered title="Empréstimos" :rows="rows" :columns="columns" :filter=filter
              row-key="identificador">

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
                    {{ col.value }}
                  </q-td>
                </q-tr>
                <q-tr v-show="props.expand" :props="props">
                  <q-td colspan="100%">
                    <div class="text-left">{{ props.row.items }}.</div>
                  </q-td>
                </q-tr>
              </template>

              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <q-btn color="primary" label="View Details" />
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
.flex-container {
  display: flex;
}

.pad {
  padding: 15px;
}
</style>
