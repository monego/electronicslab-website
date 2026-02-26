<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { format } from 'date-fns';
import { useQuasar } from 'quasar';
import type { AxiosResponse } from 'axios';

const $q = useQuasar();
const notifTimeout = 30;

const showDialog = ref<boolean>(false);
const showBudgetDialog = ref<boolean>(false);
const dialogMode = ref<'create' | 'edit'>('create');
const selectedId = ref<number | null>(null);

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
const selectStatus = ref<string>('solicitado');

interface Budget {
  url: string;
  source: string;
  price: number;
  company: string;
  date: string;
}

const budgetSourceOptions = [
  { label: 'Website', value: 'website' },
  { label: 'Telefone', value: 'telefone' },
  { label: 'E-mail', value: 'email' },
];

const budgets = ref<[Budget, Budget, Budget]>([
  { url: '', source: 'website', price: 0, company: '', date: '' },
  { url: '', source: 'website', price: 0, company: '', date: '' },
  { url: '', source: 'website', price: 0, company: '', date: '' },
]);

const precoMaximo = ref<number>(0);

const statusOptions: Record<string, string> = {
  Solicitado: 'solicitado',
  Aprovado: 'aprovado',
  Tramitado: 'tramitado',
  Comprado: 'comprado',
  Recebido: 'recebido',
  Negado: 'negado',
  Excluído: 'excluido',
};

function getKeys(options: Record<string, string>, val: unknown): string {
  return Object.keys(options).find(
    (key: string) => options[key] === String(val),
  ) ?? '';
}

interface Row {
    id: number,
    data: string,
    origem: string,
    tipo: string,
    titulo: string,
    descricao: string,
    justificativa: string,
    estado: string,
    quantidade: number,
    funcionario_nome: string,
    url_orcamento_1: string | null,
    fonte_orcamento_1: string | null,
    preco_orcamento_1: number | string | null,
    empresa_orcamento_1: string | null,
    data_orcamento_1: string | null,
    url_orcamento_2: string | null,
    fonte_orcamento_2: string | null,
    preco_orcamento_2: number | string | null,
    empresa_orcamento_2: string | null,
    data_orcamento_2: string | null,
    url_orcamento_3: string | null,
    fonte_orcamento_3: string | null,
    preco_orcamento_3: number | string | null,
    empresa_orcamento_3: string | null,
    data_orcamento_3: string | null,
    preco_maximo: number | string | null,
}

interface Column {
    name: string;
    label: string;
    align?: 'left' | 'right' | 'center';
    field: string | ((row: Row) => string | number | null | undefined);
    required?: boolean;
    format?: (val: unknown) => string;
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
    format: (val) => String(val),
    sortable: true,
  },
  {
    name: 'quantidade',
    label: 'Qtd',
    align: 'center',
    field: (row: Row) => row.quantidade,
    sortable: true,
  },
  {
    name: 'funcionario',
    label: 'Solicitante',
    align: 'left',
    field: (row: Row) => row.funcionario_nome,
    sortable: true,
  },
  {
    name: 'origem',
    label: 'Origem',
    align: 'left',
    field: (row: Row) => row.origem,
    required: true,
    format: (val) => getKeys(originOptions, val),
    sortable: true,
  },
  {
    name: 'tipo',
    label: 'Tipo',
    align: 'left',
    field: (row: Row) => row.tipo,
    required: true,
    format: (val) => getKeys(typeOptions, val),
    sortable: true,
  },
  {
    name: 'data',
    label: 'Data',
    align: 'left',
    field: (row: Row) => row.data,
    required: true,
    format: (val) => {
      if (!val) return '';
      const date = new Date(val as string | number | Date);
      return isNaN(date.getTime()) ? '' : format(date, 'yyyy-MM-dd HH:mm:ss');
    },
    sortable: true,
  },
  {
    name: 'estado',
    label: 'Estado',
    align: 'left',
    field: (row: Row) => row.estado,
    required: true,
    format: (val) => getKeys(statusOptions, val),
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
  {
    name: 'demapa',
    label: 'DEMAPA',
    align: 'center',
    field: '',
  },
];

async function getCompras() {
  try {
    const response: AxiosResponse<Row[]> = await api.get('/controle/compras/');
    if (response.status === 200) {
      rows.value = response.data;
    }
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Erro ao buscar a lista de compras.',
      timeout: notifTimeout,
    });
  }
}

function openCreateDialog() {
  dialogMode.value = 'create';
  selectedId.value = null;
  selectTitle.value = '';
  selectDescription.value = '';
  selectOrigin.value = '';
  selectType.value = '';
  selectQuantity.value = 0;
  selectReasoning.value = '';
  selectStatus.value = 'solicitado';
  showDialog.value = true;
}

function openEditDialog(row: Row) {
  dialogMode.value = 'edit';
  selectedId.value = row.id;
  selectTitle.value = row.titulo;
  selectDescription.value = row.descricao;
  selectOrigin.value = getKeys(originOptions, row.origem);
  selectType.value = getKeys(typeOptions, row.tipo);
  selectQuantity.value = row.quantidade;
  selectReasoning.value = row.justificativa;
  selectStatus.value = getKeys(statusOptions, row.estado);
  showDialog.value = true;
}

function openBudgetDialog(row: Row) {
  selectedId.value = row.id;
  precoMaximo.value = Number(row.preco_maximo) || 0;
  budgets.value = [
    { url: row.url_orcamento_1 || '', source: row.fonte_orcamento_1 || 'website', price: Number(row.preco_orcamento_1) || 0, company: row.empresa_orcamento_1 || '', date: row.data_orcamento_1 || '' },
    { url: row.url_orcamento_2 || '', source: row.fonte_orcamento_2 || 'website', price: Number(row.preco_orcamento_2) || 0, company: row.empresa_orcamento_2 || '', date: row.data_orcamento_2 || '' },
    { url: row.url_orcamento_3 || '', source: row.fonte_orcamento_3 || 'website', price: Number(row.preco_orcamento_3) || 0, company: row.empresa_orcamento_3 || '', date: row.data_orcamento_3 || '' },
  ];
  showBudgetDialog.value = true;
}

async function saveCompra() {
  const payload = {
    titulo: selectTitle.value,
    descricao: selectDescription.value,
    origem: originOptions[selectOrigin.value],
    tipo: typeOptions[selectType.value],
    quantidade: selectQuantity.value,
    justificativa: selectReasoning.value,
    estado: statusOptions[selectStatus.value] || 'solicitado',
  };

  try {
    if (dialogMode.value === 'create') {
      await api.post('/controle/compras/', payload);
    } else {
      await api.patch(`/controle/compras/${selectedId.value}/`, payload);
    }
    $q.notify({
      type: 'positive',
      message: `Solicitação de compra ${dialogMode.value === 'create' ? 'registrada' : 'atualizada'} com successo.`,
      timeout: notifTimeout,
    });
    await getCompras();
    showDialog.value = false;
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Erro ao salvar solicitação de compra',
      timeout: notifTimeout,
    });
  }
}

async function saveBudgets() {
  const payload = {
    url_orcamento_1: budgets.value[0].url,
    fonte_orcamento_1: budgets.value[0].source,
    preco_orcamento_1: budgets.value[0].price || null,
    empresa_orcamento_1: budgets.value[0].company,
    data_orcamento_1: budgets.value[0].date || null,
    url_orcamento_2: budgets.value[1].url,
    fonte_orcamento_2: budgets.value[1].source,
    preco_orcamento_2: budgets.value[1].price || null,
    empresa_orcamento_2: budgets.value[1].company,
    data_orcamento_2: budgets.value[1].date || null,
    url_orcamento_3: budgets.value[2].url,
    fonte_orcamento_3: budgets.value[2].source,
    preco_orcamento_3: budgets.value[2].price || null,
    empresa_orcamento_3: budgets.value[2].company,
    data_orcamento_3: budgets.value[2].date || null,
    preco_maximo: precoMaximo.value || null,
  };

  try {
    await api.patch(`/controle/compras/${selectedId.value}/`, payload);
    $q.notify({
      type: 'positive',
      message: 'Orçamentos atualizados com sucesso.',
      timeout: notifTimeout,
    });
    await getCompras();
    showBudgetDialog.value = false;
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Erro ao salvar orçamentos.',
      timeout: notifTimeout,
    });
  }
}

async function downloadDemapa(id: number) {
  try {
    const response = await api.get(`/controle/compras/${id}/demapa/`, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `demapa_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
    $q.notify({
      type: 'positive',
      message: 'PDF gerado com sucesso.',
      timeout: notifTimeout,
    });
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Erro ao gerar PDF.',
      timeout: notifTimeout,
    });
  }
}

onMounted(() => {
  getCompras()
  .catch(err => console.error('Falhou ao buscar compras:', err));
});
</script>

<template>
  <div class="q-pa-md">

    <div class="q-pa-md q-gutter-sm">
      <q-btn color="primary" label="Adicionar nova solicitação" @click="openCreateDialog" />
    </div>

    <q-table
    title="Solicitações de compra"
    :rows="rows"
    :columns="columns"
    row-key="id"
    >
      <template v-slot:body-cell-editar="props">
        <q-td :props="props">
          <q-btn rounded color="primary" size="sm" icon="edit" @click="openEditDialog(props.row)">
            Editar
          </q-btn>
        </q-td>
      </template>

      <template v-slot:body-cell-orcamentos="props">
        <q-td :props="props">
          <q-btn rounded color="secondary" size="sm" icon="request_quote" @click="openBudgetDialog(props.row)">
            Orçamentos
          </q-btn>
        </q-td>
      </template>

      <template v-slot:body-cell-demapa="props">
        <q-td :props="props">
          <q-btn rounded color="accent" size="sm" icon="description" @click="downloadDemapa(props.row.id)">
            DEMAPA
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="min-width: 400px" v-if="showDialog">
        <q-card-section>
          <div class="text-h6">{{ dialogMode === 'create' ? 'Nova Solicitação' : 'Editar Solicitação' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="selectTitle" label="Título" filled />
          <q-input v-model="selectDescription" type="textarea" label="Descrição" filled />
          <div class="row q-col-gutter-sm">
            <div class="col-6">
              <q-select v-model="selectOrigin" :options="Object.keys(originOptions)" label="Origem" filled />
            </div>
            <div class="col-6">
              <q-select v-model="selectType" :options="Object.keys(typeOptions)" label="Material" filled />
            </div>
          </div>
          <div class="row q-col-gutter-sm">
            <div class="col-6">
              <q-input v-model.number="selectQuantity" type="number" label="Quantidade" filled />
            </div>
            <div class="col-6">
               <q-select v-model="selectStatus" :options="Object.keys(statusOptions)" label="Estado" filled />
            </div>
          </div>
          <q-input v-model="selectReasoning" type="textarea" label="Justificativa" filled />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="red" v-close-popup />
          <q-btn flat label="Salvar" color="primary" @click="saveCompra" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Dialog de Orçamentos -->
    <q-dialog v-model="showBudgetDialog">
      <q-card style="min-width: 500px" v-if="showBudgetDialog">
        <q-card-section>
          <div class="text-h6">Orçamentos</div>
        </q-card-section>

        <q-card-section class="q-px-md">
          <q-input
            v-model.number="precoMaximo"
            type="number"
            label="Preço Máximo Estimado (R$)"
            filled
            prefix="R$"
            hint="Valor que aparecerá no cabeçalho do documento"
          />
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <div v-for="(budget, index) in budgets" :key="index" class="q-mb-md border-bottom q-pb-md">
            <div class="text-subtitle2">Orçamento {{ index + 1 }}</div>
            <div class="row q-col-gutter-sm">
              <div class="col-8">
                <q-input
                  v-model="budget.url"
                  :label="budget.source === 'website' ? 'URL' : budget.source === 'telefone' ? 'Telefone' : 'E-mail'"
                  filled
                />
              </div>
              <div class="col-4">
                <q-select
                  v-model="budget.source"
                  :options="budgetSourceOptions"
                  label="Fonte"
                  filled
                  emit-value
                  map-options
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm q-mt-xs">
              <div class="col-8">
                <q-input v-model="budget.company" label="Empresa" filled />
              </div>
              <div class="col-4">
                <q-input
                  v-model.number="budget.price"
                  type="number"
                  label="Preço"
                  filled
                  prefix="R$"
                />
              </div>
            </div>
            <div class="row q-col-gutter-sm q-mt-xs">
              <div class="col-12">
                <q-input v-model="budget.date" type="date" label="Data do Orçamento" filled stack-label />
              </div>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="red" v-close-popup />
          <q-btn flat label="Salvar Orçamentos" color="primary" @click="saveBudgets" />
        </q-card-actions>
      </q-card>
    </q-dialog>
 </div>
</template>
