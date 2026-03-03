<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { api } from 'boot/axios';
import { format, parseISO } from 'date-fns';
import { useQuasar } from 'quasar';
import MatriculaButton from 'components/MatriculaButton.vue';

const $q = useQuasar();

// State
const tab = ref('consultar');
const loanStatus = ref<'pending' | 'all'>('pending');
const filter = ref('');
const loadingLoans = ref(false);
const checkingId = ref(false);

const pagination = ref({
  sortBy: 'data',
  descending: true,
  page: 1,
  rowsPerPage: 20
});

// Form State
const loanId = ref<string>('');
const matricula = ref<string>('');
const obs = ref<string>('');
const newItems = ref<string[]>(['']);
const startCode = ref<number | undefined>();
const pagesCount = ref<number | undefined>();

// Validation
const idExists = ref(false);

interface Loan {
  identificador: string;
  responsavel_nome: string;
  responsavel_matricula: string;
  funcionario_nome: string;
  items_nomes: string;
  local: string;
  retirada: string;
  encerrado: boolean;
}

interface LoanItem {
  nome: string;
  equipamento_nome?: string;
  equipamento_patrimonio?: string;
  emprestimo: string;
  recebente_nome: string;
  devolvido: boolean;
  devolucao: string;
}

const rows = ref<Loan[]>([]);
const itemsMap = ref<Record<string, { items: LoanItem[], loading: boolean }>>({});
const equipmentLookup = ref<Record<string, string>>({});

// Utilities
function capitalizeEachWord(str: string): string {
  if (!str) return '';
  return str
    .split(' ')
    .filter(w => w)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

const columns = [
  { name: 'identificador', label: 'ID', align: 'left' as const, field: 'identificador', sortable: true },
  {
    name: 'responsavel',
    label: 'Responsável',
    align: 'left' as const,
    field: 'responsavel_nome',
    format: (val: string) => capitalizeEachWord(val),
    sortable: true
  },
  // items_summary is kept for filtering but will be hidden in the template
  { name: 'items_summary', label: 'Itens', align: 'left' as const, field: 'items_nomes', classes: 'hidden', headerClasses: 'hidden' },
  { name: 'funcionario', label: 'Registrado por', align: 'left' as const, field: 'funcionario_nome' },
  {
    name: 'data',
    label: 'Data Retirada',
    align: 'center' as const,
    field: 'retirada',
    format: (val: string) => format(parseISO(val), 'dd/MM/yyyy HH:mm'),
    sortable: true
  },
  { name: 'quem_recebeu', label: 'Devolvido para', align: 'left' as const, field: 'quem_recebeu' },
  { name: 'status', label: 'Status', align: 'center' as const, field: 'encerrado' },
  { name: 'acoes', label: '', align: 'right' as const, field: 'acoes' }
];

// Actions
async function getLoans() {
  loadingLoans.value = true;
  try {
    const query = loanStatus.value === 'all' ? '?all=true' : '';
    const response = await api.get(`/controle/emprestimos/${query}`);
    if (response.status === 200) {
      rows.value = response.data;
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar empréstimos.' });
  } finally {
    loadingLoans.value = false;
  }
}

async function fetchLoanItems(identifier: string) {
  const currentEntry = itemsMap.value[identifier];
  if (currentEntry && currentEntry.items.length > 0) return;

  itemsMap.value[identifier] = { items: [], loading: true };
  try {
    const response = await api.get('/controle/items/', { params: { emprestimo: identifier } });
    if (response.status === 200) {
      itemsMap.value[identifier] = { items: response.data, loading: false };
    }
  } catch {
    $q.notify({ type: 'negative', message: `Erro ao carregar itens do empréstimo ${identifier}.` });
    itemsMap.value[identifier] = { items: [], loading: false };
  }
}

async function toggleExpand(slotProps: { expand: boolean, row: Loan }) {
  slotProps.expand = !slotProps.expand;
  if (slotProps.expand) {
    await fetchLoanItems(slotProps.row.identificador);
  }
}

async function returnSingleItem(loanIdentifier: string, itemName: string) {
  try {
    const response = await api.patch('/controle/items/return/', {
      emprestimo: loanIdentifier,
      nome: itemName,
    });

    if (response.status === 200) {
      $q.notify({ type: 'positive', message: 'Item devolvido.' });
      if (itemsMap.value[loanIdentifier]) {
        itemsMap.value[loanIdentifier].items = [];
      }
      await fetchLoanItems(loanIdentifier);
      await getLoans();
    }
  } catch (error: unknown) {
    const errorWithResponse = error as { response?: { data?: { detail?: string } } };
    const msg = errorWithResponse.response?.data?.detail || 'Erro ao devolver item.';
    $q.notify({ type: 'negative', message: msg });
  }
}

function returnAllItems(loanIdentifier: string) {
  $q.dialog({
    title: 'Finalizar Empréstimo',
    message: `Deseja quitar todos os itens do empréstimo ${loanIdentifier}?`,
    cancel: true,
    persistent: true
  }).onOk(() => {
    void (async () => {
      try {
        const response = await api.patch('/controle/emprestimos/byidentifier/', {
          identificador: loanIdentifier,
        });

        if (response.status === 200) {
          $q.notify({ type: 'positive', message: 'Empréstimo finalizado com sucesso.' });
          if (itemsMap.value[loanIdentifier]) {
            itemsMap.value[loanIdentifier].items = [];
          }
          await getLoans();
        }
      } catch {
        $q.notify({ type: 'negative', message: 'Erro ao finalizar empréstimo.' });
      }
    })();
  });
}

// Form Actions
function addItemInput() { newItems.value.push(''); }
function removeItemInput(index: number) {
  const val = newItems.value[index];
  if (val) delete equipmentLookup.value[val];
  newItems.value.splice(index, 1);
}

async function lookupEquipment(val: string) {
  if (!val || val.length < 2) return;
  if (equipmentLookup.value[val]) return;

  try {
    const response = await api.get('/controle/equipamento/', { params: { patrimonio: val } });
    if (response.data && response.data.length > 0) {
      equipmentLookup.value[val] = response.data[0].nome;
    }
  } catch { /* Silent fail */ }
}

async function checkIdAvailability() {
  if (!loanId.value) {
    idExists.value = false;
    return;
  }
  checkingId.value = true;
  try {
    const response = await api.get('/controle/emprestimos/', {
      params: { identificador: loanId.value, all: 'true' }
    });
    idExists.value = response.data.length > 0;
  } catch { /* Silent fail */ } finally {
    checkingId.value = false;
  }
}

async function registerLoan() {
  if (idExists.value || !loanId.value || !matricula.value) {
    if (idExists.value) $q.notify({ type: 'warning', message: 'Identificador já cadastrado.' });
    return;
  }

  const payload = {
    identificador: loanId.value,
    matricula: matricula.value,
    obs: obs.value,
    items: newItems.value.filter(i => i.trim() !== ''),
  };

  try {
    const response = await api.post('/controle/emprestimos/', payload);
    if (response.status === 201) {
      $q.notify({ type: 'positive', message: 'Empréstimo registrado!' });
      resetForm();
      tab.value = 'consultar';
      await getLoans();
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao registrar empréstimo.' });
  }
}

function resetForm() {
  loanId.value = '';
  matricula.value = '';
  obs.value = '';
  newItems.value = [''];
  idExists.value = false;
  equipmentLookup.value = {};
}

async function printCodes() {
  if (!startCode.value || !pagesCount.value) return;
  try {
    const response = await api.get('/controle/emprestimos/printsheet/', {
      params: { inicio: startCode.value, paginas: pagesCount.value },
      responseType: 'blob',
    });
    const blob = response.data;
    const fileURL = URL.createObjectURL(blob);
    window.open(fileURL, '_blank');
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao gerar folha de códigos.' });
  }
}

function getDisplayItemName(item: LoanItem) {
  return item.equipamento_nome
    ? `${item.equipamento_nome} (${item.equipamento_patrimonio})`
    : item.nome;
}

function getItemIdentifier(item: LoanItem) {
  return item.equipamento_patrimonio || item.nome;
}

watch(loanStatus, () => getLoans());
onMounted(() => getLoans());

</script>

<template>
  <q-page class="q-pa-md bg-grey-1">
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-card flat bordered class="shadow-2">
          <q-tabs
            v-model="tab"
            dense
            active-color="primary"
            indicator-color="primary"
            align="left"
            narrow-indicator
            class="text-grey-7 bg-white"
          >
            <q-tab name="consultar" icon="search" label="Consultar" />
            <q-tab name="cadastrar" icon="add_circle" label="Novo Empréstimo" />
            <q-tab name="codigos" icon="print" label="Gerar Códigos" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="tab" animated class="bg-transparent">
            <!-- ABA CONSULTAR -->
            <q-tab-panel name="consultar" class="q-pa-none">
              <q-table
                flat
                :rows="rows"
                :columns="columns"
                :filter="filter"
                row-key="identificador"
                :loading="loadingLoans"
                v-model:pagination="pagination"
                class="no-shadow"
              >
                <template v-slot:top>
                  <div class="row full-width items-center q-gutter-md">
                    <div class="text-h6 text-grey-8">Histórico de Empréstimos</div>
                    <q-space />
                    <q-btn-toggle
                      v-model="loanStatus"
                      flat
                      toggle-color="primary"
                      :options="[
                        { label: 'Pendentes', value: 'pending' },
                        { label: 'Todos', value: 'all' }
                      ]"
                    />
                    <q-input
                      outlined dense
                      v-model="filter"
                      placeholder="Pesquisar..."
                      class="bg-white"
                    >
                      <template v-slot:append>
                        <q-icon name="search" />
                      </template>
                    </q-input>
                  </div>
                </template>

                <template v-slot:header="slotProps">
                  <q-tr :props="slotProps">
                    <q-th auto-width />
                    <q-th v-for="col in slotProps.cols" :key="col.name" :props="slotProps">
                      {{ col.label }}
                    </q-th>
                  </q-tr>
                </template>

                <template v-slot:body="slotProps">
                  <q-tr :props="slotProps" :class="slotProps.row.encerrado ? 'text-grey-5' : ''">
                    <q-td auto-width>
                      <q-btn
                        size="sm" color="primary" round flat
                        :icon="slotProps.expand ? 'remove' : 'add'"
                        @click="toggleExpand(slotProps)"
                      />
                    </q-td>
                    <q-td v-for="col in slotProps.cols" :key="col.name" :props="slotProps">
                      <template v-if="col.name === 'status'">
                        <q-chip
                          dense
                          :color="slotProps.row.encerrado ? 'grey-4' : 'warning'"
                          :text-color="slotProps.row.encerrado ? 'grey-7' : 'white'"
                          :icon="slotProps.row.encerrado ? 'check_circle' : 'schedule'"
                        >
                          {{ slotProps.row.encerrado ? 'Devolvido' : 'Pendente' }}
                        </q-chip>
                      </template>
                      <template v-else-if="col.name === 'acoes'">
                        <q-btn
                          v-if="!slotProps.row.encerrado"
                          flat round dense
                          color="positive" icon="done_all"
                          @click="returnAllItems(slotProps.row.identificador)"
                        >
                          <q-tooltip>Quitar Empréstimo</q-tooltip>
                        </q-btn>
                      </template>
                      <template v-else>
                        {{ col.value }}
                      </template>
                    </q-td>
                  </q-tr>
                  <q-tr v-show="slotProps.expand" :props="slotProps">
                    <q-td colspan="100%" class="bg-grey-1 q-pa-md">
                      <div class="row items-center q-mb-sm">
                        <div class="text-subtitle2 text-primary">Itens do Empréstimo</div>
                        <q-space />
                        <div class="text-caption text-grey-7">Local: {{ slotProps.row.local || 'Não informado' }}</div>
                      </div>

                      <q-list bordered separator dense class="bg-white rounded-borders">
                        <q-item v-if="itemsMap[slotProps.row.identificador]?.loading" class="q-pa-md justify-center">
                          <q-spinner color="primary" size="2em" />
                        </q-item>

                        <q-item
                          v-for="(item, idx) in itemsMap[slotProps.row.identificador]?.items"
                          :key="idx"
                          :class="item.devolvido ? 'bg-grey-1 text-grey-6' : ''"
                        >
                          <q-item-section avatar>
                            <q-icon
                              :name="item.devolvido ? 'check_circle' : 'circle'"
                              :color="item.devolvido ? 'positive' : 'warning'"
                              size="18px"
                            />
                          </q-item-section>
                          <q-item-section>
                            <q-item-label>{{ getDisplayItemName(item) }}</q-item-label>
                            <q-item-label v-if="item.devolvido" caption>
                              Devolvido em {{ item.devolucao ? format(parseISO(item.devolucao), 'dd/MM/yyyy HH:mm') : '---' }} para {{ item.recebente_nome || 'Sistema' }}
                            </q-item-label>
                          </q-item-section>
                          <q-item-section side v-if="!item.devolvido">
                            <q-btn
                              flat round dense
                              color="primary" icon="mdi-reply"
                              @click="returnSingleItem(slotProps.row.identificador, getItemIdentifier(item))"
                            >
                              <q-tooltip>Devolver Item</q-tooltip>
                            </q-btn>
                          </q-item-section>
                        </q-item>

                        <q-item v-if="!itemsMap[slotProps.row.identificador]?.loading && itemsMap[slotProps.row.identificador]?.items.length === 0">
                          <q-item-section class="text-italic text-grey text-center">Nenhum item encontrado.</q-item-section>
                        </q-item>
                      </q-list>
                    </q-td>
                  </q-tr>
                </template>
              </q-table>
            </q-tab-panel>

            <!-- ABA CADASTRAR -->
            <q-tab-panel name="cadastrar" class="q-pa-lg">
              <div class="row q-col-gutter-lg justify-center">
                <!-- Coluna Formulário -->
                <div class="col-12 col-md-7">
                  <q-card flat bordered class="q-pa-md bg-white">
                    <div class="text-h6 q-mb-md flex items-center">
                      <q-icon name="mdi-tray-arrow-up" color="primary" class="q-mr-sm" />
                      Novo Empréstimo
                    </div>

                    <div class="row q-col-gutter-md">
                      <div class="col-12 col-sm-6">
                        <q-input
                          v-model="loanId"
                          label="Identificador do Empréstimo"
                          outlined dense
                          :error="idExists"
                          error-message="ID já em uso em outro empréstimo"
                          @blur="checkIdAvailability"
                          @update:model-value="idExists = false"
                          :loading="checkingId"
                        >
                          <template v-slot:append>
                            <q-icon v-if="loanId && !idExists && !checkingId" name="check" color="positive" />
                          </template>
                        </q-input>
                      </div>
                      <div class="col-12 col-sm-6">
                        <MatriculaButton v-model="matricula" />
                      </div>
                      <div class="col-12">
                        <q-input
                          v-model="obs"
                          label="Observação / Local de Uso"
                          outlined dense
                          maxlength="20"
                          hint="Ex: Laboratório 3"
                        />
                      </div>

                      <div class="col-12 q-mt-sm">
                        <div class="text-subtitle2 q-mb-sm text-grey-8">Itens a serem emprestados:</div>
                        <div class="q-gutter-y-sm">
                          <div v-for="(_, index) in newItems" :key="index">
                            <div class="row q-col-gutter-sm items-center">
                              <div class="col">
                                <q-input
                                  v-model="newItems[index]"
                                  label="Nome do Item ou Patrimônio"
                                  outlined dense
                                  bg-color="blue-grey-1"
                                  @blur="newItems[index] && lookupEquipment(newItems[index]!)"
                                />
                              </div>
                              <div class="col-auto">
                                <q-btn flat round dense color="negative" icon="delete" @click="removeItemInput(index)" :disable="newItems.length === 1" />
                              </div>
                            </div>
                            <div v-if="newItems[index] && equipmentLookup[newItems[index]!]" class="text-caption text-primary q-ml-sm q-mt-xs">
                              <q-icon name="check" /> {{ equipmentLookup[newItems[index]!] }}
                            </div>
                          </div>
                          <q-btn
                            flat dense color="primary"
                            icon="add_circle" label="Adicionar outro item"
                            @click="addItemInput"
                            class="q-mt-sm"
                          />
                        </div>
                      </div>
                    </div>

                    <div class="flex justify-end q-mt-xl">
                      <q-btn flat label="Limpar" color="grey" @click="resetForm" class="q-mr-sm" />
                      <q-btn label="Registrar Empréstimo" color="primary" rounded class="q-px-lg" @click="registerLoan" />
                    </div>
                  </q-card>
                </div>
              </div>
            </q-tab-panel>

            <!-- ABA CODIGOS -->
            <q-tab-panel name="codigos" class="q-pa-lg">
              <div class="row justify-center">
                <div class="col-12 col-md-6">
                  <q-card flat bordered class="bg-white q-pa-md shadow-2">
                    <div class="text-h6 q-mb-md flex items-center">
                      <q-icon name="print" color="primary" class="q-mr-sm" />
                      Gerar Folha de Códigos
                    </div>
                    <p class="text-body2 text-grey-7 q-mb-lg">Gere uma folha PDF com novos códigos de barras para identificadores de empréstimo.</p>

                    <div class="q-gutter-y-md">
                      <q-input v-model.number="startCode" type="number" label="Código Inicial" outlined dense bg-color="blue-grey-1" />
                      <q-input v-model.number="pagesCount" type="number" label="Total de Páginas" outlined dense bg-color="blue-grey-1" />

                      <div class="row q-mt-lg">
                        <q-btn
                          label="Abrir PDF"
                          color="primary"
                          class="full-width q-py-sm"
                          icon="open_in_new"
                          @click="printCodes"
                        />
                      </div>
                    </div>
                  </q-card>
                </div>
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<style scoped>
.modern-table {
  background: transparent;
}
</style>
