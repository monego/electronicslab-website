<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';
import type { AxiosResponse } from 'axios';
import ComponentTable from 'components/ComponentTable.vue';

interface Componente {
  id?: number;
  nome: string;
  descricao?: string;
  quantidade: number;
  datasheet: string | null;
  categoria: string;
  tipo: string;
}

const $q = useQuasar();
const components = ref<Componente[]>([]);
const loading = ref(false);
const tab = ref('consultar');
const showEditDialog = ref(false);

interface TableColumn {
  name: string;
  label: string;
  align?: 'left' | 'right' | 'center';
  field: string | ((row: Componente) => string | number | null | undefined);
  required?: boolean;
  sortable?: boolean;
}

const columns: TableColumn[] = [
  { name: 'nome', label: 'Nome', field: 'nome', align: 'left', sortable: true },
  { name: 'descricao', label: 'Descrição', field: 'descricao', align: 'left' },
  { name: 'tipo', label: 'Tipo', field: 'tipo', align: 'left', sortable: true },
  { name: 'quantidade', label: 'Quantidade', field: 'quantidade', align: 'center', sortable: true },
  { name: 'categoria', label: 'Categoria', field: 'categoria', align: 'center', sortable: true },
  { name: 'datasheet', label: 'Datasheet', field: 'datasheet', align: 'center' },
  { name: 'acoes', label: 'Ações', field: '', align: 'center' },
];

const componentForm = ref<Componente>({
  nome: '',
  descricao: '',
  quantidade: 0,
  datasheet: null,
  categoria: 'EL',
  tipo: 'OUTRO',
});

const editForm = ref<Componente>({
  nome: '',
  descricao: '',
  quantidade: 0,
  datasheet: null,
  categoria: 'EL',
  tipo: 'OUTRO',
});

const datasheetFile = ref<File | null>(null);
const editDatasheetFile = ref<File | null>(null);

const categoriaOptions = [
  { label: 'Elétrica', value: 'Elétrica' },
  { label: 'Pneumática', value: 'Pneumática' },
  { label: 'Processos', value: 'Processos' },
];

const tipoOptions = [
  { label: 'Resistor', value: 'Resistor' },
  { label: 'Potenciômetro', value: 'Potenciômetro' },
  { label: 'Capacitor', value: 'Capacitor' },
  { label: 'Indutor', value: 'Indutor' },
  { label: 'CI Lógico', value: 'CI Lógico' },
  { label: 'CI', value: 'CI' },
  { label: 'Transistor', value: 'Transistor' },
  { label: 'MOSFET', value: 'MOSFET' },
  { label: 'IGBT', value: 'IGBT' },
  { label: 'Triac', value: 'TRIAC' },
  { label: 'Diac', value: 'DIAC' },
  { label: 'Semicondutor', value: 'Semicondutor' },
  { label: 'Regulador', value: 'Regulador' },
  { label: 'Op-Amp', value: 'Op-Amp' },
  { label: 'Diodo', value: 'Diodo' },
  { label: 'LED', value: 'LED' },
  { label: 'Sensor', value: 'Sensor' },
  { label: 'Shield', value: 'Shield' },
  { label: 'MCU', value: 'Microcontrolador' },
  { label: 'Cabo', value: 'Cabo' },
  { label: 'Módulo', value: 'Módulo' },
  { label: 'Componente', value: 'Componente' },
  { label: 'Outro', value: 'Outro' },
];

async function getComponents() {
  loading.value = true;
  try {
    const response: AxiosResponse<Componente[]> = await api.get('/controle/componentes/');
    components.value = response.data;
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar componentes.' });
  } finally {
    loading.value = false;
  }
}

async function registerComponent() {
  const formData = new FormData();
  if (componentForm.value.nome) formData.append('nome', componentForm.value.nome);
  if (componentForm.value.descricao) formData.append('descricao', componentForm.value.descricao);
  formData.append('quantidade', String(componentForm.value.quantidade));
  formData.append('categoria', componentForm.value.categoria);
  formData.append('tipo', componentForm.value.tipo);

  if (datasheetFile.value) {
    formData.append('datasheet', datasheetFile.value);
  }

  try {
    await api.post('/controle/componentes/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    $q.notify({ type: 'positive', message: 'Componente cadastrado.' });
    resetForm();
    tab.value = 'consultar';
    void getComponents();
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao cadastrar componente.' });
  }
}

function resetForm() {
  componentForm.value = {
    nome: '',
    descricao: '',
    quantidade: 0,
    datasheet: null,
    categoria: 'EL',
    tipo: 'OUTRO',
  };
  datasheetFile.value = null;
}

function openEditDialog(row: Componente) {
  editForm.value = { ...row };
  editDatasheetFile.value = null;
  showEditDialog.value = true;
}

async function updateComponent() {
  const formData = new FormData();
  if (editForm.value.nome) formData.append('nome', editForm.value.nome);
  if (editForm.value.descricao) formData.append('descricao', editForm.value.descricao);
  formData.append('quantidade', String(editForm.value.quantidade));
  formData.append('categoria', editForm.value.categoria);
  formData.append('tipo', editForm.value.tipo);

  if (editDatasheetFile.value) {
    formData.append('datasheet', editDatasheetFile.value);
  }

  try {
    await api.patch(`/controle/componentes/${editForm.value.id ?? ''}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    $q.notify({ type: 'positive', message: 'Componente atualizado.' });
    showEditDialog.value = false;
    void getComponents();
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao atualizar componente.' });
  }
}

function deleteComponent(row: Componente) {
  $q.dialog({
    title: 'Confirmar exclusão',
    message: `Deseja realmente excluir o componente ${row.nome}?`,
    cancel: true,
    persistent: true
  }).onOk(() => {
    void (async () => {
      try {
        await api.delete(`/controle/componentes/${row.id ?? ''}/`);
        $q.notify({ type: 'positive', message: 'Componente excluído.' });
        void getComponents();
      } catch {
        $q.notify({ type: 'negative', message: 'Erro ao excluir componente.' });
      }
    })();
  });
}

onMounted(() => {
  void getComponents();
});
</script>

<template>
  <q-page class="q-pa-md bg-grey-1">
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-card flat bordered class="shadow-2" style="border-radius: 12px;">
          <q-tabs
            v-model="tab"
            dense
            class="text-grey-7 bg-white"
            active-color="primary"
            indicator-color="primary"
            align="left"
            narrow-indicator
            style="border-radius: 12px 12px 0 0;"
          >
            <q-tab name="consultar" icon="mdi-magnify" label="Consultar" />
            <q-tab name="cadastrar" icon="mdi-plus-circle-outline" label="Cadastrar Novo" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="tab" animated class="bg-transparent">
            <!-- LIST VIEW -->
            <q-tab-panel name="consultar" class="q-pa-none">
              <ComponentTable
                :rows="components"
                :columns="columns"
                :loading="loading"
                @edit="openEditDialog"
                @delete="deleteComponent"
              />
            </q-tab-panel>

            <!-- CREATE VIEW -->
            <q-tab-panel name="cadastrar">
              <div class="row justify-center">
                <div class="col-12 col-md-8">
                  <q-card flat bordered class="q-pa-lg bg-white shadow-1" style="border-radius: 8px;">
                    <div class="text-h6 q-mb-lg text-primary text-weight-bold">Novo Componente</div>
                    <q-form @submit.prevent="registerComponent" class="q-gutter-md">
                      <div class="row q-col-gutter-md">
                        <div class="col-12 col-sm-6">
                          <q-input v-model="componentForm.nome" label="Nome" outlined dense required />
                        </div>
                        <div class="col-12 col-sm-3">
                          <q-select
                            v-model="componentForm.categoria"
                            :options="categoriaOptions"
                            label="Categoria"
                            outlined dense emit-value map-options
                          />
                        </div>
                        <div class="col-12 col-sm-3">
                          <q-input v-model.number="componentForm.quantidade" label="Quantidade" type="number" outlined dense required />
                        </div>

                        <div class="col-12 col-sm-6">
                          <q-select
                            v-model="componentForm.tipo"
                            :options="tipoOptions"
                            label="Tipo de Componente"
                            outlined dense emit-value map-options
                          />
                        </div>

                        <div class="col-12 col-sm-6">
                          <q-file v-model="datasheetFile" label="Datasheet (PDF)" outlined dense accept=".pdf">
                            <template v-slot:prepend>
                              <q-icon name="mdi-file-pdf-box" />
                            </template>
                          </q-file>
                        </div>

                        <div class="col-12">
                          <q-input v-model="componentForm.descricao" label="Descrição" outlined dense autogrow />
                        </div>
                      </div>

                      <div class="flex justify-end q-mt-xl">
                        <q-btn label="Limpar" flat color="grey" @click="resetForm" class="q-mr-sm" />
                        <q-btn label="Cadastrar Componente" type="submit" color="primary" rounded unelevated />
                      </div>
                    </q-form>
                  </q-card>
                </div>
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>

    <!-- EDIT DIALOG -->
    <q-dialog v-model="showEditDialog" backdrop-filter="blur(4px)">
      <q-card style="min-width: 500px; border-radius: 12px;">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Editar Componente</div>
        </q-card-section>

        <q-card-section class="q-gutter-md q-pt-lg">
          <div class="row q-col-gutter-sm">
            <div class="col-12">
              <q-input v-model="editForm.nome" label="Nome" outlined dense />
            </div>
            <div class="col-6">
              <q-select
                v-model="editForm.categoria"
                :options="categoriaOptions"
                label="Categoria"
                outlined dense emit-value map-options
              />
            </div>
            <div class="col-6">
              <q-input v-model.number="editForm.quantidade" label="Quantidade" type="number" outlined dense />
            </div>
            <div class="col-12">
              <q-select
                v-model="editForm.tipo"
                :options="tipoOptions"
                label="Tipo"
                outlined dense emit-value map-options
              />
            </div>
            <div class="col-12">
              <q-input v-model="editForm.descricao" label="Descrição" outlined dense autogrow />
            </div>
            <div class="col-12">
               <q-file v-model="editDatasheetFile" label="Novo Datasheet (PDF)" outlined dense accept=".pdf">
                <template v-slot:prepend>
                  <q-icon name="mdi-file-pdf-box" />
                </template>
              </q-file>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancelar" color="grey" v-close-popup />
          <q-btn unelevated label="Salvar Alterações" color="primary" @click="updateComponent" rounded />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>
