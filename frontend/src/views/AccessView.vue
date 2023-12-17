<script lang="ts" setup>
import { computed, ref } from 'vue'
import Sidebar from "../components/Sidebar.vue"
import { ElTable } from 'element-plus'
import axios from 'axios';

const matricula = ref('')
const lab = ref('')

let student = [];
let selectedStudents = [];

function getLabs() {
    // List all classrooms for the selector

    axios.get('/api/laboratorio')
      .then(response => {
        lab.value = response.data.map(lab => ({ label: lab.nome, value: lab.id }));
      })
      .catch(error => {
        console.error('Erro ao carregar laboratórios:', error);
      });
}

function getStudent() {

    axios.get('/api/pessoa', {
        params: {
            matricula: matricula
        }
    }).then(response => {
        const { nome, matricula, email, telefone } = response.data;
        console.log(`Nome: ${nome}, Matrícula: ${matricula}, Email: ${email}, Telefone: ${telefone}`);
    }).catch(error => {
        console.error('Ocorreu um erro ao obter as informações do aluno:', error);
    });
}

function registerStudent() {
        async function registerStudent() {
            try {
                const laboratorioResponse = await axios.get('/api/laboratorio', {
                    params: {
                        nome: lab.value
                    }
                });
                const laboratorioData = laboratorioResponse.data;

                const controleAcessoResponse = await axios.post('/api/controleacesso', {
                    matricula: matricula.value,
                    laboratorio: laboratorioData.id, // assuming "id" is the field to link laboratorio
                    hora_entrada: new Date().toISOString() // sending the current date in ISO format
                });

                // Handle the response from the ControleAcesso model if necessary
                console.log('Acesso registrado:', controleAcessoResponse.data);
            } catch (error) {
                console.error('Erro ao registrar o estudante no controle de acesso:', error);
            }
        }
}

async function getAcccessList() {
    // Query the ControleAcesso model for active accesses where horario_saida is null
    student = await axios.get('/api/controleacesso', {
        params: {
            horario_saida: null
        }
    }).then(response => response.data)
    .catch(error => console.error('An error occurred:', error));
}

function releaseStudents() {

    for (const studentId of Object.keys(selectedStudents)) {
        axios.patch(`/api/controleacesso/${studentId}`, {
            hora_saida: new Date().toISOString()
        })
        .then(response => {
            console.log(`Hora de saída registrada para o aluno com ID: ${studentId}`);
        })
        .catch(error => {
            console.error('Erro ao registrar a hora de saída do aluno:', error);
        });
    }

    console.log("Aluno liberado!")
}

interface User {
    date: string
    name: string
    address: string
}

const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<User[]>([])
const toggleSelection = (rows?: User[]) => {
    if (rows) {
        rows.forEach((row) => {
            // TODO: improvement typing when refactor table
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-expect-error
            multipleTableRef.value!.toggleRowSelection(row, undefined)
        })
    } else {
        multipleTableRef.value!.clearSelection()
    }
}
const handleSelectionChange = (val: User[]) => {
    multipleSelection.value = val
}

const search = ref('')
const filterTableData = computed(() =>
    tableData.filter(
        (data) =>
            !search.value ||
            data.name.toLowerCase().includes(search.value.toLowerCase())
    )
)
const handleEdit = (index: number, row: User) => {
    console.log(index, row)
}
const handleDelete = (index: number, row: User) => {
    console.log(index, row)
}

const value = ref('')
const options = [
    {
        value: 'Option1',
        label: 'Option1',
    },
    {
        value: 'Option2',
        label: 'Option2',
    },
    {
        value: 'Option3',
        label: 'Option3',
    },
    {
        value: 'Option4',
        label: 'Option4',
    },
    {
        value: 'Option5',
        label: 'Option5',
    },
]

const tableData: User[] = [
    {
        date: '2016-05-03',
        name: 'Tom',
        address: 'No. 189, Grove St, Los Angeles',
    },
    {
        date: '2016-05-02',
        name: 'John',
        address: 'No. 189, Grove St, Los Angeles',
    },
    {
        date: '2016-05-04',
        name: 'Morgan',
        address: 'No. 189, Grove St, Los Angeles',
    },
    {
        date: '2016-05-01',
        name: 'Jessy',
        address: 'No. 189, Grove St, Los Angeles',
    },
]
</script>

<template>
    <div class="flex bg-[#eff1f5]">
        <Sidebar />
        <div class="w-screen h-screen">
            <el-tabs type="border-card" class="demo-tabs">
                <el-tab-pane label="Controle de Acesso">
                    <div class="h-screen">
                        <el-form label-position="right" label-width="100px" style="max-width: 460px">
                            <el-form-item label="Matrícula">
                                <el-input v-model="matricula" />
                            </el-form-item>
                            <div class="flex">
                                <el-form-item label="Sala">
                                    <el-select v-model="lab" filterable placeholder="Escolha a sala">
                                        <el-option v-for="item in lab" :key="item.value" :label="item.label"
                                            :value="item.value" />
                                    </el-select>
                                </el-form-item>
                            </div>
                            <el-button @click="registerStudent">Registrar</el-button>
                        </el-form>
                    </div>
                </el-tab-pane>
                <el-tab-pane label="Bolsistas">
                    <div class="h-screen">
                        <el-table :data="filterTableData" style="width: 100%">
                            <el-table-column type="selection" width="55" />
                            <el-table-column label="Bolsista" prop="name" />
                            <el-table-column label="Matrícula" prop="enroll" />
                            <el-table-column label="Horário" prop="time" />
                            <el-table-column label="Entrada" prop="entrada">
                                <template #default="scope">
                                    <el-button size="small"
                                        @click="handleDelete(scope.$index, scope.row)">Marcar</el-button>
                                </template>
                            </el-table-column>
                            <el-table-column label="Saída" prop="saida">
                                <template #default="scope">
                                    <el-button size="small"
                                        @click="handleDelete(scope.$index, scope.row)">Marcar</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </el-tab-pane>
                <el-tab-pane label="Atualmente registrados">
                    <div class="h-screen">
                        <el-table :data="filterTableData" style="width: 100%">
                            <el-table-column type="selection" width="55" />
                            <el-table-column label="Horário" prop="time" />
                            <el-table-column label="Matrícula" prop="enroll" />
                            <el-table-column label="Nome" prop="name" />
                            <el-table-column label="Sala" prop="classroom" />
                            <el-table-column align="right">
                                <template #header>
                                    <el-input v-model="search" size="small" placeholder="Digite para buscar" />
                                </template>
                                <template #default="scope">
                                    <el-button size="small"
                                        @click="handleDelete(scope.$index, scope.row)">Liberar</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <el-button>Liberar marcados</el-button>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>
