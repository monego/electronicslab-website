<script setup lang="ts">
import { watch, nextTick, useTemplateRef } from 'vue';
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

// Auto-scroll: calculate how far to scroll based on content overflow
const contentListRef = useTemplateRef<HTMLElement>('contentListRef');
const contentInnerRef = useTemplateRef<HTMLElement>('contentInnerRef');

const updateScrollDistance = () => {
  const container = contentListRef.value;
  const inner = contentInnerRef.value;
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

watch(() => props.aulas, () => {
  void nextTick(updateScrollDistance);
}, { immediate: true, deep: true });
</script>

<template>
  <section class="quadrant q-pa-md">
    <h2 class="text-h5 q-mb-sm flex items-center">
      <q-icon
        :name="andar === 1 ? 'mdi-stairs-up' : 'mdi-stairs-up'"
        class="q-mr-sm"
        :color="andar === 1 ? 'cyan' : 'orange'"
      />
      Aulas - {{ andar }}º Andar
    </h2>
    <div ref="contentListRef" class="content-list">
      <div ref="contentInnerRef" class="content-list-inner">
        <div v-if="aulas.length === 0" class="empty-state text-h6 text-grey-5">
          Nenhuma aula programada
        </div>
        <div
          v-for="aula in aulas"
          :key="aula.id"
          class="item-card q-mb-sm q-pa-sm"
          :class="{
            'active-aula': andar === 1 && isAulaActive(aula),
            'active-aula-orange': andar === 2 && isAulaActive(aula),
            'orange-border': andar === 2 && !isAulaActive(aula)
          }"
        >
          <div class="row items-center justify-between">
            <div class="text-h6 text-weight-bold" :class="andar === 1 ? 'text-cyan' : 'text-orange'">
              {{ aula.disciplina }}
              <q-badge v-if="isAulaActive(aula)" :color="andar === 1 ? 'cyan' : 'orange'" label="AO VIVO" class="q-ml-sm" />
            </div>
            <div class="sala-badge text-h6 text-weight-bold">Sala {{ aula.sala_numero }}</div>
          </div>
          <div class="row justify-between items-center q-mt-xs">
            <div class="text-subtitle1 text-grey-4">{{ aula.professor }}</div>
            <div class="text-subtitle1 text-weight-bold text-white">
              {{ format(parseISO(aula.inicio), 'HH:mm') }} - {{ format(parseISO(aula.fim), 'HH:mm') }}
            </div>
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
  overflow: hidden;
  position: relative;
}

.content-list-inner {
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

.sala-badge {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  letter-spacing: 0.5px;
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
  width: 0;
  display: none;
}
</style>
