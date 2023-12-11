<!-- Calendário para consulta de horário de aulas -->

<script>
import { ref } from 'vue';
import Datepicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import VueCal from 'vue-cal'
import 'vue-cal/dist/vuecal.css'

export default {

    components: { Datepicker, VueCal },

    setup() {
        const date = ref();

        return {
            date,
        }
    },

    data: () => ({
        events: [
            {
                start: '2022-10-24 08:30',
                end: '2022-10-24 12:30',
                title: 'Alguma aula'
            },
            {
                start: '2022-10-25 08:30',
                end: '2022-10-25 10:30',
                title: 'Aula outra aula'
            },
            {
                start: '2022-10-25 10:30',
                end: '2022-10-25 12:30',
                title: 'Terceira aula'
            },
        ]
    })
}
</script>

<template>
    <label for="labs">Laboratório:</label>

    <select name="labs" id="labs">
        <option value="lab1-1">[1-1] Acionamentos Elétricos</option>
        <option value="lab1-2">[1-2] Processos e Instrumentação</option>
        <option value="lab1-3">[1-3] Eletropneumática</option>
        <option value="lab1-6">[1-6] Máquinas Elétricas e Acionamentos</option>
    </select>

    <div class="md:mx-48">
        <vue-cal small hide-view-selector hide-weekends :time-from="7.5 * 60" :time-to="19.5 * 60" :events="events"
            active-view="week" locale="pt-br" :disable-views="['years', 'day', 'year', 'month']" />
    </div>
</template>
