<script setup lang="ts">
import { ScheduleXCalendar } from '@schedule-x/vue';
import { createCurrentTimePlugin } from '@schedule-x/current-time';
import { ref, reactive, watch, onMounted } from 'vue';
import { createEventsServicePlugin } from '@schedule-x/events-service';
import { createCalendarControlsPlugin } from '@schedule-x/calendar-controls';
import { AxiosInstance } from 'axios';
import { axios, api } from 'boot/axios';
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
      salas.value = response.data.map((obj) => ({
        label: `[${obj.numero}] ${obj.nome}`,
        value: obj.codigo,
      }));
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      console.error(`Axios Error: ${error.message}`);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`); // Formatted JSON
      }
    } else {
      console.error(`Error: ${error.message}`);
    }
    throw error; // Rethrow the error
  }
}

async function getUserList(roomId: string, range: Range) {
  const rangeStart: string = range.start.split(' ')[0];
  const rangeEnd: string = range.end.split(' ')[0];

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
        aulasApi.forEach((aula, index) => {
          const titleSplit = aula.title.split('-');
          const subject = capitalizeWords(titleSplit[0]);
          const lecturer = capitalizeWords(titleSplit.at(-1));
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
      console.error(`Axios Error: ${error.message}`);
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`);
      }
    } else {
      console.error(`Error: ${error}`);
    }
    throw error;
  }
}

const calendarApp = createCalendar({
  selectedDate: today.toISOString().slice(0, 10),
  views: [viewDay, viewWeek],
  locale: 'pt-BR',
  // calendars: {
  //   work: {
  //     colorName: 'work',
  //     lightColors: {
  //       main: '#d91c45',
  //       container: '#0fd2dc',
  //       onContainer: '#09000d',
  //     },
  //     darkColors: {
  //       main: '#ffc0cc',
  //       onContainer: '#ffdee6',
  //       container: '#a24258',
  //     },
  //   },
  // },
  callbacks: {
    onRangeUpdate(range) {
      getUserList(sala.value, range);
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
  getUserList(newValue, calendarControlsPlugin.getRange());
});

onMounted(() => {
  getSalas();
  // getUserList('3143', calendarControlsPlugin.getRange());
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
    <ScheduleXCalendar :calendar-app="calendarApp" />
  </q-card>
</template>

<style lang="scss">
body {
  background-color: #eeeeee; /* Cinza claro */
}
#calendar {
  width: 50%;
  height: 400px;
  max-height: 90vh;
}
.sx__time-grid-event-title {
  font-weight: normal;
  font-size: medium;
}
</style>
