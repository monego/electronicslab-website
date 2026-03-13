<script setup lang="ts">
import { api } from 'boot/axios';
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import type { AxiosResponse } from 'axios';

interface Row {
  nome: string;
  patrimonio: string;
  sala_numero: string;
  foto: string | null;
  manual: string | null;
}

interface Column {
  name: string;
  label: string;
  align?: 'left' | 'right' | 'center';
  field: string | ((row: Row) => string | number | boolean | null | undefined);
  required?: boolean;
  sortable?: boolean;
}

const $q = useQuasar();
const search = ref('');
const loading = ref(false);

const columns: Column[] = [
  { name: 'foto', label: 'Visualizar', align: 'center', field: 'foto' },
  { name: 'nome', label: 'Equipamento', align: 'left', field: 'nome', sortable: true, required: true },
  { name: 'patrimonio', label: 'Patrimônio', align: 'center', field: 'patrimonio', sortable: true },
  { name: 'sala', label: 'Localização', align: 'center', field: 'sala_numero', sortable: true },
  { name: 'manual', label: 'Documentação', align: 'center', field: 'manual' },
];

const rows = ref<Row[]>([]);

const pagination = ref({
  sortBy: 'nome',
  descending: false,
  page: 1,
  rowsPerPage: 15,
});

async function getEquipments() {
  loading.value = true;
  try {
    const response: AxiosResponse<Row[]> = await api.get('/controle/materiais/');
    if (response.status === 200) {
      rows.value = response.data;
    }
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Erro ao carregar os equipamentos.',
      timeout: 2500,
    });
  } finally {
    loading.value = false;
  }
}

const openUrl = (url: string | null) => {
  if (url) window.open(url, '_blank');
};

onMounted(() => {
  void getEquipments();
});
</script>

<template>
  <q-page class="q-pa-md lg-container">
    <!-- Header Section -->
    <div class="header-section q-mb-xl text-center">
      <h1 class="text-h3 text-weight-bolder text-primary q-mb-sm">Inventário de Equipamentos</h1>
      <p class="text-subtitle1 text-grey-7">Consulte o patrimônio e manuais técnicos do laboratório.</p>
    </div>

    <!-- Main Content -->
    <q-card flat bordered class="equipment-card shadow-2">
      <q-table
        :rows="rows"
        :columns="columns"
        :filter="search"
        :loading="loading"
        row-key="patrimonio"
        v-model:pagination="pagination"
        :grid="$q.screen.xs"
        flat
        class="bg-white"
      >
        <!-- Custom Top Section with Robust Search -->
        <template v-slot:top-right>
          <q-input
            outlined
            dense
            debounce="300"
            v-model="search"
            placeholder="Buscar por nome, patrimônio ou sala..."
            class="search-input bg-white"
            style="min-width: 320px;"
          >
            <template v-slot:append>
              <q-icon name="mdi-magnify" color="primary" />
            </template>
          </q-input>
        </template>

        <!-- Tooltip for Foto -->
        <template v-slot:body-cell-foto="props">
          <q-td :props="props" class="text-center">
            <q-avatar v-if="props.row.foto" size="50px" rounded class="cursor-pointer shadow-1" @click="openUrl(props.row.foto)">
              <img :src="props.row.foto" style="object-fit: cover;">
              <q-tooltip>Clique para ampliar</q-tooltip>
            </q-avatar>
            <q-icon v-else name="mdi-image-off-outline" size="sm" color="grey-4" />
          </q-td>
        </template>

        <!-- Styled Localização -->
        <template v-slot:body-cell-sala="props">
          <q-td :props="props">
            <q-badge color="blue-1" text-color="blue-8" class="q-pa-sm text-weight-bold">
              <q-icon name="mdi-door-open" class="q-mr-xs" />
              Sala {{ props.value }}
            </q-badge>
          </q-td>
        </template>

        <!-- Styled Manual Button -->
        <template v-slot:body-cell-manual="props">
          <q-td :props="props">
            <q-btn
              v-if="props.row.manual"
              round
              flat
              color="primary"
              icon="mdi-file-pdf-box"
              @click="openUrl(props.row.manual)"
            >
              <q-tooltip>Ver Manual Técnico</q-tooltip>
            </q-btn>
            <q-icon v-else name="mdi-file-cancel-outline" color="grey-3" size="sm" />
          </q-td>
        </template>

        <!-- MOBILE GRID VIEW -->
        <template v-slot:item="props">
          <div class="q-pa-xs col-xs-12 col-sm-6">
            <q-card flat bordered class="mobile-equipment-card">
              <div class="row no-wrap">
                <div class="col-4 q-pa-sm flex flex-center">
                  <q-img
                    v-if="props.row.foto"
                    :src="props.row.foto"
                    class="rounded-borders shadow-1"
                    style="height: 100px; width: 100px; object-fit: cover;"
                    @click="openUrl(props.row.foto)"
                  />
                  <div v-else class="bg-grey-2 rounded-borders flex flex-center" style="height: 100px; width: 100px;">
                    <q-icon name="mdi-image-off-outline" color="grey-4" size="lg" />
                  </div>
                </div>

                <div class="col-8">
                  <q-card-section class="q-py-md">
                    <div class="text-subtitle1 text-weight-bold text-primary line-clamp-1">{{ props.row.nome }}</div>
                    <div class="text-caption text-grey-7 q-mb-sm">PAT: {{ props.row.patrimonio }}</div>

                    <div class="row items-center justify-between">
                      <q-badge color="blue-1" text-color="blue-8" class="q-pa-xs">
                        Sala {{ props.row.sala_numero }}
                      </q-badge>

                      <q-btn
                        v-if="props.row.manual"
                        flat
                        round
                        dense
                        color="primary"
                        icon="mdi-file-pdf-box"
                        @click="openUrl(props.row.manual)"
                      />
                    </div>
                  </q-card-section>
                </div>
              </div>
            </q-card>
          </div>
        </template>
      </q-table>
    </q-card>
  </q-page>
</template>

<style scoped>
.lg-container {
  max-width: 1400px;
  margin: 0 auto;
}

.header-section h1 {
  background: linear-gradient(45deg, var(--q-primary), #64b5f6);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.equipment-card {
  border-radius: 16px;
  overflow: hidden;
}

.search-input {
  transition: all 0.3s ease;
}

.search-input:focus-within {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.mobile-equipment-card {
  border-radius: 12px;
  transition: all 0.2s ease;
}

.mobile-equipment-card:hover {
  background: #f8fafc;
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

:deep(.q-table th) {
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  background-color: #f8fafc;
}

:deep(.q-table__card) {
  box-shadow: none !important;
}
</style>

