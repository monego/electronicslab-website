<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { format, parseISO } from 'date-fns';
import { api } from 'boot/axios';

const $q = useQuasar();

interface Option {
  label: string;
  value: string;
}

const sala = ref<string | null>(null);
const matricula = ref<string>('');
const tab = ref<string>('entrada');
const options = ref<Option[]>([]);
const rows = ref<Row[]>([]);
const selected = ref<Row[]>([]);
const loading = ref<boolean>(false);
const studentName = ref<string>('');
const searchingStudent = ref<boolean>(false);

interface Student {
  nome: string;
  matricula: string;
  last_access: string | null;
}

const showSearchModal = ref(false);
const searchName = ref('');
const searchQueryResult = ref<Student[]>([]);
const searchingByName = ref(false);

function formatLastAccess(dateStr: string | null) {
  if (!dateStr) return '';
  return `ultimo registro em ${format(parseISO(dateStr), "dd/MM/yyyy 'às' HH:mm")}`;
}

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
  studentName.value = student.nome;
  showSearchModal.value = false;
  searchName.value = '';
  searchQueryResult.value = [];
}

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

async function getSalas() {
  try {
    const response = await api.get('/root/salas/');
    if (response.status === 200) {
      options.value = response.data.map((item: { nome: string, numero: string }) => ({
        label: `[${item.numero}] ${item.nome}`,
        value: item.numero,
      }));
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar salas.' });
  }
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

async function lookupStudent() {
  if (!matricula.value) {
    studentName.value = '';
    return;
  }
  searchingStudent.value = true;
  try {
    const response = await api.get('/root/pessoas/', { params: { matricula: matricula.value } });
    if (response.data && response.data.length > 0) {
      studentName.value = response.data[0].nome;
    } else {
      studentName.value = 'Aluno não encontrado';
    }
  } catch {
    studentName.value = 'Erro ao buscar aluno';
  } finally {
    searchingStudent.value = false;
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
      $q.notify({ type: 'positive', message: 'Acesso registrado com sucesso.' });
      matricula.value = '';
      studentName.value = '';
      await getRegistered();
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
                      <q-input
                        v-model="matricula"
                        label="Matrícula"
                        outlined
                        dense
                        @blur="lookupStudent"
                        @keyup.enter="lookupStudent"
                        :loading="searchingStudent"
                        :hint="studentName"
                        hide-bottom-space
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

                      <q-select
                        v-model="sala"
                        :options="options"
                        label="Sala de Destino"
                        outlined
                        dense
                        emit-value
                        map-options
                      >
                        <template v-slot:prepend>
                          <q-icon name="meeting_room" />
                        </template>
                      </q-select>

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
                :class="props.row.last_access ? 'bg-green-1' : ''"
              >
                <q-td key="nome" :props="props">
                  {{ capitalizeEachWord(props.row.nome) }}
                  <q-tooltip v-if="props.row.last_access">
                    {{ formatLastAccess(props.row.last_access) }}
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
</style>
