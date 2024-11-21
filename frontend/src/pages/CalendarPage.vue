<script setup lang="ts">
import { ScheduleXCalendar } from '@schedule-x/vue';
import { createCurrentTimePlugin } from '@schedule-x/current-time';
import { ref, watch, onMounted } from 'vue';
import { createEventsServicePlugin } from '@schedule-x/events-service';
import { createCalendarControlsPlugin } from '@schedule-x/calendar-controls';
import type { AxiosInstance, AxiosError } from 'axios';
import { axios, api } from 'boot/axios';
import { useQuasar } from 'quasar';
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
  'calendarId': string,
}

interface Range {
  'start': string,
  'end': string,
}

interface Sala {
  'label': string,
  'value': string
}

interface SalaResponse {
  'id': number,
  'predio': number,
  'nome': string,
  'numero': string,
  'codigo': string,
}

const showError = ref(false);
const errorMessage = ref<string>('');
const $q = useQuasar();

function displayError(message: string) {
  errorMessage.value = message;
  showError.value = true;
}

let aulasApi = [];

const sala = ref<Sala | null>(null);
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
        value: obj.codigo,
      }));
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
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
    throw error; // Rethrow the error
  }
}

async function getUserList(roomId: Sala, range: Range) {
  const rangeStart: string = range.start.split(' ')[0] as string;
  const rangeEnd: string = range.end.split(' ')[0] as string;

  // It seems that I have to add a day to pick up Friday.
  const rangeEndDate = new Date(rangeEnd);
  rangeEndDate.setDate(rangeEndDate.getDate() + 1);
  const rangeEndPlusOne = rangeEndDate.toISOString().slice(0, 10);

  try {
    const aulas: Aula[] = [];
    const response = await axios.post('https://oca.ctism.ufsm.br/ensalamento/getFullCalendar', {
      withCredentials: false,
      espaco: roomId,
      inicio: rangeStart,
      fim: rangeEndPlusOne,
      apenasDeferidos: true,
    });
    if (response.status === 200) {
      if (response.data.length !== 0) {
        aulasApi = response.data;
        aulasApi.forEach((aula: Aula, index: number) => {
          const titleSplit: string[] = (aula.title as string).split('-');
          const subject = capitalizeWords(titleSplit[0] as string);
          const lecturer = capitalizeWords(titleSplit.at(-1)!);
          const filtTitle = `${subject} - ${lecturer}`;
          const obj: Aula = {
            id: index, start: aula.start.slice(0, -3), end: aula.end.slice(0, -3), title: filtTitle, calendarId: 'work',
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
  } catch (error) {
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

const calendarApp = createCalendar({
  selectedDate: today.toISOString().slice(0, 10),
  views: [viewDay, viewWeek],
  locale: 'pt-BR',
  callbacks: {
    onRangeUpdate(range) {
      if (sala.value != null) {
        getUserList(sala.value, range);
      }
    },
  },
  dayBoundaries: {
    start: '07:30',
    end: '20:30',
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
    getUserList(newValue, calendarControlsPlugin.getRange() as Range);
  }
});

onMounted(() => {
  getSalas();
  const [firstSala] = salas.value;
  sala.value = firstSala as Sala;
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
