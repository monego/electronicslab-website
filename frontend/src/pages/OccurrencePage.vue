<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { format, parse, addHours, differenceInMinutes } from 'date-fns';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';

const today = new Date();
const formattedDate = format(today, 'yyyy/MM/dd');
const $q = useQuasar();

type DateModel = {
  from: string;
  to: string;
} | string;

interface Jornada {
  segunda: (string | null)[],
  terca: (string | null)[],
  quarta: (string | null)[],
  quinta: (string | null)[],
  sexta: (string | null)[],
}

interface AusenciaRow {
  id: number;
  inicio: string;
  fim: string;
  motivo: string;
  funcionario: number;
  funcionario_nome: string;
}

interface HorarioResponse {
  dia_da_semana: string;
  inicio: string | null;
  inicio_intervalo: string | null;
  fim_intervalo: string | null;
  fim: string | null;
}

const dayKeys: (keyof Jornada)[] = ['segunda', 'terca', 'quarta', 'quinta', 'sexta'];
const dayLabels: Record<keyof Jornada, string> = {
  segunda: 'Segunda-feira',
  terca: 'Terça-feira',
  quarta: 'Quarta-feira',
  quinta: 'Quinta-feira',
  sexta: 'Sexta-feira',
};

const model = ref<DateModel>(formattedDate);
const motivo = ref<string>('');
const ausencias = ref<AusenciaRow[]>([]);

const horarios = ref<Jornada>({
  segunda: [null, null, null, null],
  terca: [null, null, null, null],
  quarta: [null, null, null, null],
  quinta: [null, null, null, null],
  sexta: [null, null, null, null],
});

const ausenciaColumns = [
  {
    name: 'inicio',
    label: 'Início',
    align: 'left' as const,
    field: 'inicio',
    format: (val: string) => format(new Date(val + 'T00:00:00'), 'dd/MM/yyyy'),
    sortable: true
  },
  {
    name: 'fim',
    label: 'Fim',
    align: 'left' as const,
    field: 'fim',
    format: (val: string) => format(new Date(val + 'T00:00:00'), 'dd/MM/yyyy'),
    sortable: true
  },
  { name: 'motivo', label: 'Motivo', align: 'left' as const, field: 'motivo' },
  { name: 'acoes', label: 'Ações', align: 'center' as const, field: 'id' },
];

async function getAusencias() {
  try {
    const response = await api.get('/controle/ausencia/');
    ausencias.value = response.data;
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar ocorrências.' });
  }
}

async function getHorarios() {
  try {
    const response = await api.get('/controle/horarios/');
    if (response.status === 200) {
      dayKeys.forEach(k => horarios.value[k] = [null, null, null, null]);

      (response.data as HorarioResponse[]).forEach((item) => {
        const dia = item.dia_da_semana as keyof Jornada;
        if (horarios.value[dia]) {
          horarios.value[dia] = [
            item.inicio ? item.inicio.slice(0, 5) : null,
            item.inicio_intervalo ? item.inicio_intervalo.slice(0, 5) : null,
            item.fim_intervalo ? item.fim_intervalo.slice(0, 5) : null,
            item.fim ? item.fim.slice(0, 5) : null
          ];
        }
      });
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar horários.' });
  }
}

async function patchHorarios(day: keyof Jornada) {
  const hour = horarios.value[day];

  if (!hour[0] || !hour[1] || !hour[2] || !hour[3]) {
      $q.notify({ type: 'warning', message: 'Preencha todos os campos do horário.' });
      return;
  }

  const start = parse(hour[1], 'HH:mm', new Date());
  const end = parse(hour[2], 'HH:mm', new Date());
  if (differenceInMinutes(end, start) < 60) {
    $q.notify({ type: 'warning', message: 'O intervalo deve ser de pelo menos 1 hora.' });
    return;
  }

  try {
    await api.patch('/controle/horarios/byday/', {
      dia: day,
      inicio: hour[0],
      inicio_intervalo: hour[1],
      fim_intervalo: hour[2],
      fim: hour[3],
    });
    $q.notify({ type: 'positive', message: `Horário de ${dayLabels[day]} atualizado.` });
    await getHorarios();
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao salvar horário.' });
  }
}

function parseDateModel(time: DateModel): { from: string; to: string } {
  if (typeof time === 'string') {
    const d = format(new Date(time), 'yyyy-MM-dd');
    return { from: d, to: d };
  }
  return {
    from: format(new Date(time.from), 'yyyy-MM-dd'),
    to: format(new Date(time.to), 'yyyy-MM-dd'),
  };
}

async function setAusencia() {
  if (!motivo.value) {
    $q.notify({ type: 'warning', message: 'Informe o motivo.' });
    return;
  }
  try {
    const { from, to } = parseDateModel(model.value);
    await api.post('/controle/ausencia/', { inicio: from, fim: to, motivo: motivo.value });
    $q.notify({ type: 'positive', message: 'Ocorrência registrada.' });
    motivo.value = '';
    model.value = formattedDate;
    await getAusencias();
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao registrar ocorrência.' });
  }
}

async function deleteAusencia(id: number) {
  try {
    await api.delete(`/controle/ausencia/${id}/`);
    $q.notify({ type: 'positive', message: 'Ocorrência excluída.' });
    await getAusencias();
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao excluir.' });
  }
}

function setOneHourInterval(day: keyof Jornada) {
  const hour = horarios.value[day];
  if (hour[1]) {
    const start = parse(hour[1], 'HH:mm', new Date());
    const end = addHours(start, 1);
    horarios.value[day][2] = format(end, 'HH:mm');
  }
}

function calculateTotalHours(day: keyof Jornada) {
  const h = horarios.value[day];
  if (!h[0] || !h[1] || !h[2] || !h[3]) return null;

  try {
    const start = parse(h[0], 'HH:mm', new Date());
    const breakStart = parse(h[1], 'HH:mm', new Date());
    const breakEnd = parse(h[2], 'HH:mm', new Date());
    const end = parse(h[3], 'HH:mm', new Date());

    const work1 = differenceInMinutes(breakStart, start);
    const work2 = differenceInMinutes(end, breakEnd);
    const totalMinutes = work1 + work2;

    if (totalMinutes < 0) return 'Erro';

    const hours = Math.floor(totalMinutes / 60);
    const mins = totalMinutes % 60;
    return `${hours}h${mins > 0 ? mins : ''}`;
  } catch {
    return null;
  }
}

onMounted(() => {
  void getHorarios();
  void getAusencias();
});
</script>

<template>
  <div class="q-pa-lg">
    <div class="row q-col-gutter-lg">
      <div class="col-12 col-md-5">
        <q-card flat bordered class="q-mb-md shadow-2">
          <q-card-section class="bg-primary text-white">
            <div class="text-h6"><q-icon name="event_note" class="q-mr-sm" /> Registrar Ocorrência</div>
          </q-card-section>

          <q-card-section class="q-gutter-y-md">
            <div class="text-subtitle2 text-grey-7">Selecione o período e o motivo:</div>
            <div class="row justify-center">
              <q-date v-model="model" range flat bordered dense color="primary" />
            </div>
            <q-input
              v-model="motivo"
              label="Justificativa / Motivo"
              filled
              autogrow
              prefix="📝"
            />
            <q-btn
              color="primary"
              icon="add_circle"
              label="Registrar"
              class="full-width q-py-sm"
              rounded
              @click="setAusencia"
            />
          </q-card-section>
        </q-card>

        <q-card flat bordered class="shadow-2">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">Minhas Ocorrências</div>
            <q-space />
            <q-btn icon="refresh" flat round dense @click="getAusencias" />
          </q-card-section>

          <q-card-section>
            <q-table
              flat
              bordered
              :rows="ausencias"
              :columns="ausenciaColumns"
              row-key="id"
              :pagination="{ rowsPerPage: 5 }"
              no-data-label="Nenhuma ocorrência encontrada"
            >
              <template v-slot:body-cell-acoes="props">
                <q-td :props="props">
                  <q-btn
                    flat round dense
                    color="negative"
                    icon="delete_outline"
                    @click="deleteAusencia(props.row.id)"
                  >
                    <q-tooltip>Excluir</q-tooltip>
                  </q-btn>
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-12 col-md-7">
        <q-card flat bordered class="shadow-2">
          <q-card-section class="bg-secondary text-white">
            <div class="text-h6"><q-icon name="schedule" class="q-mr-sm" /> Jornada de Trabalho</div>
            <div class="text-caption">Permitido: 07:30 às 19:30 | Intervalo obrigatório: 1h</div>
          </q-card-section>

          <q-card-section class="q-pa-none">
            <q-list separator>
              <q-item v-for="day in dayKeys" :key="day" class="q-py-md">
                <q-item-section style="min-width: 120px" class="col-2">
                  <div class="text-weight-bold text-subtitle1">{{ dayLabels[day] }}</div>
                  <div class="text-caption text-primary" v-if="calculateTotalHours(day)">
                    Total: {{ calculateTotalHours(day) }}
                  </div>
                </q-item-section>

                <q-item-section class="col-8">
                  <div class="row q-col-gutter-sm items-center">
                    <div class="col-3">
                      <q-input
                        v-model="horarios[day][0]"
                        filled dense type="time"
                        label="Início"
                        min="07:30" max="19:30"
                      />
                    </div>
                    <div class="col-3">
                      <q-input
                        v-model="horarios[day][1]"
                        filled dense type="time"
                        label="Início Intervalo"
                        min="07:30" max="19:30"
                        @update:model-value="setOneHourInterval(day)"
                      />
                    </div>
                    <div class="col-3">
                      <q-input
                        v-model="horarios[day][2]"
                        filled dense type="time"
                        label="Fim Intervalo"
                        min="07:30" max="19:30"
                      />
                    </div>
                    <div class="col-3">
                      <q-input
                        v-model="horarios[day][3]"
                        filled dense type="time"
                        label="Fim"
                        min="07:30" max="19:30"
                      />
                    </div>
                  </div>
                </q-item-section>

                <q-item-section side class="col-2">
                  <q-btn
                    round flat color="primary"
                    icon="save"
                    @click="patchHorarios(day)"
                  >
                    <q-tooltip>Salvar dia</q-tooltip>
                  </q-btn>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>

          <q-card-section class="bg-grey-2 text-grey-8 text-caption text-center">
            Ao alterar o início do intervalo, o fim será ajustado automaticamente para manter 1h.
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.q-card {
  border-radius: 12px;
}
</style>
