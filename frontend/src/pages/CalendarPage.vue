<script setup lang="ts">
import { ScheduleXCalendar } from '@schedule-x/vue';
import { createCurrentTimePlugin } from '@schedule-x/current-time';
import { ref, watch, onMounted } from 'vue';
import { createEventsServicePlugin } from '@schedule-x/events-service';
import { createCalendarControlsPlugin } from '@schedule-x/calendar-controls';
import { api } from 'boot/axios';
import {
  createCalendar,
  createViewDay,
  createViewWeek,
} from '@schedule-x/calendar';
import 'temporal-polyfill/global';
import '@schedule-x/theme-default/dist/index.css';

// Schedule-X v3 uses Temporal objects natively
interface CalendarEvent {
  id: number;
  start: Temporal.ZonedDateTime;
  end: Temporal.ZonedDateTime;
  title: string;
}

interface TemporalRange {
  start: Temporal.ZonedDateTime;
  end: Temporal.ZonedDateTime;
}

interface Sala {
  label: string;
  code: string;
}

interface SalaResponse {
  id: number;
  predio: number;
  nome: string;
  numero: string;
  codigo: string;
}

interface AulaApiResponse {
  inicio: string;
  fim: string;
  disciplina: string;
  professor: string;
}

const sala = ref<Sala | null>(null);
const salas = ref<Sala[]>([]);
const isSyncing = ref(false);

const localTz = Temporal.Now.timeZoneId();
const calendarControlsPlugin = createCalendarControlsPlugin();
const eventsServicePlugin = createEventsServicePlugin();

function capitalizeWords(str: string): string {
  if (!str) return '';
  return str
    .toLowerCase()
    .split(' ')
    .filter(word => word.length > 0)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

async function getSalas() {
  try {
    const response = await api.get<SalaResponse[]>('/root/salas');
    if (response.status === 200) {
      salas.value = response.data.map((obj) => ({
        label: `Sala ${obj.numero} - ${obj.nome}`,
        code: obj.codigo,
      }));
    }
  } catch (error) {
    console.error('Erro ao buscar salas:', error);
  }
}

/**
 * Fetch aulas from Django API for a given room and Temporal date range.
 */
async function getAulas(roomId: string, range: TemporalRange) {
  isSyncing.value = true;

  // Convert Temporal range (ZonedDateTime) to plain date strings for the Django API
  const rangeStart = range.start.toPlainDate().toString();
  const rangeEnd = range.end.toPlainDate().add({ days: 1 }).toString();

  try {
    const response = await api.get<AulaApiResponse[]>('/aulas/aulas/calendario', {
      params: {
        codigo: roomId,
        inicio: rangeStart,
        fim: rangeEnd,
      },
    });

    if (response.status === 200) {
      const aulasMapped: CalendarEvent[] = response.data.map((aula, index: number) => {
        const disciplina = capitalizeWords(aula.disciplina);
        const professor = capitalizeWords(aula.professor);

        // Convert API ISO string to Temporal.ZonedDateTime in local timezone
        const start = Temporal.Instant.from(aula.inicio).toZonedDateTimeISO(localTz);
        const end = Temporal.Instant.from(aula.fim).toZonedDateTimeISO(localTz);

        return {
          id: index,
          start,
          end,
          title: `${disciplina} - ${professor}`,
        };
      });
      eventsServicePlugin.set(aulasMapped);
    }
  } catch (error) {
    console.error('Erro ao buscar aulas:', error);
  } finally {
    isSyncing.value = false;
  }
}

const calendarApp = createCalendar({
  selectedDate: Temporal.Now.plainDateISO(),
  views: [createViewDay(), createViewWeek()],
  locale: 'pt-BR',
  timezone: localTz,
  callbacks: {
    onRangeUpdate(range) {
      if (sala.value) {
        // Use unknown cast to satisfy TS because library types might slightly differ
        void getAulas(sala.value.code, range as unknown as TemporalRange);
      }
    },
  },
  dayBoundaries: {
    start: '07:00',
    end: '20:00',
  },
  weekOptions: {
    gridHeight: 800,
    nDays: 5,
  },
  defaultView: createViewWeek().name,
  plugins: [
    createCurrentTimePlugin(),
    eventsServicePlugin,
    calendarControlsPlugin
  ],
  events: [],
});

watch(sala, (newValue) => {
  if (newValue) {
    const range = calendarControlsPlugin.getRange();
    if (range) {
      void getAulas(newValue.code, range as unknown as TemporalRange);
    }
  }
});

onMounted(async () => {
  await getSalas();
  if (salas.value.length > 0) {
    sala.value = salas.value[0] || null;
  }
});
</script>

<template>
  <q-page class="calendar-page q-pa-md md:q-pa-xl">
    <div class="header-section q-mb-lg flex items-center justify-between no-wrap">
      <div>
        <h1 class="text-h3 text-weight-bold q-ma-none text-primary">Calendário de Aulas</h1>
        <p class="text-subtitle1 text-grey-7 q-ma-none">Visualize a ocupação das salas e laboratórios</p>
      </div>

      <div class="room-selector glass-card q-pa-sm">
        <q-select
          v-model="sala"
          :options="salas"
          label="Selecionar Sala"
          filled
          color="primary"
          style="min-width: 300px"
          class="custom-select"
        >
          <template v-slot:prepend>
            <q-icon name="mdi-door-open" color="primary" />
          </template>
        </q-select>
      </div>
    </div>

    <div class="calendar-container glass-card">
      <q-inner-loading :showing="isSyncing">
        <q-spinner-dots color="primary" size="4em" />
      </q-inner-loading>
      <ScheduleXCalendar :calendar-app="calendarApp" />
    </div>
  </q-page>
</template>

<style lang="scss">
.calendar-page {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.glass-card {
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  overflow: hidden;
}

.calendar-container {
  position: relative;
  min-height: 700px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(2px);
  z-index: 10;
}

/* Schedule-X Customizations for better contrast */
.sx__calendar {
  --sx-color-primary: var(--q-primary);
  --sx-color-on-primary: white;
  --sx-font-family: 'Inter', sans-serif;
}

.sx__time-grid-event {
  background: var(--q-primary) !important;
  color: white !important;
  border-radius: 6px !important;
  border-left: 4px solid darken(#1976D2, 10%) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.sx__time-grid-event-title {
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  line-height: 1.2 !important;
}

.sx__time-grid-event-time {
  opacity: 0.9;
  font-size: 0.8rem !important;
}

.sx__week-grid__day-header {
  border-bottom: 2px solid #eee !important;
  padding: 12px 0 !important;
}

.sx__week-grid__day-header-date {
  font-size: 1.2rem !important;
  font-weight: 700 !important;
}

.sx__week-grid__day-header-day {
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.75rem !important;
  color: #666;
}

/* Responsive adjustments */
@media (max-width: 900px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 16px;
  }

  .room-selector {
    width: 100%;

    .custom-select {
      min-width: 100% !important;
    }
  }

  .text-h3 {
    font-size: 2rem;
  }
}
</style>
