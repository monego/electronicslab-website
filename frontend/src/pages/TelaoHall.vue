<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, inject, type Ref } from 'vue';
import { useRoute } from 'vue-router';
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

const route = useRoute();
const filteredAndar = computed(() => {
  const andarParam = route.query.andar;
  if (andarParam === '1' || andarParam === '2') {
    return parseInt(andarParam as string);
  }
  return null; // No valid andar param
});

const isSingleQuadrant = computed(() => filteredAndar.value !== null);

const layoutParams = computed(() => {
  const layoutQuery = route.query.layout as string || '';
  const parts = layoutQuery.split('-');
  
  let baseLayout = 'vertical';
  let isInverted = false;
  let hasPriorityFlag = false;

  for (const part of parts) {
    if (part === 'vertical' || part === 'horizontal') {
      baseLayout = part;
    } else if (part === 'i') {
      isInverted = true;
    } else if (part === 'p') {
      hasPriorityFlag = true;
    }
  }

  // Validate layout combinations
  if (hasPriorityFlag && baseLayout !== 'horizontal') {
    hasPriorityFlag = false; // Priority flag only applies to horizontal layouts
  }

  return { baseLayout, isInverted, hasPriorityFlag };
});

const currentBaseLayout = computed(() => layoutParams.value.baseLayout);
const isInverted = computed(() => layoutParams.value.isInverted);
const hasPriorityFlag = computed(() => layoutParams.value.hasPriorityFlag);


const gridClasses = computed(() => {
  const classes = ['grid-container'];
  if (isSingleQuadrant.value) {
    classes.push('single-quadrant-grid');
  } else {
    if (currentBaseLayout.value === 'horizontal') {
      classes.push('grid-horizontal');
      if (hasPriorityFlag.value) {
        classes.push('grid-horizontal-priority');
      }
    } else { // vertical
      classes.push('grid-vertical');
    }
  }
  return classes;
});

const isLargeLayout = computed(() => {
  return isSingleQuadrant.value || currentBaseLayout.value === 'horizontal';
});

const quadrantSizeMultiplier = computed(() => {
  return isLargeLayout.value ? 1.15 : 1.0; // 1.15x multiplier for large layouts
});

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
    <div :class="gridClasses">
      <template v-if="isSingleQuadrant">
        <QuadranteAulas
          v-if="filteredAndar === 1"
          :aulas="aulasAndar1"
          :andar="1"
          :currentTime="currentTime"
          :isSingleQuadrant="isSingleQuadrant"
          :isLargeLayout="isLargeLayout"
          :quadrantSizeMultiplier="quadrantSizeMultiplier"
        />
        <QuadranteAulas
          v-else-if="filteredAndar === 2"
          :aulas="aulasAndar2"
          :andar="2"
          :currentTime="currentTime"
          :isSingleQuadrant="isSingleQuadrant"
          :isLargeLayout="isLargeLayout"
          :quadrantSizeMultiplier="quadrantSizeMultiplier"
        />
      </template>
      <template v-else>
        <!-- Render 2nd Quadrant first for inverse layouts -->
        <template v-if="isInverted">
          <QuadranteAulas
            :aulas="aulasAndar2"
            :andar="2"
            :currentTime="currentTime"
            :isSingleQuadrant="isSingleQuadrant"
            :isLargeLayout="isLargeLayout"
            :quadrantSizeMultiplier="quadrantSizeMultiplier"
          />
          <QuadranteAulas
            :aulas="aulasAndar1"
            :andar="1"
            :currentTime="currentTime"
            :isSingleQuadrant="isSingleQuadrant"
            :isLargeLayout="isLargeLayout"
            :quadrantSizeMultiplier="quadrantSizeMultiplier"
          />
        </template>
        <!-- Render 1st Quadrant first for default layouts -->
        <template v-else>
          <QuadranteAulas
            :aulas="aulasAndar1"
            :andar="1"
            :currentTime="currentTime"
            :isSingleQuadrant="isSingleQuadrant"
            :isLargeLayout="isLargeLayout"
            :quadrantSizeMultiplier="quadrantSizeMultiplier"
          />
          <QuadranteAulas
            :aulas="aulasAndar2"
            :andar="2"
            :currentTime="currentTime"
            :isSingleQuadrant="isSingleQuadrant"
            :isLargeLayout="isLargeLayout"
            :quadrantSizeMultiplier="quadrantSizeMultiplier"
          />
        </template>
      </template>
    </div>
  </q-page>
</template>

<style scoped>
.grid-container {
  display: grid;
  gap: 12px;
  height: calc(100vh - 148px);
  width: 100%;
}

.single-quadrant-grid {
  grid-template-columns: 1fr;
  gap: 0;
}

.grid-vertical {
  grid-template-columns: 1fr 1fr;
}

.grid-horizontal {
  grid-template-columns: 1fr;
  grid-template-rows: 1fr 1fr;
}

.grid-horizontal-priority {
  grid-template-rows: 65% 35%; /* 65% for top, 35% for bottom */
}
</style>
