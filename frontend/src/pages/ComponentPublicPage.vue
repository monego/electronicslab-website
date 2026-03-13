<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import type { AxiosResponse } from 'axios';
import ComponentTable from 'components/ComponentTable.vue';

interface Componente {
  nome: string;
  quantidade: number;
  datasheet: string | null;
  categoria: string;
  tipo: string;
  descricao?: string;
}

const $q = useQuasar();
const components = ref<Componente[]>([]);
const loading = ref(false);

interface TableColumn {
  name: string;
  label: string;
  align?: 'left' | 'right' | 'center';
  field: string | ((row: Componente) => string | number | null | undefined);
  required?: boolean;
  sortable?: boolean;
}

const columns: TableColumn[] = [
  { name: 'nome', label: 'Nome', field: 'nome', align: 'left', sortable: true },
  { name: 'tipo', label: 'Tipo', field: 'tipo', align: 'left', sortable: true },
  { name: 'quantidade', label: 'Quantidade', field: 'quantidade', align: 'center', sortable: true },
  { name: 'categoria', label: 'Categoria', field: 'categoria', align: 'center', sortable: true },
  { name: 'datasheet', label: 'Datasheet', field: 'datasheet', align: 'center' },
];

async function getComponents() {
  loading.value = true;
  try {
    const response: AxiosResponse<Componente[]> = await api.get('/controle/componentes-publico/');
    components.value = response.data;
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Erro ao carregar componentes.',
      timeout: 2500,
    });
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void getComponents();
});
</script>

<template>
  <q-page class="q-pa-md lg-container">
    <div class="header-section q-mb-xl text-center">
      <h1 class="text-h3 text-weight-bolder text-primary q-mb-sm">Banco de Componentes</h1>
      <p class="text-subtitle1 text-grey-7">Consulte a disponibilidade de componentes eletrônicos no laboratório.</p>
    </div>

    <ComponentTable
      title="Componentes Disponíveis"
      :rows="components"
      :columns="columns"
      :loading="loading"
    />
  </q-page>
</template>

<style scoped>
.lg-container {
  max-width: 1200px;
  margin: 0 auto;
}

.header-section h1 {
  background: linear-gradient(45deg, var(--q-primary), #64b5f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
