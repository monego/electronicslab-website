<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { format, parseISO } from 'date-fns';
import { api } from 'boot/axios';
import MatriculaButton from 'components/MatriculaButton.vue';

const $q = useQuasar();

const sala = ref<string | null>(null);
const matricula = ref<string>('');
const tab = ref<string>('entrada');
const options = ref<{ label: string; value: string }[]>([]);
const rows = ref<Row[]>([]);
const selected = ref<Row[]>([]);
const loading = ref<boolean>(false);

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
                      <MatriculaButton v-model="matricula" />

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
  </q-page>
</template>


<style scoped>
.modern-table {
  background: transparent;
}
</style>
