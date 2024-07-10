<script setup lang="ts">
import { ScheduleXCalendar } from '@schedule-x/vue';
import { createCurrentTimePlugin } from '@schedule-x/current-time';
import { ref, onMounted } from 'vue';
import { createEventsServicePlugin } from '@schedule-x/events-service';
import { createCalendarControlsPlugin } from '@schedule-x/calendar-controls';
import axios from 'axios';
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

let aulasApi = [];

const stringOptions = [
  'Informáticas',
];

const model = ref(null);
const options = ref(stringOptions);

function filterFn(val, update, abort) {
  update(() => {
    const needle = val.toLocaleLowerCase();
    options.value = stringOptions.filter(v => v.toLocaleLowerCase().indexOf(needle) > -1)
  });
}

const calendarControlsPlugin = createCalendarControlsPlugin();
const eventsServicePlugin = createEventsServicePlugin();

function capitalizeWords(str: string): string {
  return str
    .toLowerCase()
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

async function getUserList(range: Range) {
  const rangeStart: string = range.start.split(' ')[0];
  const rangeEnd: string = range.end.split(' ')[0];

  // It seems that I have to add a day to pick up Friday.
  const rangeEndDate = new Date(rangeEnd);
  rangeEndDate.setDate(rangeEndDate.getDate() + 1);
  const rangeEndPlusOne = rangeEndDate.toISOString().slice(0, 10);

  try {
    const response = await axios.post('https://oca.ctism.ufsm.br/ensalamento/getFullCalendar', {
      withCredentials: false,
      espaco: '3145',
      inicio: rangeStart,
      fim: rangeEndPlusOne,
      apenasDeferidos: true,
    });
    if (response.status === 200) {
      const aulas: Aula[] = [];
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
  selectedDate: '2024-07-10',
  views: [viewDay, viewWeek],
  locale: 'pt-BR',
  calendars: {
    work: {
      colorName: 'work',
      lightColors: {
        main: '#f91c45',
        container: '#ffd2dc',
        onContainer: '#59000d',
      },
      darkColors: {
        main: '#ffc0cc',
        onContainer: '#ffdee6',
        container: '#a24258',
      },
    },
  },
  callbacks: {
    onRangeUpdate(range) {
      getUserList(range);
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

onMounted(() => {
  getUserList(calendarControlsPlugin.getRange());
});
</script>

<template>
  <div class="q-pa-md">
    <div class="q-gutter-md row">
      <p class="text-h4">Escolha uma sala:</p>
      <q-select filled v-model="model" use-input hide-selected fill-input input-debounce="0"
      :options="options" @filter="filterFn" hint="Basic filtering" style="width: 250px;
      padding-bottom: 32px">
        <template v-slot:no-option>
          <q-item>
            <q-item-section class="text-grey">
              Nenhum resultado
            </q-item-section>
          </q-item>
        </template>
      </q-select>
    </div>
  </div>
  <div>
    <ScheduleXCalendar :calendar-app="calendarApp" />
  </div>
</template>

<style scoped>
#calendar {
  width: 50%;
  height: 400px;
  max-height: 90vh;
}
</style>
