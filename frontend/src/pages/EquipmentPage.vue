<script setup lang="ts">
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { ref, onMounted } from 'vue';
import { format } from 'date-fns';
import type { AxiosResponse } from 'axios';

// Data properties
const tab = ref('consultar');
const descManutencao = ref<string>('');
const showDialog = ref<boolean>(false);
const showEditDialog = ref<boolean>(false);
const $q = useQuasar();

const pagination = ref({
  sortBy: 'nome',
  descending: false,
  page: 1,
  rowsPerPage: 20
});


interface Row {
  id?: number;
  nome: string;
  descricao: string;
  patrimonio: string;
  sala: number | null;
  sala_numero: string;
  defeito: boolean;
  num_manutencao: number;
  num_emprestimo: number;
  foto: string | null;
  manual: string | null;
}

interface EditFormData {
  id?: number;
  nome: string;
  descricao: string;
  patrimonio: string;
  sala: number | null;
  sala_numero: string;
  defeito: boolean;
  num_manutencao: number;
  num_emprestimo: number;
}

interface Sala {
  id: number;
  numero: string;
  nome: string;
}

interface Column {
  name: string;
  label: string;
  align?: 'left' | 'right' | 'center';
  field: string | ((row: Row) => string | number | boolean | null | undefined);
  required?: boolean;
  format?: (val: boolean) => string;
  sortable?: boolean;
}

const search = ref('');
const columns: Column[] = [
  {
    name: 'nome',
    label: 'Nome',
    align: 'left',
    field: (row: Row) => row.nome,
    required: true,
    sortable: true,
  },
  {
    name: 'patrimonio',
    label: 'Patrimônio',
    align: 'center',
    field: (row: Row) => row.patrimonio,
    sortable: true,
  },
  {
    name: 'sala',
    label: 'Sala',
    align: 'center',
    field: (row: Row) => row.sala_numero,
  },
  {
    name: 'defeito',
    label: 'Defeito',
    align: 'center',
    field: (row: Row) => row.defeito,
    format: (val: boolean) => (val ? 'Sim' : 'Não'),
  },
  {
    name: 'manutencao',
    label: 'Manutenções',
    align: 'center',
    field: (row: Row) => row.num_manutencao,
    sortable: true,
  },
  {
    name: 'emprestimo',
    label: 'Empréstimos',
    align: 'center',
    field: (row: Row) => row.num_emprestimo,
    sortable: true,
  },
  {
    name: 'foto',
    label: 'Foto',
    align: 'center',
    field: (row: Row) => row.foto,
  },
  {
    name: 'manual',
    label: 'Manual',
    align: 'center',
    field: (row: Row) => row.manual,
  },
  {
    name: 'acoes',
    label: 'Ações',
    align: 'center',
    field: '',
  },
];

interface RowManutencao {
  id: string;
  descricao: string;
  data: string;
  equipamento_nome: string;
  funcionario_nome: string;
}

const selectedNome = ref<string>('');
const selectedPatrimonio = ref<string>('');
const rows = ref<Row[]>([]);
const manutencoes = ref<RowManutencao[]>([]);
const salas = ref<Sala[]>([]);

// Form state for registration
const equipmentForm = ref({
  nome: '',
  descricao: '',
  patrimonio: '',
  sala: null as number | null,
  defeito: false,
  foto: null as File | null,
  manual: null as File | null,
});

// Form state for editing
const editForm = ref<EditFormData>({
  nome: '',
  descricao: '',
  patrimonio: '',
  sala: null,
  sala_numero: '',
  defeito: false,
  num_manutencao: 0,
  num_emprestimo: 0,
});
const editFoto = ref<File | null>(null);
const editManual = ref<File | null>(null);

async function getSalas() {
  try {
    const response: AxiosResponse<Sala[]> = await api.get('/root/salas/');
    salas.value = response.data;
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar salas.' });
  }
}

async function getEquipments() {
  try {
    const response: AxiosResponse<Row[]> = await api.get('/controle/equipamento/');
    if (response.status === 200) {
      rows.value = response.data;
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar equipamentos.' });
  }
}

async function registerEquipment() {
  const formData = new FormData();
  formData.append('nome', equipmentForm.value.nome);
  formData.append('descricao', equipmentForm.value.descricao);
  formData.append('patrimonio', equipmentForm.value.patrimonio);
  if (equipmentForm.value.sala) formData.append('sala', String(equipmentForm.value.sala));
  formData.append('defeito', String(equipmentForm.value.defeito));
  
  if (equipmentForm.value.foto) formData.append('foto', equipmentForm.value.foto);
  if (equipmentForm.value.manual) formData.append('manual', equipmentForm.value.manual);

  try {
    const response = await api.post('/controle/equipamento/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    if (response.status === 201) {
      $q.notify({ type: 'positive', message: 'Equipamento cadastrado com sucesso.' });
      resetForm();
      tab.value = 'consultar';
      await getEquipments();
    }
  } catch (error: unknown) {
    const axiosErr = error as { response?: { data?: { detail?: string } } };
    const detail = axiosErr.response?.data?.detail || 'Erro ao cadastrar equipamento.';
    $q.notify({ type: 'negative', message: detail });
  }
}

function resetForm() {
  equipmentForm.value = {
    nome: '',
    descricao: '',
    patrimonio: '',
    sala: null,
    defeito: false,
    foto: null,
    manual: null,
  };
}

function deleteEquipment(patrimonio: string) {
  $q.dialog({
    title: 'Confirmar exclusão',
    message: `Deseja realmente excluir o equipamento ${patrimonio}?`,
    cancel: true,
    persistent: true
  }).onOk(() => {
    void (async () => {
      try {
        const equip = rows.value.find(r => r.patrimonio === patrimonio);
        if (equip?.id) {
          await api.delete(`/controle/equipamento/${equip.id}/`);
          $q.notify({ type: 'positive', message: 'Equipamento excluído.' });
          await getEquipments();
        }
      } catch {
        $q.notify({ type: 'negative', message: 'Erro ao excluir equipamento.' });
      }
    })();
  });
}


function openEditDialog(row: Row) {
  editForm.value = { ...row };
  editFoto.value = null;
  editManual.value = null;
  showEditDialog.value = true;
}

async function updateEquipment() {
  const formData = new FormData();
  formData.append('nome', editForm.value.nome);
  formData.append('descricao', editForm.value.descricao);
  formData.append('patrimonio', editForm.value.patrimonio);
  if (editForm.value.sala) formData.append('sala', String(editForm.value.sala));
  formData.append('defeito', String(editForm.value.defeito));

  if (editFoto.value) formData.append('foto', editFoto.value);
  if (editManual.value) formData.append('manual', editManual.value);

  try {
    const response = await api.patch(`/controle/equipamento/${editForm.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    if (response.status === 200) {
      $q.notify({ type: 'positive', message: 'Equipamento atualizado.' });
      showEditDialog.value = false;
      await getEquipments();
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao atualizar equipamento.' });
  }
}

async function getManutencao(patr: string) {
  try {
    const response: AxiosResponse<RowManutencao[]> = await api.get('/controle/manutencao/', {
      params: { patrimonio: patr },
    });
    manutencoes.value = response.data;
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao buscar manutenções.' });
  }
}

async function registerManutencao(desc: string, patr: string) {
  try {
    const response = await api.post('/controle/manutencao/', {
      descricao: desc,
      patrimonio: patr,
    });
    if (response.status === 201) {
      $q.notify({ type: 'positive', message: 'Manutenção registrada.' });
      descManutencao.value = '';
      await getEquipments();
      await getManutencao(patr);
    }
  } catch {
    $q.notify({ type: 'negative', message: 'Erro ao registrar manutenção.' });
  }
}

function openMaintenanceDialog(row: Row) {
  selectedNome.value = row.nome;
  selectedPatrimonio.value = row.patrimonio;
  showDialog.value = true;
  void getManutencao(row.patrimonio);
}

const openImage = (imageUrl: string) => {
  window.open(imageUrl, '_blank');
};

onMounted(() => {
  void getEquipments();
  void getSalas();
});
</script>

<template>
  <q-page class="q-pa-md bg-grey-1">
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-card flat bordered class="shadow-2">
          <q-tabs
            v-model="tab"
            dense
            class="text-grey-7 bg-white"
            active-color="primary"
            indicator-color="primary"
            align="left"
            narrow-indicator
          >
            <q-tab name="consultar" icon="search" label="Consultar" />
            <q-tab name="cadastrar" icon="add_circle" label="Cadastrar" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="tab" animated class="bg-transparent">
            <!-- CONSULTAR TAB -->
            <q-tab-panel name="consultar" class="q-pa-none">
              <q-table
                flat
                :rows="rows"
                :columns="columns"
                :filter="search"
                row-key="id"
                v-model:pagination="pagination"
                class="no-shadow"
              >
                <template v-slot:top-right>
                  <q-input 
                    outlined 
                    dense 
                    debounce="300" 
                    v-model="search" 
                    placeholder="Pesquisar..."
                    class="bg-white"
                  >
                    <template v-slot:append>
                      <q-icon name="search" />
                    </template>
                  </q-input>
                </template>

                <template v-slot:body-cell-foto="props">
                  <q-td :props="props">
                    <q-avatar v-if="props.row.foto" rounded size="48px" class="cursor-pointer" @click="openImage(props.row.foto)">
                      <img :src="props.row.foto" style="object-fit: cover">
                    </q-avatar>
                    <q-icon v-else name="image" size="32px" color="grey-4" />
                  </q-td>
                </template>

                <template v-slot:body-cell-manual="props">
                  <q-td :props="props">
                    <q-btn 
                      v-if="props.row.manual" 
                      flat round color="primary" 
                      icon="description" 
                      type="a" :href="props.row.manual" target="_blank"
                    >
                      <q-tooltip>Ver Manual</q-tooltip>
                    </q-btn>
                    <q-icon v-else name="block" color="grey-3" />
                  </q-td>
                </template>

                <template v-slot:body-cell-acoes="props">
                  <q-td :props="props" class="q-gutter-x-sm">
                    <q-btn flat round dense color="secondary" icon="build" @click="openMaintenanceDialog(props.row)">
                      <q-tooltip>Manutenção</q-tooltip>
                    </q-btn>
                    <q-btn flat round dense color="primary" icon="edit" @click="openEditDialog(props.row)">
                      <q-tooltip>Editar</q-tooltip>
                    </q-btn>
                    <q-btn flat round dense color="negative" icon="delete" @click="deleteEquipment(props.row.patrimonio)">
                      <q-tooltip>Excluir</q-tooltip>
                    </q-btn>
                  </q-td>
                </template>
              </q-table>
            </q-tab-panel>

            <!-- CADASTRAR TAB -->
            <q-tab-panel name="cadastrar">
              <div class="row justify-center">
                <div class="col-12 col-md-8">
                  <q-card flat bordered class="q-pa-md bg-white">
                    <div class="text-h6 q-mb-md">Novo Equipamento</div>
                    <q-form @submit.prevent="registerEquipment" class="q-gutter-md">
                      <div class="row q-col-gutter-md">
                        <div class="col-12 col-sm-8">
                          <q-input 
                            v-model="equipmentForm.nome" 
                            label="Nome do Equipamento" 
                            outlined dense
                            required
                            :rules="[val => !!val || 'Campo obrigatório']"
                          />
                        </div>
                        <div class="col-12 col-sm-4">
                          <q-input 
                            v-model="equipmentForm.patrimonio" 
                            label="Patrimônio" 
                            outlined dense
                            required
                            :rules="[val => !!val || 'Campo obrigatório']"
                          />
                        </div>
                        <div class="col-12">
                          <q-input 
                            v-model="equipmentForm.descricao" 
                            label="Descrição" 
                            outlined dense autogrow
                          />
                        </div>
                        <div class="col-12 col-sm-6">
                          <q-select
                            v-model="equipmentForm.sala"
                            :options="salas"
                            option-label="numero"
                            option-value="id"
                            emit-value
                            map-options
                            label="Sala"
                            outlined dense
                          >
                            <template v-slot:option="scope">
                              <q-item v-bind="scope.itemProps">
                                <q-item-section>
                                  <q-item-label>{{ scope.opt.numero }}</q-item-label>
                                  <q-item-label caption>{{ scope.opt.nome }}</q-item-label>
                                </q-item-section>
                              </q-item>
                            </template>
                          </q-select>
                        </div>
                        <div class="col-12 col-sm-6 flex items-center">
                          <q-checkbox v-model="equipmentForm.defeito" label="Apresenta defeito?" color="negative" />
                        </div>
                        
                        <div class="col-12 col-sm-6">
                          <q-file v-model="equipmentForm.foto" label="Foto do Equipamento" outlined dense accept="image/*">
                            <template v-slot:prepend>
                              <q-icon name="image" />
                            </template>
                          </q-file>
                        </div>
                        <div class="col-12 col-sm-6">
                          <q-file v-model="equipmentForm.manual" label="Manual (PDF)" outlined dense accept=".pdf">
                            <template v-slot:prepend>
                              <q-icon name="description" />
                            </template>
                          </q-file>
                        </div>
                      </div>

                      <div class="flex justify-end q-mt-lg">
                        <q-btn label="Limpar" flat color="grey" @click="resetForm" class="q-mr-sm" />
                        <q-btn label="Cadastrar Equipamento" type="submit" color="primary" rounded />
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

    <!-- MAINTENANCE DIALOG -->
    <q-dialog v-model="showDialog">
      <q-card style="min-width: 450px">
        <q-card-section class="bg-secondary text-white">
          <div class="text-h6">Manutenções: {{ selectedNome }}</div>
          <div class="text-caption">Patrimônio: {{ selectedPatrimonio }}</div>
        </q-card-section>

        <q-card-section class="q-pt-md">
          <q-input 
            v-model="descManutencao" 
            label="Nova nota de manutenção" 
            outlined dense autogrow
            @keyup.enter="registerManutencao(descManutencao, selectedPatrimonio)"
          >
            <template v-slot:append>
              <q-btn round dense flat icon="send" @click="registerManutencao(descManutencao, selectedPatrimonio)" />
            </template>
          </q-input>
        </q-card-section>

        <q-separator />

        <q-card-section style="max-height: 50vh" class="scroll">
          <q-list separator>
            <q-item v-for="manutencao in manutencoes" :key="manutencao.id">
              <q-item-section>
                <q-item-label>{{ manutencao.descricao }}</q-item-label>
                <q-item-label caption>
                  {{ format(new Date(manutencao.data), 'dd/MM/yyyy HH:mm') }} • {{ manutencao.funcionario_nome }}
                </q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="manutencoes.length === 0">
              <q-item-section class="text-italic text-grey">Sem registros de manutenção.</q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right">
          <q-btn flat label="Fechar" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- EDIT DIALOG -->
    <q-dialog v-model="showEditDialog">
      <q-card style="min-width: 500px">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Editar Equipamento</div>
        </q-card-section>

        <q-card-section class="q-gutter-md q-pt-md">
          <q-input v-model="editForm.nome" label="Nome" outlined dense />
          <q-input v-model="editForm.patrimonio" label="Patrimônio" outlined dense />
          <q-input v-model="editForm.descricao" label="Descrição" outlined dense autogrow />
          <q-select
            v-model="editForm.sala"
            :options="salas"
            option-label="numero"
            option-value="id"
            emit-value
            map-options
            label="Sala"
            outlined dense
          />
          <q-checkbox v-model="editForm.defeito" label="Defeito" color="negative" />
          
          <div class="row q-col-gutter-sm">
            <div class="col-6">
              <q-file v-model="editFoto" label="Nova Foto" outlined dense accept="image/*" />
            </div>
            <div class="col-6">
              <q-file v-model="editManual" label="Novo Manual" outlined dense accept=".pdf" />
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" v-close-popup />
          <q-btn flat label="Salvar Alterações" color="primary" @click="updateEquipment" />
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<style scoped>
.q-tab-panel {
  padding: 16px;
}
</style>
