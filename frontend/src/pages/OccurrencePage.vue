<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { format } from 'date-fns';
import { api, axios } from 'boot/axios';
import { AxiosInstance, AxiosError } from 'axios';

const today = new Date();
const formattedDate = format(today, 'yyyy/MM/dd');

type DateModel = {
  from: string;
  to: string;
} | string;

type Jornada = {
  segunda: (string | null)[],
  terca: (string | null)[],
  quarta: (string | null)[],
  quinta: (string | null)[],
  sexta: (string | null)[],
}

const model = ref<DateModel>(formattedDate);
const motivo = ref<string>('');
const horarios = ref<Jornada>({
  segunda: [null, null, null, null],
  terca: [null, null, null, null],
  quarta: [null, null, null, null],
  quinta: [null, null, null, null],
  sexta: [null, null, null, null],
});

async function getHorarios() {
  try {
    const response = await (api as AxiosInstance).get('/controle/horarios');

    if (response.status === 200) {
      Object.keys(horarios.value).forEach((day, index) => {
        const inicio = response.data[index].inicio;
        const inicioIntervalo = response.data[index].inicio_intervalo;
        const fimIntervalo = response.data[index].fim_intervalo;
        const fim = response.data[index].fim;
        const diaDaSemana = response.data[index].dia_da_semana;
        horarios.value[diaDaSemana] = [inicio, inicioIntervalo, fimIntervalo, fim];
      });
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.log(error);
      }
    } else {
      console.log(error);
    }
    throw error;
  }
}

async function patchHorarios(day: string, hour: (string | null)[]) {
  try {
    const response = await (api as AxiosInstance).patch('/controle/horarios/byday/', {
      dia: day,
      inicio: hour[0],
      inicio_intervalo: hour[1],
      fim_intervalo: hour[2],
      fim: hour[3],
    });

    await getHorarios();

    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.log(error);
      }
    } else {
      console.log(error);
    }
    throw error;
  }
}

async function setAusencia(time: DateModel, reason: string) {
  try {
    let from: string;
    let to: string;

    if (typeof time === 'string') {
      from = format(time, 'yyyy-MM-dd');
      to = format(time, 'yyyy-MM-dd');
    } else {
      from = format(time.from, 'yyyy-MM-dd');
      to = format(time.to, 'yyyy-MM-dd');
    }

    const data = {
      inicio: from,
      fim: to,
      motivo: reason,
    };

    const response = await (api as AxiosInstance).post('/controle/ausencia/', data);

    if (response.status === 201) {
      console.log("Success!");
    } else {
      throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.log(error);
      }
    } else {
      console.log(error);
    }
    throw error;
  }
}

onMounted(() => {
  getHorarios();
});
</script>

<template>
  <div class="q-pa-md">
    <div class="q-pb-sm">
      <div class="flex flex-1">
        <div>
          <p>Ocorrências</p>

          <q-date v-model="model" range />

          <q-input v-model="motivo" label="Motivo" />

          <q-btn color="primary" label="Registrar" @click="setAusencia(model, motivo)" />
        </div>
        <div>
          <p>Jornada</p>
          <div class="flex flex-1">
            <p>Segunda-feira</p>
            <q-input v-model="horarios.segunda[0]" filled type="time" hint="Início" />
            <q-input v-model="horarios.segunda[1]" filled type="time" hint="Saída" />
            <q-input v-model="horarios.segunda[2]" filled type="time" hint="Entrada" />
            <q-input v-model="horarios.segunda[3]" filled type="time" hint="Fim" />
            <q-btn color="primary" label="Atualizar"
            @click="patchHorarios('segunda', horarios.segunda)" />
          </div>
          <div class="flex">
            Terça-feira
            <q-input v-model="horarios.terca[0]" filled type="time" hint="Início" />
            <q-input v-model="horarios.terca[1]" filled type="time" hint="Saída" />
            <q-input v-model="horarios.terca[2]" filled type="time" hint="Entrada" />
            <q-input v-model="horarios.terca[3]" filled type="time" hint="Fim" />
            <q-btn color="primary" label="Atualizar"
            @click="patchHorarios('terca', horarios.terca)" />
          </div>
          <div class="flex">
            Quarta-feira
            <q-input v-model="horarios.quarta[0]" filled type="time" hint="Início" />
            <q-input v-model="horarios.quarta[1]" filled type="time" hint="Saída" />
            <q-input v-model="horarios.quarta[2]" filled type="time" hint="Entrada" />
            <q-input v-model="horarios.quarta[3]" filled type="time" hint="Fim" />
            <q-btn color="primary" label="Atualizar"
            @click="patchHorarios('quarta', horarios.quarta)" />
          </div>
          <div class="flex">
            Quinta-feira
            <q-input v-model="horarios.quinta[0]" filled type="time" hint="Início" />
            <q-input v-model="horarios.quinta[1]" filled type="time" hint="Saída" />
            <q-input v-model="horarios.quinta[2]" filled type="time" hint="Entrada" />
            <q-input v-model="horarios.quinta[3]" filled type="time" hint="Fim" />
            <q-btn color="primary" label="Atualizar"
            @click="patchHorarios('quinta', horarios.quinta)" />
          </div>
          <div class="flex">
            Sexta-feira
            <q-input v-model="horarios.sexta[0]" filled type="time" hint="Início" />
            <q-input v-model="horarios.sexta[1]" filled type="time" hint="Saída" />
            <q-input v-model="horarios.sexta[2]" filled type="time" hint="Entrada" />
            <q-input v-model="horarios.sexta[3]" filled type="time" hint="Fim" />
            <q-btn color="primary" label="Atualizar"
            @click="patchHorarios('sexta', horarios.sexta)" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.flex-1 {
  justify-content: space-evenly;
}
</style>
