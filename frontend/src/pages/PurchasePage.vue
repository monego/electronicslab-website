<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { AxiosInstance } from 'axios';
import { api } from 'boot/axios';
import { format } from 'date-fns';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const notifTimeout = 30;

const showDialog = ref<boolean>(false);

const selectTitle = ref<string>('');

const selectOrigin = ref<string>('');

const originOptions: Record<string, string> = {
  'Registro de Preço': 'rp',
  Almoxarifado: 'almox',
  'Cartão Corporativo': 'cc',
};

const selectType = ref<string>('');

const typeOptions: Record<string, string> = {
  Consumo: 'consumo',
  Permanente: 'permanente',
};

const selectQuantity = ref<number>(0);
const selectDescription = ref<string>('');
const selectReasoning = ref<string>('');

const statusOptions: Record<string, string> = {
  Solicitado: 'solicitado',
  Aprovado: 'aprovado',
  Tramitado: 'tramitado',
  Comprado: 'comprado',
  Recebido: 'recebido',
  Negado: 'negado',
  Excluído: 'excluido',
};

function getKeys(options: Record<string, string>, val: string): string {
  return Object.keys(options).filter(
    (key: string) => options[key] === `${val}`,
  )[0] ?? '';
}

type Row = {
    data: string,
    origem: string,
    tipo: string,
    titulo: string,
    justificativa: string,
    estado: string,
    quantidade: number,
    funcionario_nome: string,
}

type Column = {
    name: string;
    label: string;
    align?: 'left' | 'right' | 'center';
    field: string | ((row: Row) => string);
    required?: boolean;
    format?: (val: string) => string;
    sortable?:boolean;
}

const rows = ref<Row[]>([]);

const columns: Column[] = [
  {
    name: 'titulo',
    label: 'Título',
    align: 'left',
    field: (row: Row) => row.titulo,
    required: true,
    format: (val: string) => `${val}`,
    sortable: true,
  },
  {
    name: 'origem',
    label: 'Origem',
    align: 'left',
    field: (row: Row) => row.origem,
    required: true,
    format: (val: string) => getKeys(originOptions, val),
    sortable: true,
  },
  {
    name: 'tipo',
    label: 'Tipo',
    align: 'left',
    field: (row: Row) => row.tipo,
    required: true,
    format: (val: string) => getKeys(typeOptions, val),
    sortable: true,
  },
  {
    name: 'data',
    label: 'Data',
    align: 'left',
    field: (row: Row) => row.data,
    required: true,
    format: (val: string) => format(`${val}`, 'yyyy-MM-dd HH:mm:ss'),
    sortable: true,
  },
  {
    name: 'estado',
    label: 'Estado',
    align: 'left',
    field: (row: Row) => row.estado,
    required: true,
    format: (val: string) => getKeys(statusOptions, val),
    sortable: true,
  },
  {
    name: 'editar',
    label: 'Editar',
    align: 'center',
    field: '',
  },
  {
    name: 'orcamentos',
    label: 'Orçamentos',
    align: 'center',
    field: '',
  },
];

async function getCompras() {
  try {
    const response = await (api as AxiosInstance).get('/controle/compras/');
    if (response.status === 200) {
      const purchaseList = response.data
        .map(async (item: Row) => ({
          data: item.data,
          origem: item.origem,
          tipo: item.tipo,
          titulo: item.titulo,
          estado: item.estado,
          justificativa: item.justificativa,
          quantidade: item.quantidade,
          funcionario_nome: item.funcionario_nome,
        }));
      rows.value = await Promise.all(purchaseList);
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao buscar a lista de compras.',
      timeout: notifTimeout,
    });
  }
}

async function createNewCompra() {
  const payload = {
    titulo: selectTitle.value,
    descricao: selectDescription.value,
    origem: originOptions[selectOrigin.value],
    tipo: typeOptions[selectType.value],
    quantidade: selectQuantity.value,
    justificativa: selectReasoning.value,
  };

  try {
    await (api as AxiosInstance).post('/controle/compras/', payload);
    $q.notify({
      type: 'positive',
      message: 'Solicitação de compra registrada com successo.',
      timeout: notifTimeout,
    });
    await getCompras();
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Erro ao registrar empréstimo',
      timeout: notifTimeout,
    });
  }
  showDialog.value = false;
}

onMounted(() => {
  getCompras();
});
</script>

<template>
  <div class="q-pa-md">

    <div class="q-pa-md">
      <q-btn color="primary" label="Adicionar nova solicitação" @click="showDialog = true" />
      <q-btn color="primary" label="Gerar documento DEMAPA" />
    </div>

    <q-table
    title="Solicitações de compra"
    :rows="rows"
    :columns="columns"
    row-key="titulo"
    >
      <template v-slot:body-cell-editar="props">
        <q-td :props="props">
          <q-btn rounded color="primary" size="sm">
            Editar
          </q-btn>
        </q-td>
      </template>

      <template v-slot:body-cell-orcamentos="props">
        <q-td :props="props">
          <q-btn rounded color="primary" size="sm">
            Orçamentos
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card>
        <q-card-section>
          <q-input v-model="selectTitle" label="Título" />
          <q-input v-model="selectDescription" type="textarea" label="Descrição" />
          <q-select v-model="selectOrigin" :options="Object.keys(originOptions)" label="Origem" />
          <q-select v-model="selectType" :options="Object.keys(typeOptions)" label="Material" />
          <q-input v-model.number="selectQuantity" type="number" />
          <q-input v-model="selectReasoning" type="textarea" label="Justificativa" />
          <q-btn color="red" label="Cancelar" @click="showDialog = false" />
          <q-btn color="primary" label="Adicionar" @click="createNewCompra" />
        </q-card-section>
      </q-card>
    </q-dialog>
 </div>
</template>
