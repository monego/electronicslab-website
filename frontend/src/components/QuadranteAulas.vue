<script setup lang="ts">
import { watch, nextTick, useTemplateRef, computed } from 'vue';
import { format, parseISO, isWithinInterval } from 'date-fns';
import { Temporal } from '@js-temporal/polyfill';

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
  isSingleQuadrant: boolean;
  isLargeLayout: boolean;
  quadrantSizeMultiplier: number;
}>();

const formatTimeSP = (isoString: string) => {
  try {
    return Temporal.Instant.from(isoString)
      .toZonedDateTimeISO('America/Sao_Paulo')
      .toPlainTime()
      .toString()
      .slice(0, 5);
  } catch {
    return format(parseISO(isoString), 'HH:mm');
  }
};

const isAulaActive = (aula: Aula) => {
  const start = parseISO(aula.inicio);
  const end = parseISO(aula.fim);
  return isWithinInterval(props.currentTime, { start, end });
};

// Truncate text utility
function truncateText(text: string, maxLength: number): string {
  const effectiveMaxLength = props.isLargeLayout ? maxLength * 2 : maxLength;
  if (text.length > effectiveMaxLength) {
    return text.substring(0, effectiveMaxLength - 3) + '...';
  }
  return text;
}

// Format professor name utility
function formatProfessorName(name: string, maxLength: number): string {
  const effectiveMaxLength = props.isLargeLayout ? maxLength * 2 : maxLength;
  if (name.length > effectiveMaxLength) {
    const parts = name.split(' ');
    if (parts.length >= 2) {
      const firstName = parts[0];
      const lastName = parts[parts.length - 1];
      const formatted = `${firstName} ${lastName}`;
      if (formatted.length <= effectiveMaxLength) {
        return formatted;
      }
    }
    // Fallback to truncation if first+last name is still too long or not enough parts
    return truncateText(name, effectiveMaxLength);
  }
  return name;
}

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

const agoraBadgeStyle = computed(() => {
  const defaultFontSize = 0.8; // in em
  const defaultPaddingV = 4; // in px
  const defaultPaddingH = 8; // in px

  if (props.isLargeLayout) {
    // 0.75em for large layout "Agora" button
    return {
      fontSize: `0.75em`,
      padding: `6px 12px`, // slightly larger padding for visual balance
      color: 'rgba(255, 255, 255, 0.7)'
    };
  } else {
    // Scale by quadrantSizeMultiplier for default layout
    const effectiveFontSize = defaultFontSize * props.quadrantSizeMultiplier;
    const effectivePaddingV = defaultPaddingV * props.quadrantSizeMultiplier;
    const effectivePaddingH = defaultPaddingH * props.quadrantSizeMultiplier;
    return {
      fontSize: `${effectiveFontSize}em`,
      padding: `${effectivePaddingV}px ${effectivePaddingH}px`,
      color: 'rgba(255, 255, 255, 0.7)'
    };
  }
});

const disciplinaFontSize = computed(() => {
  const baseRem = 1.4; // Was 1.5
  return `${baseRem * props.quadrantSizeMultiplier}rem`;
});
const professorFontSize = computed(() => {
  const baseRem = 1.1; // Was 1.2
  return `${baseRem * props.quadrantSizeMultiplier}rem`;
});
const timeFontSize = computed(() => {
  const baseRem = 1.6; // Was 1.8
  return `${baseRem * props.quadrantSizeMultiplier}rem`;
});
const salaFontSize = computed(() => {
  const baseRem = 1.6; // Was 1.8
  return `${baseRem * props.quadrantSizeMultiplier}rem`;
});

watch(() => props.aulas, () => {
  void nextTick(updateScrollDistance);
}, { immediate: true, deep: true });
</script>

<template>
  <section class="quadrant q-pa-md">
    <h2 class="q-mb-sm flex items-center text-weight-bold" style="font-size: 2rem;">
      <q-icon
        :name="andar === 1 ? 'mdi-stairs-down' : 'mdi-stairs-up'"
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
          <div class="row items-start justify-between">
            <div class="column">
              <div class="text-weight-bold" :style="{ fontSize: disciplinaFontSize }" :class="andar === 1 ? 'text-cyan' : 'text-orange'">
                {{ truncateText(aula.disciplina, 25) }}
                <q-badge v-if="isAulaActive(aula)" :color="andar === 1 ? 'cyan' : 'orange'" label="Agora" class="q-ml-sm" :style="agoraBadgeStyle" />
              </div>
              <div class="text-grey-4" :style="{ fontSize: professorFontSize }">{{ formatProfessorName(aula.professor, 30) }}</div>
            </div>
            <div class="flex items-center" :style="{ fontSize: timeFontSize }">
              <div class="text-white text-weight-bold sala-badge" :style="{ fontSize: timeFontSize }">{{ formatTimeSP(aula.inicio) }} ~ {{ formatTimeSP(aula.fim) }}</div>
              <div class="q-ml-md text-white text-weight-bold sala-badge" :style="{ fontSize: salaFontSize }">{{ aula.sala_numero }}</div>
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
