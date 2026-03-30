<template>
  <q-page class="q-pa-lg">
    <div class="row q-col-gutter-lg">
      <!-- Filters Card -->
      <div class="col-12 col-md-4">
        <q-card flat bordered class="filter-card glass-card">
          <q-card-section>
            <div class="text-h6 text-weight-bold flex items-center">
              <q-icon name="mdi-filter-variant" color="primary" class="q-mr-sm" />
              Filtros do Relatório
            </div>
            <div class="text-caption text-grey-7">Personalize os dados do Polare</div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <!-- Date Selection -->
            <div class="q-mb-md">
              <div class="text-subtitle2 q-mb-xs">Período</div>
              <div class="row q-col-gutter-sm">
                <div class="col-6">
                  <q-input filled v-model="startDate" label="Data Inicial" mask="XXXX-XX-XX">
                    <template v-slot:append>
                      <q-icon name="mdi-calendar" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                          <q-date v-model="startDate" mask="YYYY-MM-DD">
                            <div class="row items-center justify-end">
                              <q-btn v-close-popup label="Fechar" color="primary" flat />
                            </div>
                          </q-date>
                        </q-popup-proxy>
                      </q-icon>
                    </template>
                  </q-input>
                </div>
                <div class="col-6">
                  <q-input filled v-model="endDate" label="Data Final" mask="XXXX-XX-XX">
                    <template v-slot:append>
                      <q-icon name="mdi-calendar" class="cursor-pointer">
                        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                          <q-date v-model="endDate" mask="YYYY-MM-DD">
                            <div class="row items-center justify-end">
                              <q-btn v-close-popup label="Fechar" color="primary" flat />
                            </div>
                          </q-date>
                        </q-popup-proxy>
                      </q-icon>
                    </template>
                  </q-input>
                </div>
              </div>
              
              <!-- Quick Buttons -->
              <div class="row q-mt-sm q-col-gutter-xs">
                <div class="col-4">
                  <q-btn flat dense no-caps label="Hoje" class="full-width quick-btn" @click="setToday" />
                </div>
                <div class="col-4">
                  <q-btn flat dense no-caps label="Semana" class="full-width quick-btn" @click="setThisWeek" />
                </div>
                <div class="col-4">
                  <q-btn flat dense no-caps label="Mês" class="full-width quick-btn" @click="setThisMonth" />
                </div>
              </div>
            </div>

            <!-- Period Selection -->
            <div class="q-mb-md">
              <div class="text-subtitle2 q-mb-xs">Momento do Dia</div>
              <div class="row q-col-gutter-sm">
                <q-radio v-model="period" val="abertura" label="Abertura" class="col-4" />
                <q-radio v-model="period" val="fechamento" label="Fechamento" class="col-4" />
                <q-radio v-model="period" val="ambos" label="Ambos" class="col-4" />
              </div>
            </div>

            <!-- Floor Selection -->
            <div class="q-mb-lg">
              <div class="text-subtitle2 q-mb-xs">Andar</div>
              <div class="row q-col-gutter-sm">
                <q-radio v-model="floor" val="1" label="1º Andar" class="col-4" />
                <q-radio v-model="floor" val="2" label="2º Andar" class="col-4" />
                <q-radio v-model="floor" val="ambos" label="Ambos" class="col-4" />
              </div>
            </div>

            <q-btn
              color="primary"
              label="Gerar Relatórios"
              class="full-width shadow-2"
              icon="mdi-refresh"
              :loading="loading"
              @click="fetchReports"
            />
          </q-card-section>
        </q-card>
      </div>

      <!-- Reports Display -->
      <div class="col-12 col-md-8">
        <div v-if="!reportsGenerated && !loading" class="empty-state text-center q-pa-xl">
          <q-icon name="mdi-file-find-outline" size="84px" color="grey-4" />
          <div class="text-h6 text-grey-5 q-mt-md">Aguardando geração de relatório</div>
          <div class="text-caption text-grey-6">Selecione os filtros e clique no botão para começar</div>
        </div>

        <template v-else>
          <!-- Aulas Report -->
          <q-card flat bordered class="q-mb-lg glass-card report-card">
            <q-card-section class="row items-center no-wrap">
              <div class="col">
                <div class="text-h6 text-weight-bold">Relatório de Aulas</div>
                <div class="text-caption text-grey-7">{{ aulas.length }} registros encontrados</div>
              </div>
              <q-btn
                v-if="aulas.length > 0"
                outline
                color="primary"
                label="Gerar Script Polare"
                icon="mdi-code-braces"
                @click="copyScript(aulas)"
              />
            </q-card-section>

            <q-card-section class="q-pt-none">
              <div v-if="aulas.length === 0" class="text-center q-pa-md text-grey-6">
                Nenhuma aula encontrada para este período.
              </div>
              <div v-else class="column q-gutter-sm">
                <div v-for="(line, index) in aulas" :key="'aula-'+index" class="cursor-pointer">
                  <q-input
                    readonly
                    filled
                    dense
                    :model-value="line"
                    @click="copyToClipboard(line)"
                  >
                    <template v-slot:append>
                      <q-icon name="mdi-content-copy" size="xs" color="grey-6" />
                    </template>
                  </q-input>
                </div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Acessos Report -->
          <q-card flat bordered class="glass-card report-card">
            <q-card-section class="row items-center no-wrap">
              <div class="col">
                <div class="text-h6 text-weight-bold">Relatório de Acessos</div>
                <div class="text-caption text-grey-7">{{ acessos.length }} registros encontrados</div>
              </div>
              <q-btn
                v-if="acessos.length > 0"
                outline
                color="primary"
                label="Gerar Script Polare"
                icon="mdi-code-braces"
                @click="copyScript(acessos)"
              />
            </q-card-section>

            <q-card-section class="q-pt-none">
              <div v-if="acessos.length === 0" class="text-center q-pa-md text-grey-6">
                Nenhum acesso encontrado para este período.
              </div>
              <div v-else class="column q-gutter-sm">
                <div v-for="(line, index) in acessos" :key="'acesso-'+index" class="cursor-pointer">
                  <q-input
                    readonly
                    filled
                    dense
                    :model-value="line"
                    @click="copyToClipboard(line)"
                  >
                    <template v-slot:append>
                      <q-icon name="mdi-content-copy" size="xs" color="grey-6" />
                    </template>
                  </q-input>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </template>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { useQuasar, date, copyToClipboard as qCopyToClipboard } from 'quasar';

const $q = useQuasar();

const startDate = ref('');
const endDate = ref('');
const period = ref('ambos');
const floor = ref('ambos');
const loading = ref(false);
const reportsGenerated = ref(false);

const aulas = ref<string[]>([]);
const acessos = ref<string[]>([]);

const setToday = () => {
  const today = new Date();
  const formatted = date.formatDate(today, 'YYYY-MM-DD');
  startDate.value = formatted;
  endDate.value = formatted;
};

const setThisWeek = () => {
  const today = new Date();
  const day = today.getDay();
  const diff = today.getDate() - day + (day === 0 ? -6 : 1); // adjust when day is sunday
  const first = new Date(today.setDate(diff));
  const last = new Date(today.setDate(first.getDate() + 6));
  
  startDate.value = date.formatDate(first, 'YYYY-MM-DD');
  endDate.value = date.formatDate(last, 'YYYY-MM-DD');
};

const setThisMonth = () => {
  const today = new Date();
  const first = new Date(today.getFullYear(), today.getMonth(), 1);
  const last = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  
  startDate.value = date.formatDate(first, 'YYYY-MM-DD');
  endDate.value = date.formatDate(last, 'YYYY-MM-DD');
};

const fetchReports = async () => {
  if (!startDate.value || !endDate.value) {
    $q.notify({
      type: 'warning',
      message: 'Selecione as datas inicial e final.',
    });
    return;
  }

  loading.value = true;
  try {
    const response = await api.get('/controle/polare/reports/', {
      params: {
        start_date: startDate.value,
        end_date: endDate.value,
        period: period.value,
        floor: floor.value,
      },
    });

    aulas.value = response.data.aulas;
    acessos.value = response.data.acessos;
    reportsGenerated.value = true;
    
    $q.notify({
      type: 'success',
      message: 'Relatórios gerados com sucesso!',
      icon: 'mdi-check-circle',
    });
  } catch (error) {
    console.error('Erro ao buscar relatórios:', error);
    $q.notify({
      type: 'negative',
      message: 'Erro ao buscar dados do servidor.',
    });
  } finally {
    loading.value = false;
  }
};

const copyToClipboard = (text: string) => {
  qCopyToClipboard(text)
    .then(() => {
      $q.notify({
        message: 'Texto copiado!',
        color: 'positive',
        timeout: 1000,
        position: 'bottom',
        icon: 'mdi-content-copy'
      });
    })
    .catch(() => {
      $q.notify({
        message: 'Falha ao copiar.',
        color: 'negative'
      });
    });
};

const copyScript = (lines: string[]) => {
  const tasks = JSON.stringify(lines);
  const script = `(function() {const tasks = ${tasks}; let i = 0; function processNext() { if (i >= tasks.length) { console.log('[NUPEDEE] Importação dos dados concluída.'); return; } const line = tasks[i]; console.log('Processando: ' + line); $("#input-new-subtarefa").val(line); setTimeout(function() { $("#btn-add-subtarefa").prop("disabled", false); setTimeout(function() { $("#btn-add-subtarefa").click(); i++; setTimeout(processNext, 250); }, 250); }, 250); } processNext(); })();`;
  
  qCopyToClipboard(script)
    .then(() => {
      $q.notify({
        message: 'Script Polare copiado para o clipboard!',
        caption: 'Cole o console do navegador do outro sistema.',
        color: 'primary',
        icon: 'mdi-xml',
        timeout: 4000
      });
    })
    .catch(() => {
      $q.notify({
        message: 'Falha ao copiar script.',
        color: 'negative'
      });
    });
};

onMounted(() => {
  setThisMonth();
});
</script>

<style lang="scss" scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
}

.report-card {
  transition: all 0.3s ease;
  &:hover {
    border-color: var(--q-primary);
    box-shadow: 0 8px 24px rgba(25, 118, 210, 0.1);
  }
}

.filter-card {
  position: sticky;
  top: 84px;
}

.quick-btn {
  background: rgba(25, 118, 210, 0.05);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--q-primary);
  &:hover {
    background: rgba(25, 118, 210, 0.1);
  }
}

.empty-state {
  margin-top: 100px;
}

.report-item {
  transition: transform 0.2s;
  &:active {
    transform: scale(0.995);
  }
}
</style>
