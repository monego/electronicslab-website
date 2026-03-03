<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, inject, type Ref } from 'vue';
import { api } from 'boot/axios';
import QuadranteAulas from 'src/components/QuadranteAulas.vue';

// Types
interface Aula {
  id: number;
  professor: string;
  disciplina: string;
  inicio: string;
  fim: string;
  sala_nome: string;
  sala_numero: string;
  sala_andar: number;
}

// Injected State from Layout
const currentTime = inject<Ref<Date>>('currentTime') || ref(new Date());

// State
const aulas = ref<Aula[]>([]);
const loading = ref(true);

let dataInterval: number;

// Data fetching
const fetchData = async () => {
  try {
    const response = await api.get<Aula[]>('/aulas/aulas/hoje/');
    aulas.value = response.data;
  } catch (error) {
    console.error('Erro ao buscar aulas para o telão do hall:', error);
  } finally {
    loading.value = false;
  }
};

// Computed
const aulasAndar1 = computed(() => {
  const now = currentTime.value;
  return aulas.value.filter((a) => a.sala_andar === 1 && new Date(a.fim) > now);
});
const aulasAndar2 = computed(() => {
  const now = currentTime.value;
  return aulas.value.filter((a) => a.sala_andar === 2 && new Date(a.fim) > now);
});

onMounted(() => {
  void fetchData();
  dataInterval = window.setInterval(() => {
    void fetchData();
  }, 300000); // Update every 5 minutes
});

onUnmounted(() => {
  clearInterval(dataInterval);
});
</script>

<template>
  <q-page class="q-pa-md">
    <div class="grid-container">
      <!-- (0,0) Andar 1 -->
      <QuadranteAulas :aulas="aulasAndar1" :andar="1" :currentTime="currentTime" />

      <!-- (0,1) Andar 2 -->
      <QuadranteAulas :aulas="aulasAndar2" :andar="2" :currentTime="currentTime" />
    </div>
  </q-page>
</template>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  height: calc(1080px - 148px);
  width: 100%;
}
</style>
