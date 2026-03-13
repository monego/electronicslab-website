<script setup lang="ts">
import { ref } from 'vue';
import { useQuasar } from 'quasar';

interface Row {
  id?: number;
  nome: string;
  descricao?: string;
  quantidade: number;
  datasheet: string | null;
  categoria: string;
  tipo: string;
}

interface Column<T = Row> {
  name: string;
  label: string;
  align?: 'left' | 'right' | 'center';
  field: string | ((row: T) => string | number | null | undefined);
  required?: boolean;
  sortable?: boolean;
  format?: (val: string | number | boolean | null | undefined) => string;
}

defineProps<{
  rows: Row[];
  columns: Column<Row>[];
  title?: string;
  loading?: boolean;
}>();

const emit = defineEmits(['edit', 'delete']);

const search = ref('');
const $q = useQuasar();

const openDatasheet = (url: string) => {
  window.open(url, '_blank');
};

const pagination = ref({
  sortBy: 'nome',
  descending: false,
  page: 1,
  rowsPerPage: 15
});

</script>

<template>
  <q-table
    :title="title"
    :rows="rows"
    :columns="columns"
    :filter="search"
    :loading="loading"
    row-key="id"
    v-model:pagination="pagination"
    class="component-table shadow-2"
    :grid="$q.screen.xs"
    flat
    bordered
  >
    <template v-slot:top-right>
      <q-input
        outlined
        dense
        debounce="300"
        v-model="search"
        placeholder="Pesquisar componentes..."
        class="bg-white"
        style="min-width: 250px;"
      >
        <template v-slot:append>
          <q-icon name="mdi-magnify" color="primary" />
        </template>
      </q-input>
      <slot name="top-actions"></slot>
    </template>

    <template v-slot:body-cell-datasheet="props">
      <q-td :props="props" class="text-center">
        <q-btn
          v-if="props.row.datasheet"
          flat
          round
          color="primary"
          icon="mdi-file-pdf-box"
          @click="void openDatasheet(props.row.datasheet)"
        >
          <q-tooltip>Ver Datasheet</q-tooltip>
        </q-btn>
        <q-icon v-else name="mdi-file-cancel-outline" color="grey-4" size="sm" />
      </q-td>
    </template>

    <template v-slot:body-cell-categoria="props">
      <q-td :props="props">
        <q-badge :color="props.row.categoria === 'Elétrica' ? 'blue' : props.row.categoria === 'Pneumática' ? 'orange' : 'green'" outline>
          {{ props.value }}
        </q-badge>
      </q-td>
    </template>

    <template v-slot:body-cell-acoes="props">
      <q-td :props="props" class="q-gutter-x-sm text-center">
        <q-btn
          flat
          round
          dense
          color="primary"
          icon="mdi-pencil"
          @click="emit('edit', props.row)"
        >
          <q-tooltip>Editar Componente</q-tooltip>
        </q-btn>
        <q-btn
          flat
          round
          dense
          color="negative"
          icon="mdi-delete"
          @click="emit('delete', props.row)"
        >
          <q-tooltip>Excluir Componente</q-tooltip>
        </q-btn>
      </q-td>
    </template>

    <!-- Grid view for mobile -->
    <template v-slot:item="props">
      <div class="q-pa-xs col-xs-12 col-sm-6 col-md-4">
        <q-card flat bordered class="q-pa-sm">
          <q-card-section>
            <div class="row items-center no-wrap">
              <div class="col">
                <div class="text-h6 text-primary">{{ props.row.nome }}</div>
                <div class="text-caption text-grey-7">{{ props.row.tipo }}</div>
              </div>
              <div class="col-auto">
                <q-badge :color="props.row.categoria === 'EL' ? 'blue' : 'green'">
                  {{ props.row.categoria }}
                </q-badge>
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <q-list dense>
            <q-item>
              <q-item-section>Quantidade</q-item-section>
              <q-item-section side>{{ props.row.quantidade }}</q-item-section>
            </q-item>
          </q-list>

          <q-separator />

          <q-card-actions align="right">
            <q-btn
              v-if="props.row.datasheet"
              flat
              color="primary"
              icon="mdi-file-pdf-box"
              label="Datasheet"
              @click="void openDatasheet(props.row.datasheet)"
            />
            <slot name="item-actions" :row="props.row"></slot>
          </q-card-actions>
        </q-card>
      </div>
    </template>
  </q-table>
</template>

<style scoped>
.component-table {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.q-table__title) {
  font-weight: 700;
  color: var(--q-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

:deep(.q-table th) {
  font-weight: 700;
  background-color: rgba(0, 0, 0, 0.02);
}
</style>
