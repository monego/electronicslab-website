<script setup lang="ts">
import { format, parseISO, isWithinInterval } from 'date-fns';

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

const props = defineProps<{
  aulas: Aula[];
  andar: number;
  currentTime: Date;
}>();

const isAulaActive = (aula: Aula) => {
  const start = parseISO(aula.inicio);
  const end = parseISO(aula.fim);
  return isWithinInterval(props.currentTime, { start, end });
};
</script>

<template>
  <section class="quadrant q-pa-lg">
    <h2 class="text-h4 q-mb-md flex items-center">
      <q-icon
        :name="andar === 1 ? 'mdi-stairs-up' : 'mdi-stairs-up'"
        class="q-mr-sm"
        :color="andar === 1 ? 'cyan' : 'orange'"
      />
      Aulas - {{ andar }}º Andar
    </h2>
    <div class="content-list">
      <div v-if="aulas.length === 0" class="empty-state text-h5 text-grey-5">
        Nenhuma aula programada
      </div>
      <div
        v-for="aula in aulas"
        :key="aula.id"
        class="item-card q-mb-md q-pa-md"
        :class="{
          'active-aula': andar === 1 && isAulaActive(aula),
          'active-aula-orange': andar === 2 && isAulaActive(aula),
          'orange-border': andar === 2 && !isAulaActive(aula)
        }"
      >
        <div class="row items-center justify-between">
          <div class="text-h5 text-weight-bold" :class="andar === 1 ? 'text-cyan' : 'text-orange'">
            {{ aula.disciplina }}
            <q-badge v-if="isAulaActive(aula)" :color="andar === 1 ? 'cyan' : 'orange'" label="AO VIVO" class="q-ml-sm" />
          </div>
          <div class="text-h5 text-weight-medium">[Sala {{ aula.sala_numero }}]</div>
        </div>
        <div class="row justify-between items-center q-mt-xs">
          <div class="text-h6 text-grey-4">{{ aula.professor }}</div>
          <div class="text-h6 text-weight-bold text-white">
            {{ format(parseISO(aula.inicio), 'HH:mm') }} - {{ format(parseISO(aula.fim), 'HH:mm') }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
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
  overflow-y: auto;
}

.item-card {
  background: rgba(48, 54, 61, 0.3);
  border-left: 8px solid #30363d;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.active-aula {
  border-left-color: #00f2ff;
  background: rgba(0, 242, 255, 0.1);
  box-shadow: 0 0 15px rgba(0, 242, 255, 0.1);
}

.active-aula-orange {
  border-left-color: #ff9d00;
  background: rgba(255, 157, 0, 0.1);
  box-shadow: 0 0 15px rgba(255, 157, 0, 0.1);
}

.orange-border {
  border-left-color: #30363d;
}

.item-card.orange-border.active-aula-orange {
    border-left-color: #ff9d00;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #484f58;
}
</style>
