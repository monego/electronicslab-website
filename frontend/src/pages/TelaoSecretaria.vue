<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, inject, watch, nextTick, useTemplateRef, type Ref } from 'vue';
import { api } from 'boot/axios';
import { format, parseISO } from 'date-fns';
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

interface Ausencia {
  id: number;
  funcionario_nome: string;
  inicio: string;
  fim: string;
  motivo: string;
}

interface HorarioTrabalho {
  id: number;
  funcionario: number;
  funcionario_nome: string;
  dia_da_semana: string;
  inicio: string;
  fim: string;
  inicio_intervalo: string | null;
  fim_intervalo: string | null;
}

// Injected State from Layout
const currentTime = inject<Ref<Date>>('currentTime') || ref(new Date());

// State
const aulas = ref<Aula[]>([]);
const ausencias = ref<Ausencia[]>([]);
const horarios = ref<HorarioTrabalho[]>([]);
const loading = ref(true);

let dataInterval: number;

// Data fetching
const fetchData = async () => {
  try {
    const [aulasRes, ausenciasRes, horariosRes] = await Promise.all([
      api.get<Aula[]>('/aulas/aulas/hoje/'),
      api.get<Ausencia[]>('/controle/ausencia/'),
      api.get<HorarioTrabalho[]>('/controle/horarios/?all=true'),
    ]);

    aulas.value = aulasRes.data;
    ausencias.value = ausenciasRes.data;
    horarios.value = horariosRes.data;
  } catch (error) {
    console.error('Erro ao buscar dados do telão:', error);
  } finally {
    loading.value = false;
  }
};

// Computed
// Computed
const aulasAndar1 = computed(() => {
  const now = currentTime.value;
  return aulas.value.filter((a) => a.sala_andar === 1 && parseISO(a.fim) > now);
});
const aulasAndar2 = computed(() => {
  const now = currentTime.value;
  return aulas.value.filter((a) => a.sala_andar === 2 && parseISO(a.fim) > now);
});

const dayOfWeekMap: Record<number, string> = {
  1: 'segunda',
  2: 'terca',
  3: 'quarta',
  4: 'quinta',
  5: 'sexta',
};

const processedHorarios = computed(() => {
  const todayNum = currentTime.value.getDay();
  const todayStr = dayOfWeekMap[todayNum] || 'segunda';

  return horarios.value
    .filter((h) => h.dia_da_semana === todayStr)
    .sort((a, b) => a.funcionario_nome.localeCompare(b.funcionario_nome));
});

// Gantt & Time Helpers
const startTimeLimit = '07:30:00';
const totalMinutes = 12 * 60; // 07:30 to 19:30

const timeToMinutes = (timeStr: string) => {
  const parts = timeStr.split(':').map(Number);
  const h = parts[0] ?? 0;
  const m = parts[1] ?? 0;
  return h * 60 + m;
};

const getPosition = (timeStr: string) => {
  const startLimitMinutes = timeToMinutes(startTimeLimit);
  const minutes = timeToMinutes(timeStr);
  const relativeMinutes = Math.max(0, minutes - startLimitMinutes);
  return (relativeMinutes / totalMinutes) * 100;
};

const getWidth = (start: string, end: string) => {
  const startMin = timeToMinutes(start);
  const endMin = timeToMinutes(end);
  const duration = Math.max(0, endMin - startMin);
  return (duration / totalMinutes) * 100;
};

// Break position/width relative to parent work block
const getBreakStyle = (workStart: string, workEnd: string, breakStart: string, breakEnd: string) => {
  const workStartMin = timeToMinutes(workStart);
  const workEndMin = timeToMinutes(workEnd);
  const workDuration = workEndMin - workStartMin;
  if (workDuration <= 0) return { left: '0%', width: '0%' };

  const breakStartMin = timeToMinutes(breakStart);
  const breakEndMin = timeToMinutes(breakEnd);
  const leftPct = ((breakStartMin - workStartMin) / workDuration) * 100;
  const widthPct = ((breakEndMin - breakStartMin) / workDuration) * 100;
  return { left: `${leftPct}%`, width: `${widthPct}%` };
};

const hoursArray = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19];

// Auto-scroll refs
const ganttRowsRef = useTemplateRef<HTMLElement>('ganttRowsRef');
const ganttRowsInnerRef = useTemplateRef<HTMLElement>('ganttRowsInnerRef');
const ausenciasListRef = useTemplateRef<HTMLElement>('ausenciasListRef');
const ausenciasInnerRef = useTemplateRef<HTMLElement>('ausenciasInnerRef');

const updateAutoScroll = (container: HTMLElement | null, inner: HTMLElement | null) => {
  if (!container || !inner) return;
  const overflow = inner.scrollHeight - container.clientHeight;
  if (overflow > 0) {
    inner.style.setProperty('--scroll-distance', `-${overflow}px`);
    inner.style.animationPlayState = 'running';
  } else {
    inner.style.setProperty('--scroll-distance', '0px');
    inner.style.animationPlayState = 'paused';
  }
};

watch([processedHorarios, ausencias], () => {
  void nextTick(() => {
    updateAutoScroll(ganttRowsRef.value, ganttRowsInnerRef.value);
    updateAutoScroll(ausenciasListRef.value, ausenciasInnerRef.value);
  });
}, { immediate: true, deep: true });

onMounted(() => {
  void fetchData();
  dataInterval = window.setInterval(() => {
    void fetchData();
  }, 300000); // Update data from backend every 5 minutes
});

onUnmounted(() => {
  clearInterval(dataInterval);
});
</script>

<template>
  <q-page class="q-pa-md">
    <!-- Main Grid -->
    <main class="grid-container">
      <!-- (0,0) Andar 1 -->
      <QuadranteAulas :aulas="aulasAndar1" :andar="1" :currentTime="currentTime" />

      <!-- (0,1) Andar 2 -->
      <QuadranteAulas :aulas="aulasAndar2" :andar="2" :currentTime="currentTime" />

      <!-- (1,0) Escala de Trabalho -->
      <section class="quadrant q-pa-md">
        <h2 class="text-h5 q-mb-sm flex items-center">
          <q-icon name="mdi-calendar-clock" class="q-mr-sm" color="green" />
          Escala de Funcionários
        </h2>
        <div class="gantt-container">
          <!-- Timeline Header -->
          <div class="gantt-header row no-wrap">
            <div class="name-col-header">Funcionário</div>
            <div class="chart-col-header row no-wrap relative-position">
              <div v-for="hour in hoursArray" :key="hour" class="hour-mark" :style="{ left: getPosition(`${hour < 10 ? '0'+hour : hour}:00:00`) + '%' }">
                {{ hour }}:00
              </div>
            </div>
          </div>

          <div ref="ganttRowsRef" class="gantt-rows">
            <div ref="ganttRowsInnerRef" class="gantt-rows-inner">
              <div v-for="h in processedHorarios" :key="h.id" class="gantt-row row no-wrap items-center">
                <div class="name-col text-subtitle1">{{ h.funcionario_nome }}</div>
                <div class="chart-col relative-position">
                  <!-- Grid Lines -->
                  <div class="grid-line" :style="{ left: '0%' }"></div>
                  <div v-for="hour in hoursArray" :key="hour" class="grid-line" :style="{ left: getPosition(`${hour < 10 ? '0'+hour : hour}:00:00`) + '%' }"></div>
                  <div class="grid-line" :style="{ left: '100%' }"></div>

                  <!-- Current Time Marker -->
                  <div
                      v-if="currentTime.getHours() >= 7 && currentTime.getHours() <= 19"
                      class="now-marker"
                      :style="{ left: getPosition(format(currentTime, 'HH:mm:ss')) + '%' }"
                  ></div>

                  <!-- Work Block -->
                  <div
                    class="work-block"
                    :style="{
                      left: getPosition(h.inicio) + '%',
                      width: getWidth(h.inicio, h.fim) + '%'
                    }"
                  >
                    <!-- Break Block (if exists) -->
                    <div
                      v-if="h.inicio_intervalo && h.fim_intervalo"
                      class="break-block"
                      :style="getBreakStyle(h.inicio, h.fim, h.inicio_intervalo, h.fim_intervalo)"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- (1,1) Ausências -->
      <section class="quadrant q-pa-md">
        <h2 class="text-h5 q-mb-sm flex items-center">
          <q-icon name="mdi-account-off" class="q-mr-sm" color="red" />
          Ausências
        </h2>
        <div ref="ausenciasListRef" class="content-list">
          <div ref="ausenciasInnerRef" class="content-list-inner">
            <div v-if="ausencias.length === 0" class="empty-state text-h6 text-grey-5">
              Nenhuma ausência registrada
            </div>
            <div v-for="aus in ausencias" :key="aus.id" class="item-card q-mb-sm q-pa-sm red-border">
              <div class="row items-center justify-between">
                <div class="text-h6 text-weight-bold text-red">{{ aus.funcionario_nome }}</div>
                <div class="text-subtitle1 text-grey-4">
                  {{ format(parseISO(aus.inicio), 'dd/MM') }} - {{ format(parseISO(aus.fim), 'dd/MM') }}
                </div>
              </div>
              <div class="text-subtitle1 text-white q-mt-xs">{{ aus.motivo }}</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </q-page>
</template>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 12px;
  height: calc(1080px - 148px);
  width: 100%;
}

.quadrant {
  background: rgba(22, 27, 34, 0.5);
  border: 1px solid #30363d;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-list {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.content-list-inner,
.gantt-rows-inner {
  animation: autoScroll 20s ease-in-out infinite;
}

@keyframes autoScroll {
  0%, 15% {
    transform: translateY(0);
  }
  45%, 55% {
    transform: translateY(var(--scroll-distance, 0px));
  }
  85%, 100% {
    transform: translateY(0);
  }
}

.item-card {
  background: rgba(48, 54, 61, 0.3);
  border-left: 6px solid #30363d;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.red-border {
  border-left-color: #ff4444;
}

/* Gantt Chart Styles */
.gantt-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.gantt-header {
  height: 30px;
  border-bottom: 1px solid #30363d;
  margin-bottom: 6px;
  align-items: center;
}

.name-col-header {
  width: 180px;
  padding-left: 8px;
  font-weight: bold;
  font-size: 13px;
}

.chart-col-header {
  flex: 1;
}

.hour-mark {
  position: absolute;
  transform: translateX(-50%);
  font-size: 12px;
  color: #8b949e;
}

.gantt-rows {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.gantt-row {
  height: 48px;
  border-bottom: 1px solid #21262d;
}

.name-col {
  width: 180px;
  padding-left: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chart-col {
  flex: 1;
  height: 100%;
}

.grid-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(48, 54, 61, 0.3);
}

.now-marker {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #ff4444;
    z-index: 2;
    box-shadow: 0 0 8px rgba(255, 68, 68, 0.6);
}

.work-block {
  position: absolute;
  top: 12px;
  height: 24px;
  background: linear-gradient(90deg, #238636, #2ea043);
  border-radius: 4px;
  box-shadow: 0 0 10px rgba(46, 160, 67, 0.4);
  z-index: 1;
}

.break-block {
  position: absolute;
  top: 0;
  height: 100%;
  background: rgba(13, 17, 20, 0.7);
  border-left: 1px solid rgba(255,255,255,0.1);
  border-right: 1px solid rgba(255,255,255,0.1);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
