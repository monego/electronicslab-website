<script setup lang="ts">
import { AxiosInstance, AxiosError } from 'axios';
import { api, axios } from 'boot/axios';
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';

interface Row {
  nome: string,
  patrimonio: string,
  sala_numero: string,
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

const $q = useQuasar();
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
];

const rows = ref<Row[]>([]);

async function getEquipments() {
  try {
    const response = await (api as AxiosInstance).get('/controle/materiais/');

    if (response.status === 200) {
      const accessList = response.data
        .map(async (item: Row) => ({
          nome: item.nome,
          patrimonio: item.patrimonio,
          sala: item.sala_numero,
          foto: item.foto,
          manual: item.manual,
        }));
      rows.value = await Promise.all(accessList);
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
        <q-table
        :grid="$q.screen.xs"
        title="Equipamentos"
        :rows="rows"
        :columns="columns"
        :filter="search"
        row-key="nome"
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
        </q-table>
    </q-card>
  </q-page>
</template>
