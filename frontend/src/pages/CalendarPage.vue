<script setup lang="ts">
import { ScheduleXCalendar } from '@schedule-x/vue';
import { createCurrentTimePlugin } from '@schedule-x/current-time';
import { ref, watch, onMounted } from 'vue';
import { createEventsServicePlugin } from '@schedule-x/events-service';
import { createCalendarControlsPlugin } from '@schedule-x/calendar-controls';
import type { AxiosInstance } from 'axios';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import { parseISO, format } from 'date-fns';
import {
  createCalendar,
  viewDay,
  viewWeek,
} from '@schedule-x/calendar';
import '@schedule-x/theme-default/dist/index.css';

interface Aula {
  'id': number,
  'start': string,
  'end': string,
  'title': string,
}

interface Range {
  'start': string,
  'end': string,
}

interface Sala {
  'label': string,
  'code': string
}

interface SalaResponse {
  'id': number,
  'predio': number,
  'nome': string,
  'numero': string,
  'codigo': string,
}

const $q = useQuasar();

let aulasApi = [];

const sala = ref<Sala>();
const salas = ref<Sala[]>([]);

const today = new Date();

const calendarControlsPlugin = createCalendarControlsPlugin();
const eventsServicePlugin = createEventsServicePlugin();

function capitalizeWords(str: string): string {
  return str
    .toLowerCase()
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

async function getSalas() {
  try {
    const response = await (api as AxiosInstance).get('/root/salas');

    if (response.status === 200) {
      salas.value = response.data.map((obj: SalaResponse) => ({
        label: `[${obj.numero}] ${obj.nome}`,
        code: obj.codigo,
      }));
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro na comunicação com o servidor. Consulte o desenvolvedor.',
      timeout: 2500,
    });
  }
}

async function getUserList(roomId: string, range: Range) {
  const rangeStart: string = range.start.split(' ')[0] as string;
  const rangeEnd: string = range.end.split(' ')[0] as string;

  // It seems that I have to add a day to pick up Friday.
  const rangeEndDate = new Date(rangeEnd);
  rangeEndDate.setDate(rangeEndDate.getDate() + 1);
  const rangeEndPlusOne = rangeEndDate.toISOString().slice(0, 10);

  try {
    const aulas: Aula[] = [];
    const response = await (api as AxiosInstance).get('/aulas/aulas/calendario', {
      params: {
        codigo: roomId,
        inicio: rangeStart,
        fim: rangeEndPlusOne,
      },
      withCredentials: false,
    });
    if (response.status === 200) {
      if (response.data.length !== 0) {
        aulasApi = response.data;
        aulasApi.forEach((aula: {
          inicio: string,
          fim: string,
          disciplina: string,
          professor: string
        }, index: number) => {
          const disciplina = capitalizeWords(aula.disciplina);
          const professor = capitalizeWords(aula.professor);

          const obj: Aula = {
            id: index,
            start: format(parseISO(aula.inicio), 'yyyy-MM-dd HH:mm'),
            end: format(parseISO(aula.fim), 'yyyy-MM-dd HH:mm'),
            title: `${disciplina} - ${professor}`,
          };

          aulas.push(obj);

          eventsServicePlugin.set(aulas);
        });
      } else {
        eventsServicePlugin.set([]);
      }
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    $q.notify({
      type: 'negative',
      message: 'Erro na comunicação com o servidor. Consulte o desenvolvedor.',
      timeout: 2500,
    });
  }
}

const calendarApp = createCalendar({
  selectedDate: today.toISOString().slice(0, 10),
  views: [viewDay, viewWeek],
  locale: 'pt-BR',
  callbacks: {
    onRangeUpdate(range) {
      if (sala.value != null) {
        getUserList(sala.value.code, range);
      }
    },
  },
  dayBoundaries: {
    start: '07:00',
    end: '21:00',
  },
  weekOptions: {
    gridHeight: 500,
    nDays: 5,
  },
  defaultView: viewWeek.name,
  plugins: [createCurrentTimePlugin(),
    eventsServicePlugin,
    calendarControlsPlugin],
  events: [],
});

watch(sala, (newValue) => {
  if (newValue != null) {
    getUserList(newValue.code, calendarControlsPlugin.getRange() as Range);
  }
});

onMounted(async () => {
  await getSalas();
  const [firstSala] = salas.value;
  sala.value = firstSala;
  if (sala.value != null) {
    await getUserList(sala.value.code, calendarControlsPlugin.getRange() as Range);
  }
});
</script>

<template>
  <q-card class="flex flex-center full-height">
    <q-card class="q-pa-md">
      <q-card class="row no-wrap justify-center">
        <q-card>
          <q-select v-model="sala" :options="salas" emit-value map-options label="Escolha uma sala" />
        </q-card>
      </q-card>
    </q-card>
  </q-card>
  <q-card>
    <div :class="{ 'q-mx-xl q-my-md': !$q.platform.is.mobile }">
      <ScheduleXCalendar :calendar-app="calendarApp" />
    </div>
  </q-card>
</template>

<style lang="scss">
body {
  background-color: #eeeeee;
  /* Cinza claro */
}

.sx__time-grid-event-title {
  font-weight: normal;
  font-size: medium;
}
</style>
