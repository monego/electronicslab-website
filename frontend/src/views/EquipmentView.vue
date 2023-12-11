<!-- Lista de equipamentos (patrimônios) -->

<script lang="ts" setup>
import Sidebar from "../components/Sidebar.vue"
import { ref } from 'vue'
import axios from "axios"

const nome = ref("")
const descricao = ref("")

const saveEquipamento = () => {
    axios({
        method: 'post',
        url: 'http://127.0.0.1:8000/api/emprestimos/equipamento/',
        data: {
            nome: nome,
            descricao: descricao,
        },
        auth: {
            username: '',
            password: '',
        }
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
                <el-tab-pane label="Cadastro de Equipamento">
                    <el-input v-model="nome" placeholder="Nome do equipamento" />
                    <div style="margin: 50px 0" />
                    <el-input v-model="descricao" maxlength="200" placeholder="Descrição" show-word-limit type="textarea" />
                    <el-upload v-model:file-list="foto" class="upload-demo">
                        <el-button type="primary">Enviar</el-button>
                        <el-button type="primary">
                            Upload<el-icon class="el-icon--right">
                                <Upload />
                            </el-icon>
                        </el-button>
                    </el-upload>
                    <el-upload v-model:file-list="manual" class="upload-demo">
                        <el-button type="primary">Enviar</el-button>
                    </el-upload>
                    <el-button type="primary" @click="saveEquipamento">Cadastrar</el-button>
                </el-tab-pane>
                <el-tab-pane label="Consultar Equipamentos">

                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>