<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useQuasar } from 'quasar';
import { format, parseISO, isValid } from 'date-fns';
import { api } from 'boot/axios';

const $q = useQuasar();

const registrationStatus = ref<{ name: string; sala: string } | null>(null);

const sala = ref<string | null>(null);
const matricula = ref<string>('');
const tab = ref<string>('entrada');
const options = ref<{ label: string; value: string; andar: number; numero: string }[]>([]);
const rows = ref<Row[]>([]);
const selected = ref<Row[]>([]);
const loading = ref<boolean>(false);
const loadingStudent = ref<boolean>(false);
const foundStudent = ref<{ nome: string; last_access: string | null; last_room_numero: string | null } | null>(null);

interface Student {
  nome: string;
  matricula: string;
  last_access: string | null;
  last_room_numero: string | null;
  has_active_loan: boolean;
  has_past_loan: boolean;
}

const showSearchModal = ref(false);
const searchName = ref('');
const searchQueryResult = ref<Student[]>([]);
const searchingByName = ref(false);

const searchColumns = [
  {
    name: 'nome',
    label: 'Nome',
    field: 'nome',
    align: 'left' as const,
    format: (val: string) => capitalizeEachWord(val),
    sortable: true
  },
  { name: 'matricula', label: 'Matrícula', field: 'matricula', align: 'left' as const, sortable: true },
];

function capitalizeEachWord(str: string): string {
  if (!str) return '';
  return str
    .split(' ')
    .filter(w => w)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

interface Row {
  id: number;
  pessoa_nome: string;
  pessoa_matricula: string;
  sala_numero: string;
  hora_entrada: string;
}

const columns = [
  {
    name: 'nome',
    required: true,
    label: 'Nome',
    align: 'left' as const,
    field: (row: Row) => row.pessoa_nome,
    format: (val: string) => capitalizeEachWord(val),
    sortable: true,
  },
  {
    name: 'matricula',
    required: true,
    label: 'Matrícula',
    align: 'left' as const,
    field: (row: Row) => row.pessoa_matricula,
    sortable: true,
  },
  {
    name: 'sala',
    required: true,
    label: 'Sala',
    align: 'center' as const,
    field: (row: Row) => row.sala_numero,
    sortable: true,
  },
  {
    name: 'entrada',
    required: true,
    label: 'Horário de Entrada',
    align: 'center' as const,
    field: (row: Row) => row.hora_entrada,
    format: (val: string) => (val ? format(parseISO(val), 'dd/MM/yyyy HH:mm:ss') : '-'),
    sortable: true,
  },
  {
    name: 'acoes',
    label: 'Ações',
    align: 'center' as const,
    field: 'acoes'
  }
];

const salasAndar1 = computed(() => options.value.filter(s => s.andar === 1));
const salasAndar2 = computed(() => options.value.filter(s => s.andar === 2));

async function getSalas() {
  try {
    const response = await api.get('/root/salas/');
    if (response.status === 200) {
      options.value = response.data.map((item: { nome: string, numero: string, andar: number }) => ({
        label: `[${item.numero}] ${item.nome}`,
        value: item.numero,
        andar: item.andar,
        numero: item.numero
      }));
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar salas.' });
  }
}

let debounceTimeout: ReturnType<typeof setTimeout> | null = null;
function debounceMatricula() {
  if (debounceTimeout) clearTimeout(debounceTimeout);
  foundStudent.value = null;
  if (!matricula.value) return;
  
  debounceTimeout = setTimeout(() => {
    void validateMatricula();
  }, 500);
}

async function validateMatricula() {
  if (!matricula.value) return;
  loadingStudent.value = true;
  try {
    const response = await api.get('/root/pessoas/', { params: { matricula: matricula.value } });
    if (response.status === 200 && response.data.length > 0) {
      foundStudent.value = response.data[0];
      if (foundStudent.value?.last_room_numero) {
        sala.value = foundStudent.value.last_room_numero;
      }
    }
  } catch {
    // Fail silently or notify
  } finally {
    loadingStudent.value = false;
  }
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null;
function debounceSearch() {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    void performSearch();
  }, 500);
}

async function performSearch() {
  if (!searchName.value || searchName.value.length < 3) {
    searchQueryResult.value = [];
    return;
  }
  searchingByName.value = true;
  try {
    const response = await api.get('/root/pessoas/', { params: { nome: searchName.value } });
    searchQueryResult.value = response.data;
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar alunos.' });
  } finally {
    searchingByName.value = false;
  }
}

function selectStudent(student: Student) {
  matricula.value = student.matricula;
  showSearchModal.value = false;
  searchName.value = '';
  searchQueryResult.value = [];
  void validateMatricula();
}

function getRowClass(student: Student) {
  if (student.has_active_loan) return 'bg-yellow-1';
  if (student.has_past_loan || student.last_access) return 'bg-green-1';
  return '';
}

function formatLastAccess(dateStr: string | null) {
  if (!dateStr) return 'nunca';
  const date = parseISO(dateStr);
  if (!isValid(date)) return 'nunca';
  return format(date, "dd/MM/yyyy 'às' HH:mm");
}

async function getRegistered() {
  loading.value = true;
  try {
    const response = await api.get('/controle/registros/');
    if (response.status === 200) {
      rows.value = response.data;
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao carregar registros de acesso.' });
  } finally {
    loading.value = false;
  }
}

async function registerAccess() {
  if (!matricula.value || !sala.value) {
    $q.notify({ type: 'warning', message: 'Preencha a matrícula e a sala.' });
    return;
  }

  const payload = {
    matricula: matricula.value,
    sala: sala.value,
  };

  try {
    const response = await api.post('/controle/registros/', payload);
    if (response.status === 201) {
      registrationStatus.value = {
        name: foundStudent.value?.nome || matricula.value,
        sala: sala.value
      };
      
      $q.notify({ type: 'positive', message: 'Acesso registrado com sucesso.' });
      
      // Clear fields
      matricula.value = '';
      sala.value = null;
      foundStudent.value = null;
      
      await getRegistered();
      
      // Auto-hide status after 5s
      setTimeout(() => {
        registrationStatus.value = null;
      }, 5000);
    }
  } catch (error: unknown) {
    const axiosError = error as { response?: { data?: { detail?: string } } };
    const detail = axiosError.response?.data?.detail || 'Erro ao registrar acesso.';
    $q.notify({ type: 'negative', message: detail });
  }
}

async function releaseStudent(matriculaToRelease: string) {
  try {
    const response = await api.patch('/controle/registros/bymatricula/', {
      matricula: matriculaToRelease,
    });
    if (response.status === 200) {
      return true;
    }
  } catch {
    return false;
  }
  return false;
}

async function releaseSelected() {
  if (selected.value.length === 0) return;

  try {
    $q.loading.show({ message: 'Liberando acessos...' });
    const results = await Promise.all(
      selected.value.map(s => releaseStudent(s.pessoa_matricula))
    );

    const successCount = results.filter(r => r).length;
    if (successCount > 0) {
      $q.notify({ type: 'positive', message: `${successCount} aluno(s) liberado(s).` });
    }
  } finally {
    $q.loading.hide();
    selected.value = [];
    await getRegistered();
  }
}

async function handleSingleRelease(matriculaToRelease: string) {
  const success = await releaseStudent(matriculaToRelease);
  if (success) {
    await getRegistered();
  }
}

onMounted(async () => {
  await getSalas();
  await getRegistered();
});
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
            <q-tab name="entrada" icon="mdi-login" label="Entrada" />
            <q-tab name="saida" icon="mdi-logout" label="Saída" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="tab" animated class="bg-transparent">
            <!-- ABA ENTRADA -->
            <q-tab-panel name="entrada" class="q-pa-lg">
              <div class="row justify-center">
                <div class="col-12 col-md-6">
                  <q-card flat bordered class="q-pa-md bg-white">
                    <div class="text-h6 q-mb-md flex items-center">
                      <q-icon name="mdi-door-open" color="primary" class="q-mr-sm" />
                       Novo Acesso
                    </div>

                    <div class="q-gutter-y-md">
                      <div v-if="registrationStatus" class="q-mb-md q-pa-sm bg-blue-1 text-blue-9 rounded-borders text-center text-weight-bold animate-fade">
                        {{ capitalizeEachWord(registrationStatus.name) }} - Entrada registrada na sala {{ registrationStatus.sala }}
                      </div>

                      <q-input
                        v-model="matricula"
                        label="Matrícula"
                        outlined
                        dense
                        @update:model-value="debounceMatricula"
                        :loading="loadingStudent"
                        autofocus
                      >
                        <template v-slot:prepend>
                          <q-icon name="mdi-account-card" />
                        </template>
                        <template v-slot:append>
                          <q-btn round dense flat icon="search" @click="showSearchModal = true">
                            <q-tooltip>Buscar por Nome</q-tooltip>
                          </q-btn>
                        </template>
                      </q-input>

                      <div v-if="foundStudent" class="q-pa-sm rounded-borders bg-green-1 text-green-9 flex items-center shadow-1 animate-scale">
                        <q-icon name="check_circle" class="q-mr-sm" size="sm" />
                        <div>
                          <div class="text-weight-bold text-uppercase">{{ foundStudent.nome }}</div>
                          <div class="text-caption">último registro em {{ formatLastAccess(foundStudent.last_access) }}</div>
                        </div>
                      </div>

                      <div>
                        <div class="text-subtitle2 q-mb-sm text-grey-8">Sala de Destino</div>
                        <div class="row q-col-gutter-sm">
                          <div class="col-6">
                            <div class="text-caption text-grey-6 q-mb-xs text-center text-weight-bold">1° ANDAR</div>
                            <div class="row q-col-gutter-xs">
                              <div v-for="s in salasAndar1" :key="s.value" class="col-6">
                                <q-btn
                                  :label="s.numero"
                                  :color="sala === s.value ? 'primary' : 'white'"
                                  :text-color="sala === s.value ? 'white' : 'grey-9'"
                                  unelevated
                                  dense
                                  rounded
                                  @click="sala = s.value"
                                  class="full-width border-grey"
                                  :class="{ 'shadow-2': sala === s.value }"
                                />
                              </div>
                            </div>
                          </div>
                          <div class="col-6">
                            <div class="text-caption text-grey-6 q-mb-xs text-center text-weight-bold">2° ANDAR</div>
                            <div class="row q-col-gutter-xs">
                              <div v-for="s in salasAndar2" :key="s.value" class="col-6">
                                <q-btn
                                  :label="s.numero"
                                  :color="sala === s.value ? 'primary' : 'white'"
                                  :text-color="sala === s.value ? 'white' : 'grey-9'"
                                  unelevated
                                  dense
                                  rounded
                                  @click="sala = s.value"
                                  class="full-width border-grey"
                                  :class="{ 'shadow-2': sala === s.value }"
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <q-btn
                        label="Registrar Entrada"
                        color="primary"
                        icon="mdi-check-circle"
                        class="full-width q-py-sm"
                        rounded
                        @click="registerAccess"
                      />
                    </div>
                  </q-card>
                </div>
              </div>
            </q-tab-panel>

            <!-- ABA SAÍDA -->
            <q-tab-panel name="saida" class="q-pa-none">
              <q-table
                flat
                :rows="rows"
                :columns="columns"
                row-key="id"
                selection="multiple"
                v-model:selected="selected"
                :loading="loading"
                :pagination="{ rowsPerPage: 10 }"
                class="no-shadow"
                no-data-label="Ninguém nas salas no momento"
              >
                <template v-slot:top-left>
                  <div class="text-h6 text-grey-8">Alunos em Estágio / Aula</div>
                </template>

                <template v-slot:body-cell-nome="props">
                  <q-td :props="props">
                    <div class="text-weight-bold text-primary">{{ props.value }}</div>
                  </q-td>
                </template>

                <template v-slot:body-cell-acoes="props">
                  <q-td :props="props" class="text-center">
                    <q-btn
                      flat
                      round
                      dense
                      color="negative"
                      icon="mdi-logout-variant"
                      @click="handleSingleRelease(props.row.pessoa_matricula)"
                    >
                      <q-tooltip>Registrar Saída</q-tooltip>
                    </q-btn>
                  </q-td>
                </template>

                <template v-slot:no-data="{ icon, message, filter }">
                  <div class="full-width row flex-center q-pa-xl text-grey-6 q-gutter-sm">
                    <q-icon :name="filter ? 'filter_list_off' : icon" size="48px" />
                    <div class="text-h6">{{ message }}</div>
                  </div>
                </template>
              </q-table>

              <!-- Botão de Saída Centralizado abaixo da tabela -->
              <div class="row justify-center q-pa-md">
                <q-btn
                  color="negative"
                  icon="mdi-logout-variant"
                  label="Registrar Saída"
                  rounded
                  size="lg"
                  class="q-px-xl"
                  :disable="selected.length === 0"
                  @click="releaseSelected"
                />
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>

    <!-- Modal de Busca por Nome -->
    <q-dialog v-model="showSearchModal">
      <q-card style="min-width: 400px; max-width: 90vw;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Buscar por Nome</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="searchName"
            label="Digite o nome (mín. 3 caracteres)"
            outlined
            dense
            autofocus
            @update:model-value="debounceSearch"
            :loading="searchingByName"
          >
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-table
            :rows="searchQueryResult"
            :columns="searchColumns"
            row-key="matricula"
            flat
            bordered
            dense
            :pagination="{ rowsPerPage: 10 }"
            hide-pagination
            no-data-label="Nenhum resultado encontrado"
          >
            <template v-slot:body="props">
              <q-tr
                :props="props"
                @click="selectStudent(props.row)"
                class="cursor-pointer"
                :class="getRowClass(props.row)"
              >
                <q-td key="nome" :props="props">
                  {{ capitalizeEachWord(props.row.nome) }}
                  <q-tooltip v-if="props.row.last_access">
                    último registro em {{ formatLastAccess(props.row.last_access) }}
                  </q-tooltip>
                </q-td>
                <q-td key="matricula" :props="props">
                  {{ props.row.matricula }}
                </q-td>
              </q-tr>
            </template>
          </q-table>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>


<style scoped>
.modern-table {
  background: transparent;
}

.border-grey {
  border: 1px solid #e0e0e0;
}

.animate-scale {
  animation: scale-up 0.3s ease-out;
}

.animate-fade {
  animation: fade-in 0.5s ease-out;
}

@keyframes scale-up {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
