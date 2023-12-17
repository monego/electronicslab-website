<!-- Lista de equipamentos (patrimônios) -->

<script lang="ts" setup>
import Sidebar from "../components/Sidebar.vue"
import { reactive, ref } from 'vue'
import axios from "axios"
import type { FormInstance, FormRules } from 'element-plus'

const nome = ref("")
const descricao = ref("")

interface EquipamentoForm {
    nome: string
    descricao: string
}

const EquipamentoRef = ref<FormInstance>()

const EquipamentoForm = reactive<EquipamentoForm>({
    nome: '',
    descricao: '',
})

const fotox = (event) => {
    return event.target.files[0];
}

// const manual = (event) => {
//     return event.target.files[0];
// }

const getEquipamento = () => {
    
}

const saveEquipamento = () => {
    axios({
        method: 'post',
        url: 'http://127.0.0.1:8000/api/emprestimos/equipamento/',
        data: {
            nome: nome,
            descricao: descricao,
            foto: foto,
            manual: manual,
        },
    }).then((response) => {
        let newEquipment = {
            'nome': response.data.nome,
            'descricao': response.data.descricao,
        }
    })
}
</script>

<template>
    <div class="flex bg-[#eff1f5]">
        <Sidebar />
        <div class="w-screen h-screen">
            <el-tabs type="border-card" class="demo-tabs">
                <el-tab-pane label="Cadastrar equipamento">
                    <el-form ref="">
                        <el-form-item label="Nome do equipamento">
                            <el-input v-model="nome" />
                        </el-form-item>
                    </el-form>
                    
                    <div style="margin: 50px 0" />
                    <el-input v-model="descricao" maxlength="200" placeholder="Descrição" show-word-limit type="textarea" />
                    <el-upload v-model:file-list="foto" class="upload-demo">    
                        <el-button type="primary">
                            Enviar<el-icon class="el-icon--right">
                                <Upload />
                            </el-icon>
                        </el-button>
                        <template #tip>
                            <div class="el-upload__tip">
                                Arquivos jpg/png.
                            </div>
                        </template>
                    </el-upload>
                    <el-upload v-model:file-list="manual" class="upload-demo">
                        <el-button type="primary">Enviar</el-button>
                        <template #tip>
                            <div class="el-upload__tip">
                                Arquivos PDF.
                            </div>
                        </template>
                    </el-upload>
                    <el-button type="primary" @click="saveEquipamento">Cadastrar</el-button>
                </el-tab-pane>
                <el-tab-pane label="Consultar Equipamentos">

                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>