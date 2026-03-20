<template>
    <div>
        <q-input
        outlined
        dense
        v-model="modelValue"
        :label="label"
        class="q-input"
        :error="!exists"
        :error-message="errorMessage"
        @blur="handleBlur"
        @keyup.enter="handleBlur"
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
    </div>

    <q-dialog v-model="prompt" persistent>
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">Verificação</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input filled v-model="nomePessoa" label="Nome" disable readonly class="q-mb-sm" />
          <q-input filled v-model="matriculaPessoa" label="Matrícula" disable readonly class="q-mb-sm" />
          <q-input v-model="emailPessoa" label="Email" outlined dense class="q-mb-sm" />
          <q-input v-model="telefonePessoa" label="Telefone" outlined dense />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="OK" v-close-popup />
          <q-btn flat label="Atualizar" @click="patchPersonData" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

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
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { AxiosError } from 'axios';
import { axios, api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { format, parseISO } from 'date-fns';

const $q = useQuasar();
const notifTimeout = 3000;
const prompt = ref<boolean>(false);

const modelValue = defineModel<string>();

defineOptions({
  name: 'MatriculaButton',
});

defineProps({
  label: {
    type: String,
    default: 'Matrícula',
  },
  errorMessage: {
    type: String,
    default: 'Matrícula não encontrada',
  },
});

interface Student {
  nome: string;
  matricula: string;
  last_access: string | null;
  has_active_loan: boolean;
  has_past_loan: boolean;
}

const exists = ref<boolean>(true);
const nomePessoa = ref<string>('');
const matriculaPessoa = ref<string>('');
const emailPessoa = ref<string>('');
const telefonePessoa = ref<string>('');

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

function formatLastAccess(dateStr: string | null) {
  if (!dateStr) return '';
  return `ultimo registro em ${format(parseISO(dateStr), "dd/MM/yyyy 'às' HH:mm")}`;
}

function getRowClass(student: Student) {
  if (student.has_active_loan) return 'bg-yellow-1';
  if (student.has_past_loan || student.last_access) return 'bg-green-1';
  return '';
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
  modelValue.value = student.matricula;
  showSearchModal.value = false;
  searchName.value = '';
  searchQueryResult.value = [];
  void getPersonData(student.matricula);
}

async function getPersonData(numeroMatricula: string) {
  if (!numeroMatricula) return;
  try {
    const response = await api.get('/root/pessoas', {
      params: {
        matricula: numeroMatricula,
      },
    });

    if (response.status === 200 && response.data.length > 0) {
      nomePessoa.value = response.data[0].nome;
      matriculaPessoa.value = response.data[0].matricula;
      emailPessoa.value = response.data[0].email;
      telefonePessoa.value = response.data[0].telefone;
      exists.value = true;
      prompt.value = true;
    } else {
      exists.value = false;
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        throw error;
      }
    } else {
      throw error;
    }
    throw error;
  }
}

async function patchPersonData() {
  try {
    const response = await api.patch('/root/pessoas/mailphone/', {
      matricula: matriculaPessoa.value,
      email: emailPessoa.value,
      telefone: telefonePessoa.value,
    });

    if (response.status === 200) {
      $q.notify({
        type: 'positive',
        message: 'Cadastro atualizado com sucesso.',
        timeout: notifTimeout,
      });

      return response.data;
    }
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Erro ao atualizar cadastro.',
      timeout: notifTimeout,
    });
  }
  return null;
}

async function handleBlur() {
  if (modelValue.value) {
    await getPersonData(modelValue.value);
  }
}
</script>
