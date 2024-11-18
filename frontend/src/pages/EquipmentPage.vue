<script setup lang="ts">
import { AxiosInstance, AxiosError } from 'axios';
import { useQuasar } from 'quasar';
import { api, axios } from 'boot/axios';
import { ref, onMounted } from 'vue';
import { format } from 'date-fns';

// Data properties
const tab = ref('consultar');

const showError = ref(false);
const errorMessage = ref<string>('');
const descManutencao = ref<string>('');
const showDialog = ref<boolean>(false);
const $q = useQuasar();
const notifTimeout = 30;

function displayError(message: string) {
  errorMessage.value = message;
  showError.value = true;
}

interface Row {
  nome: string,
  patrimonio: string,
  sala_numero: string,
  defeito: boolean,
  num_manutencao: number,
  num_emprestimo: number,
  foto: string,
  manual: string,
}

type ColumnType = {
  name: string;
  label: string;
  align?: 'left' | 'right' | 'center';
  field: string | ((row: Row) => string) | ((row: Row) => boolean) | ((row: Row) => number);
  required?: boolean;
  format?: (val: string) => string;
  sortable?: boolean;
};

const search = ref('');
const columns: ColumnType[] = [
  {
    name: 'nome',
    label: 'Nome',
    align: 'left',
    field: (row: Row) => row.nome,
    required: true,
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'patrimonio',
    label: 'Patrimônio',
    align: 'center',
    field: (row: Row) => row.patrimonio,
  },
  {
    name: 'sala',
    label: 'Sala',
    align: 'center',
    field: (row: Row) => row.sala_numero,
  },
  {
    name: 'defeito',
    label: 'Defeito',
    align: 'center',
    field: (row: Row) => row.defeito,
    format: (val: string) => (val ? 'Sim' : 'Não'),
  },
  {
    name: 'manutencao',
    label: 'Manutenções',
    align: 'center',
    field: (row: Row) => row.num_manutencao,
    sortable: true,
  },
  {
    name: 'emprestimo',
    label: 'Empréstimos',
    align: 'center',
    field: (row: Row) => row.num_emprestimo,
    sortable: true,
  },
  {
    name: 'foto',
    label: 'Foto',
    align: 'center',
    field: (row: Row) => row.foto,
    sortable: false,
  },
  {
    name: 'manual',
    label: 'Manual',
    align: 'center',
    field: (row: Row) => row.manual,
    sortable: false,
  },
  {
    name: 'acoes',
    label: 'Ações',
    align: 'center',
    field: '',
  },
];

interface RowManutencao {
  id: string,
  descricao: string,
  data: string,
  equipamento_nome: string,
  funcionario_nome: string,
}

const selectedNome = ref<string>('');
const selectedPatrimonio = ref<string>('');

function openDialog(row: Row) {
  selectedNome.value = row.nome;
  selectedPatrimonio.value = row.patrimonio;
  showDialog.value = true;
}

function closeDialog() {
  showDialog.value = false;
}

const rows = ref<Row[]>([]);
const manutencoes = ref<RowManutencao[]>([]);

async function getEquipments() {
  try {
    const response = await (api as AxiosInstance).get('/controle/equipamento/');

    if (response.status === 200) {
      const accessList = response.data
        .map(async (item: Row) => ({
          nome: item.nome,
          patrimonio: item.patrimonio,
          sala: item.sala_numero,
          defeito: item.defeito,
          num_manutencao: item.num_manutencao,
          num_emprestimo: item.num_emprestimo,
          foto: item.foto,
          manual: item.manual,
        }));
      rows.value = await Promise.all(accessList);
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

async function getManutencao(patr: string) {
  try {
    const response = await (api as AxiosInstance).get('/controle/manutencao/', {
      params: {
        patrimonio: patr,
      },
    });

    if (response.status === 200) {
      const manutencaoList = response.data
        .map(async (item: RowManutencao) => ({
          id: item.id,
          descricao: item.descricao,
          data: item.data,
          equipamento_nome: item.equipamento_nome,
          funcionario_nome: item.funcionario_nome,
        }));
      manutencoes.value = await Promise.all(manutencaoList);
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

async function registerManutencao(desc: string, patr: string) {
  const payload = {
    descricao: desc,
    patrimonio: patr,
  };

  try {
    const response = await (api as AxiosInstance).post('/controle/manutencao/', payload);

    if (response.status === 201) {
      $q.notify({
        type: 'positive',
        message: 'Manutenção registrada com successo.',
        timeout: notifTimeout,
      });

      await getEquipments();
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

const openImage = (imageUrl: string) => {
  window.open(imageUrl, '_blank');
};

onMounted(() => {
  getEquipments();
});
</script>

<template>
  <q-page>
    <q-card class="q-pa-md no-shadow">
      <q-tabs v-model="tab" dense class="text-grey q-mb-lg"
      active-color="primary" indicator-color="primary"
      align="justify" narrow-indicator
      >
        <q-tab class="text-purple" name="cadastrar" icon="mdi-clock-in" label="Cadastrar" />
        <q-tab class="text-orange" name="consultar" icon="mdi-clock-out" label="Consultar" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="cadastrar">
          <q-item>Em construção. Utilizar a interface de adm do Django por enquanto.</q-item>
        </q-tab-panel>

        <q-tab-panel name="consultar">

          <q-table title="Equipamentos" :rows="rows" :columns="columns"
          :filter="search" row-key="nome"
          >

            <template v-slot:top-right>
              <q-input borderless dense debounce="300" v-model="search" placeholder="Pesquisar">
                <template v-slot:append>
                  <q-icon name="mdi-table-search" />
                </template>
              </q-input>
            </template>

            <template v-slot:body-cell-foto="props">
              <q-td :props="props">
                <q-img v-if="props.row.foto"
                :src="props.row.foto" @click="openImage(props.row.foto)"
                class="q-mb-xs" style="max-width: 50px; max-height: 50px; object-fit: cover;" />
                <q-icon v-else name="mdi-image" class="text-grey" />
              </q-td>
            </template>

            <template v-slot:body-cell-manual="props">
              <q-td :props="props">
                <a v-if="props.row.manual" :href="props.row.manual" target="_blank" class="q-mb-xs">
                  <q-btn color="primary" label="Ler Manual" size="sm" />
                </a>
                <q-btn v-else color="primary" label="Ler Manual" size="sm" :disable=true />
              </q-td>
            </template>

            <template v-slot:body-cell-acoes="props">
              <q-td :props="props">
                <q-btn rounded color="primary"
                @click="openDialog(props.row); getManutencao(props.row.patrimonio);"
                size="sm">Manutenção</q-btn>
              </q-td>
            </template>
          </q-table>

          <q-dialog v-model="showDialog">
            <q-card>

              <q-card-section>
                <div class="text-h6">Adicionar manutenção</div>
              </q-card-section>

              <q-card-section class="q-pt-none">
                <q-input dense v-model="descManutencao" autofocus />
              </q-card-section>

              <q-separator />

              <q-card-section style="max-height: 50vh" class="scroll">
                <p v-for="manutencao in manutencoes" :key="manutencao.id">
                  [{{ format(manutencao.data, 'yyyy-MM-dd HH:mm:ss') }}]
                  [{{ manutencao.funcionario_nome }}] {{ manutencao.descricao }}
                </p>
              </q-card-section>

              <q-separator />

              <q-card-actions align="right">
                <q-btn flat label="Cancelar" color="primary" @click="closeDialog()" v-close-popup />
                <q-btn flat label="Adicionar" color="primary"
                  @click="registerManutencao(descManutencao, selectedPatrimonio)"
                  v-close-popup />
              </q-card-actions>
            </q-card>
          </q-dialog>

        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </q-page>
</template>
