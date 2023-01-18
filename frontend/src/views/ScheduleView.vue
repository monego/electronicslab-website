<!-- Agendamento de disciplinas -->

<template>

    <form>
        <label for="siape">SIAPE:</label>
        <input type="text" id="siape" name="siape">
    </form>

    <label for="disc">Disciplina:</label>

    <select name="disc" id="disc">
        <option value="disc1-1">[1-1] Acionamentos Elétricos</option>
        <option value="disc1-2">[1-2] Processos e Instrumentação</option>
        <option value="disc1-3">[1-3] Eletropneumática</option>
        <option value="disc1-6">[1-6] Máquinas Elétricas e Acionamentos</option>
    </select>

    <label for="labs">Laboratório:</label>

    <select name="labs" id="labs">
        <option value="lab1-1">[1-1] Acionamentos Elétricos</option>
        <option value="lab1-2">[1-2] Processos e Instrumentação</option>
        <option value="lab1-3">[1-3] Eletropneumática</option>
        <option value="lab1-6">[1-6] Máquinas Elétricas e Acionamentos</option>
    </select>

    <label for="observacao">Observação:</label>
    <textarea id="observacao" placeholder="Liste aqui os softwares, componentes, equipamentos, etc. que serão necessários para a aula. Caso prefira, o roteiro da aula pode ser anexado abaixo."></textarea>


    <label for="alunos">Alunos:</label>

    <input id="alunos" value="1" min="1" max="40" type="number" />

    <button id="cancelar" type="button">Cancelar</button>
    <button id="confirmar" type="button">Confirmar agendamento</button>

    <Datepicker v-model="date" range multiCalendars />

</template>

<script>

 import { ref, onMounted } from 'vue';
 import Datepicker from '@vuepic/vue-datepicker';
 import '@vuepic/vue-datepicker/dist/main.css';

 export default {

    setup() {
        const date = ref();

        onMounted(() => {
          const startDate = new Date();
          const endDate = new Date(new Date().setDate(startDate.getDate() + 7));
          date.value = [startDate, endDate];
        })

        return {
          date,
        }
    }
 }

</script>

<style>
</style>
