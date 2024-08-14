<script setup lang="ts">
import { AxiosInstance, AxiosError } from 'axios';
import { api, axios } from 'boot/axios';
import { ref, onMounted } from 'vue';

// Data properties
const tab = ref('consultar');

const showError = ref(false);
const errorMessage = ref<string>('');

function displayError(message: string) {
  errorMessage.value = message;
  showError.value = true;
}

type ColumnType = {
  name: string;
  label: string;
  field?: string | ((row: Record<string, string>) => string);
  required?: boolean;
  align?: 'left' | 'right' | 'center';
  format?: (val: string) => string;
  sortable?: boolean;
};

// Table
const search = ref('');
const columns: ColumnType[] = [
  {
    name: 'nome',
    required: true,
    label: 'Nome',
    align: 'left',
    field: 'nome',
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'patrimonio',
    label: 'Patrimônio',
    align: 'center',
    field: 'patrimonio',
  },
  {
    name: 'sala',
    label: 'Sala',
    align: 'center',
    field: 'sala',
  },
  {
    name: 'defeito',
    label: 'Defeito',
    align: 'center',
    field: 'defeito',
  },
  {
    name: 'manutencao',
    label: 'Manutenções',
    align: 'center',
    field: 'num_manutencao',
    sortable: true,
  },
  {
    name: 'foto',
    label: 'Foto',
    align: 'center',
    field: 'foto',
    sortable: false,
  },
  {
    name: 'manual',
    label: 'Manual',
    align: 'center',
    field: 'manual',
    sortable: false,
  },
  {
    name: 'acoes',
    label: 'Ações',
    align: 'center',
  },
];

interface Row {
  nome: string,
  patrimonio: string,
  sala_numero: string,
  defeito: boolean,
  num_manutencao: number,
  foto: string,
  manual: string,
}

const rows = ref<Row[]>([]);

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

const openImage = (imageUrl: string) => {
  window.open(imageUrl, '_blank');
};

const openFile = (fileUrl: string) => {
  window.open(fileUrl, '_blank');
};

onMounted(() => {
  getEquipments();
});
</script>

<template>
  <div class="q-pa-md">
    <q-card>
      <q-tabs v-model="tab" dense class="text-grey q-mb-lg"
      active-color="primary" indicator-color="primary"
        align="justify" narrow-indicator>
        <q-tab class="text-purple" name="cadastrar" icon="mdi-clock-in" label="Cadastrar" />
        <q-tab class="text-orange" name="consultar" icon="mdi-clock-out" label="Consultar" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated>
        <q-tab-panel name="cadastrar">
          <q-item>Em construção. Utilizar a interface de adm do Django por enquanto.</q-item>
        </q-tab-panel>

        <q-tab-panel name="consultar">

          <q-table title="Equipamentos" :rows="rows" :columns="columns"
          :filter="search" row-key="nome">

            <template v-slot:top-right>
              <q-input borderless dense debounce="300" v-model="search" placeholder="Search">
                <template v-slot:append>
                  <q-icon name="search" />
                </template>
              </q-input>
            </template>

            <template v-slot:body-cell-foto="props">
              <q-td :props="props">
                <q-img v-if="props.row.foto" :src="props.row.foto"
                @click="openImage(props.row.foto)" class="q-mb-xs"
                  style="max-width: 50px; max-height: 50px; object-fit: cover;" />
                <q-icon v-else name="photo" class="text-grey" />
              </q-td>
            </template>

            <template v-slot:body-cell-manual="props">
              <q-td :props="props">
                <a v-if="props.row.manual" :href="props.row.manual" target="_blank" class="q-mb-xs">
                  <q-btn color="primary" label="Ler Manual"
                  @click="openFile(props.row.manual)" size="sm" />
                </a>
                <q-btn v-else color="primary" label="Ler Manual" size="sm" :disable=true />
              </q-td>
            </template>

            <template v-slot:body-cell-acoes="props">
              <q-td :props="props">
                <q-btn rounded color="primary" size="sm">Manutenção</q-btn>
              </q-td>
            </template>
          </q-table>
        </q-tab-panel>
      </q-tab-panels>
    </q-card>
  </div>
</template>
