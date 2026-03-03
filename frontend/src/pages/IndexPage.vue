<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { Temporal } from '@js-temporal/polyfill';

// --- Types & Interfaces ---

interface Aula {
  title: string;
  professor: string;
  room: string;
  room_id: number;
  room_number: string;
  room_name: string;
  is_it: boolean;
  floor: number;
  start: Temporal.ZonedDateTime;
  end: Temporal.ZonedDateTime;
  startTimeLabel: string;
  endTimeLabel: string;
}

interface Sala {
  id: number;
  nome: string;
  numero: string;
  andar: number;
  e_informatica: boolean;
}

interface RoomStatus {
  room: Sala;
  isAvailable: boolean;
  currentClass: Aula | null;
  nextClass: Aula | null;
  availableUntil: string | null;
  availableNext: string | null;
}

// --- State ---

const $q = useQuasar();
const aulas = ref<Aula[]>([]);
const salas = ref<Sala[]>([]);
const filter = ref<string>('');
const salaFilter = ref<string>('todas');
const currentTime = ref(Temporal.Now.zonedDateTimeISO());
let timer: ReturnType<typeof setInterval>;

// --- Helper Functions ---

function capitalizeEachWord(str: string): string {
  if (!str) return '';
  return str
    .split(' ')
    .filter(w => w)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

interface AulaAPI {
  disciplina: string;
  professor: string;
  sala_numero: string;
  sala_nome: string;
  sala: number;
  sala_e_informatica: boolean;
  sala_andar: number;
  inicio: string;
  fim: string;
}

// --- Data Fetching ---

async function fetchData() {
  try {
    const [salasRes, aulasRes] = await Promise.all([
      api.get('/root/salas/'),
      api.get('/aulas/aulas/hoje'),
    ]);

    if (salasRes.status === 200) {
      salas.value = salasRes.data as Sala[];
    }

    if (aulasRes.status === 200) {
      aulas.value = (aulasRes.data as AulaAPI[]).map((a) => ({
        title: a.disciplina,
        professor: a.professor,
        room: `[${a.sala_numero}] ${a.sala_nome}`,
        room_id: a.sala,
        room_number: a.sala_numero,
        room_name: a.sala_nome,
        is_it: a.sala_e_informatica,
        floor: a.sala_andar,
        start: Temporal.Instant.from(a.inicio).toZonedDateTimeISO(Temporal.Now.timeZoneId()),
        end: Temporal.Instant.from(a.fim).toZonedDateTimeISO(Temporal.Now.timeZoneId()),
        startTimeLabel: Temporal.Instant.from(a.inicio)
          .toZonedDateTimeISO(Temporal.Now.timeZoneId())
          .toPlainTime()
          .toString()
          .slice(0, 5),
        endTimeLabel: Temporal.Instant.from(a.fim)
          .toZonedDateTimeISO(Temporal.Now.timeZoneId())
          .toPlainTime()
          .toString()
          .slice(0, 5),
      }));
    }
  } catch (error) {
    console.error('Error fetching data:', error);
    $q.notify({
      type: 'negative',
      message: 'Não foi possível carregar as informações.',
    });
  }
}

// --- Computed Logic ---

const filteredRows = computed(() => {
  const now = currentTime.value;
  return aulas.value.filter(aula => {
    // Ignore classes that already ended
    if (Temporal.ZonedDateTime.compare(aula.end, now) <= 0) return false;

    // Search filter
    const matchesSearch = !filter.value ||
      aula.title.toLowerCase().includes(filter.value.toLowerCase()) ||
      aula.professor.toLowerCase().includes(filter.value.toLowerCase()) ||
      aula.room.toLowerCase().includes(filter.value.toLowerCase());

    if (!matchesSearch) return false;

    // Status filter
    if (salaFilter.value === 'todas') return true;
    if (salaFilter.value === 'andar1') return aula.floor === 1;
    if (salaFilter.value === 'andar2') return aula.floor === 2;
    if (salaFilter.value === 'informatica') return aula.is_it;

    return true;
  });
});

const itRoomsStatus = computed((): RoomStatus[] => {
  const itSalas = salas.value.filter(s => s.e_informatica);
  const now = currentTime.value;

  return itSalas.map(room => {
    const roomAulas = aulas.value
      .filter(a => a.room_id === room.id)
      .sort((a, b) => Temporal.ZonedDateTime.compare(a.start, b.start));

    const currentClass = roomAulas.find(a =>
      Temporal.ZonedDateTime.compare(a.start, now) <= 0 &&
      Temporal.ZonedDateTime.compare(a.end, now) > 0
    ) || null;

    const nextClass = roomAulas.find(a =>
      Temporal.ZonedDateTime.compare(a.start, now) > 0
    ) || null;

    const isAvailable = !currentClass;

    let availableUntil = null;
    if (isAvailable) {
      availableUntil = nextClass ? nextClass.startTimeLabel : 'Resto do dia';
    } else {
      availableUntil = currentClass.endTimeLabel;
    }

    return {
      room,
      isAvailable,
      currentClass,
      nextClass,
      availableUntil,
      availableNext: nextClass ? nextClass.startTimeLabel : null
    };
  });
});

let dataTimer: ReturnType<typeof setInterval>;

onMounted(async () => {
  await fetchData();
  timer = setInterval(() => {
    currentTime.value = Temporal.Now.zonedDateTimeISO();
  }, 30000); // Update every 30s for the UI clocks/status

  dataTimer = setInterval(() => {
    void fetchData();
  }, 300000); // Refresh data from backend every 5 minutes
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
  if (dataTimer) clearInterval(dataTimer);
});

// --- Table Columns ---

const columns: {
  name: string;
  label: string;
  align: 'left' | 'center' | 'right';
  field: string | ((row: Aula) => string | number | boolean | Temporal.ZonedDateTime | null);
  sortable?: boolean;
}[] = [
  { name: 'horario', label: 'Horário', align: 'left', field: 'start', sortable: true },
  { name: 'sala', label: 'Sala', align: 'left', field: 'room', sortable: true },
  { name: 'professor', label: 'Professor', align: 'left', field: 'professor', sortable: true },
  { name: 'disciplina', label: 'Disciplina', align: 'left', field: 'title', sortable: true },
];
</script>

<template>
  <q-page class="q-pa-lg bg-page">

    <!-- Main Schedule Table -->
    <q-card flat class="table-card glass-card overflow-hidden">
      <q-card-section class="q-pb-none">
        <div class="row items-center q-col-gutter-md">
          <div class="col-12 col-md-auto">
            <h1 class="text-h5 text-weight-bolder text-slate-900 q-my-none">Programação de Hoje</h1>
          </div>
          <q-space />
          <div class="col-12 col-md-auto row q-col-gutter-md items-center">
            <q-tabs
              v-model="salaFilter"
              class="text-primary nav-tabs"
              no-caps
              rounded
              dense
              indicator-color="transparent"
              active-bg-color="primary"
              active-color="white"
            >
              <q-tab name="todas" label="Todas" />
              <q-tab name="andar1" label="1º Andar" />
              <q-tab name="andar2" label="2º Andar" />
              <q-tab name="informatica" label="Info" />
            </q-tabs>

            <q-input
              v-model="filter"
              placeholder="Pesquisar..."
              outlined
              dense
              class="search-input bg-white rounded-borders"
            >
              <template v-slot:append>
                <q-icon name="mdi-magnify" color="grey-6" />
              </template>
            </q-input>
          </div>
        </div>
      </q-card-section>

      <q-card-section class="q-pa-none q-mt-md">
        <q-table
          :rows="filteredRows"
          :columns="columns"
          row-key="id"
          flat
          class="modern-table"
          :pagination="{ rowsPerPage: 0 }"
          hide-pagination
          :grid="$q.screen.lt.md"
        >
          <!-- Desktop Table Body -->
          <template v-slot:body="props">
            <q-tr :props="props" class="table-row">
              <q-td key="horario" :props="props">
                <div class="row items-center no-wrap">
                  <q-icon name="mdi-clock-time-four-outline" color="primary" class="q-mr-md" size="20px" />
                  <div class="text-weight-bold">
                    {{ props.row.startTimeLabel }} <span class="text-grey-5">—</span> {{ props.row.endTimeLabel }}
                  </div>
                </div>
              </q-td>
              <q-td key="sala" :props="props">
                <q-chip
                  outline
                  square
                  color="slate-700"
                  text-color="slate-900"
                  class="room-chip"
                >
                  <q-icon :name="props.row.is_it ? 'mdi-desktop-classic' : 'mdi-door-open'" size="16px" class="q-mr-sm" />
                  {{ props.row.room }}
                </q-chip>
              </q-td>
              <q-td key="professor" :props="props">
                <div class="text-weight-medium">{{ capitalizeEachWord(props.row.professor) }}</div>
              </q-td>
              <q-td key="disciplina" :props="props">
                <div class="text-weight-bolder text-primary uppercase tracking-tight">
                  {{ props.row.title }}
                </div>
              </q-td>
            </q-tr>
          </template>

          <!-- Mobile Grid View -->
          <template v-slot:item="props">
            <div class="q-pa-md col-xs-12 col-sm-6">
              <q-card flat class="mobile-class-card bordered q-pa-sm">
                <q-card-section>
                  <div class="row justify-between items-start q-mb-md">
                    <q-chip dense color="primary" text-color="white" icon="mdi-clock">
                      {{ props.row.startTimeLabel }} - {{ props.row.endTimeLabel }}
                    </q-chip>
                    <q-chip dense outline color="grey-8">
                      {{ props.row.room }}
                    </q-chip>
                  </div>
                  <div class="text-h6 text-weight-bolder q-mb-xs">{{ props.row.title }}</div>
                  <div class="text-subtitle2 text-grey-8 flex items-center">
                    <q-icon name="mdi-account" class="q-mr-xs" />
                    {{ capitalizeEachWord(props.row.professor) }}
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </template>

          <!-- Empty State -->
          <template v-slot:no-data>
            <div class="full-width row flex-center q-pa-xl text-grey-6 q-gutter-sm">
              <q-icon name="mdi-calendar-blank" size="48px" />
              <div class="text-h6">Nenhuma aula encontrada para hoje</div>
            </div>
          </template>
        </q-table>
      </q-card-section>
    </q-card>

    <!-- Quick IT Dashboard -->
    <div class="row q-col-gutter-lg q-mb-xl">
      <div class="col-12">
        <div class="flex items-center q-mb-md">
          <q-icon name="mdi-desktop-classic" color="primary" size="32px" class="q-mr-sm" />
          <h2 class="text-h5 text-weight-bolder q-my-none text-slate-800">Laboratórios de Informática</h2>
        </div>
      </div>

      <div v-for="status in itRoomsStatus" :key="status.room.id" class="col-12 col-sm-6 col-md-3">
        <q-card flat class="room-status-card glass-card" :class="{ 'is-busy': !status.isAvailable }">
          <q-card-section>
            <div class="row items-center no-wrap">
              <div class="col">
                <div class="text-overline text-primary text-weight-bold">SALA {{ status.room.numero }}</div>
                <div class="text-h6 text-weight-bolder ellipsis">{{ status.room.nome }}</div>
              </div>
              <div class="col-auto">
                <q-badge
                  :color="status.isAvailable ? 'positive' : 'negative'"
                  class="status-badge"
                  rounded
                >
                  {{ status.isAvailable ? 'Livre' : 'Ocupada' }}
                </q-badge>
              </div>
            </div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <div v-if="status.isAvailable" class="availability-info">
              <div class="text-caption text-grey-7">Disponível até</div>
              <div class="text-h6 text-weight-bold text-positive">{{ status.availableUntil }}</div>
            </div>
            <div v-else class="availability-info">
              <div class="text-caption text-grey-7">Ocupada até</div>
              <div class="text-h6 text-weight-bold text-negative">{{ status.availableUntil }}</div>
            </div>

            <div class="next-info q-mt-sm" v-if="!status.isAvailable && status.nextClass">
              <q-separator class="q-mb-sm" />
              <div class="text-caption text-grey-6 flex items-center">
                <q-icon name="mdi-clock-outline" size="14px" class="q-mr-xs" />
                Próxima às {{ status.nextClass.startTimeLabel }}
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

  </q-page>
</template>

<style lang="scss" scoped>
.bg-page {
  background-color: #f8fafc;
}

.text-slate-800 { color: #1e293b; }
.text-slate-900 { color: #0f172a; }

.glass-card {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.room-status-card {
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }

  &.is-busy {
    border-left: 4px solid var(--q-negative);
  }
  &:not(.is-busy) {
    border-left: 4px solid var(--q-positive);
  }
}

.status-badge {
  padding: 4px 12px;
  font-weight: 700;
  letter-spacing: 0.025em;
}

.nav-tabs {
  background: rgba(0, 0, 0, 0.03);
  padding: 4px;
  border-radius: 12px;

  :deep(.q-tab) {
    min-height: 36px;
    border-radius: 8px;
    margin: 0 2px;
  }
}

.search-input {
  width: 240px;
  :deep(.q-field__control) {
    border-radius: 12px;
  }
}

.table-card {
  min-height: 400px;
}

.modern-table {
  background: transparent;

  :deep(thead tr) {
    background: #f1f5f9;
    th {
      font-weight: 800;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-size: 0.75rem;
      border: none;
    }
  }

  :deep(tbody tr) {
    &:hover {
      background: rgba(59, 130, 246, 0.03);
    }
  }
}

.table-row {
  transition: background 0.2s ease;
  td {
    padding: 16px !important;
    border-bottom: 1px solid #f1f5f9 !important;
  }
}

.room-chip {
  background: #f1f5f9 !important;
  border-color: #e2e8f0;
  font-weight: 700;
}

.mobile-class-card {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.uppercase { text-transform: uppercase; }
.tracking-tight { letter-spacing: -0.025em; }
.tracking-tighter { letter-spacing: -0.05em; }

@media (max-width: 600px) {
  .search-input {
    width: 100%;
  }
}
</style>
