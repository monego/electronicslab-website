<template>
    <div class="flex bg-[#eff1f5]">
        <Sidebar />
        <div class="w-screen h-screen">
            <el-tabs type="border-card" class="demo-tabs">
                <el-tab-pane label="Cadastro de Equipamento">
                    <el-input v-model="equipment.name" placeholder="Nome do equipamento" />
                    <div style="margin: 50px 0" />
                        <el-input
                            v-model="equipment.description"
                            maxlength="200"
                            placeholder="Descrição"
                            show-word-limit
                            type="textarea"
                        />
                    <el-upload
                        v-model:file-list="fileList"
                        class="upload-demo"
                        multiple
                        :on-preview="handlePreview"
                        :on-remove="handleRemove"
                        :before-remove="beforeRemove"
                        :limit="3"
                        :on-exceed="handleExceed"
                        >
                    <el-button type="primary">Enviar</el-button>
                </el-upload>
                    <el-upload
                        v-model:file-list="fileList"
                        class="upload-demo"
                        multiple
                        :on-preview="handlePreview"
                        :on-remove="handleRemove"
                        :before-remove="beforeRemove"
                        :limit="3"
                        :on-exceed="handleExceed"
                        >
                    <el-button type="primary">Enviar</el-button>
                </el-upload>
                <el-button type="primary" @click="registerEquipment">Cadastrar</el-button>
                </el-tab-pane>
                <el-tab-pane label="Consultar Equipamentos">

                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script lang="ts">
import { reactive, ref } from 'vue'
import { computed } from 'vue'
import { ElTable } from 'element-plus'
import Sidebar from "../components/Sidebar.vue"
import axios from "axios"


export default {
    setup() {

        axios.defaults.withCredentials = true;

        const equipment = reactive({
            name: '',
            description: '',
        });

        const registerEquipment = () => {
            axios.post('http://127.0.0.1:8000/api/emprestimos/equipamento/', {
                nome: equipment.name,
                descricao: equipment.description
            })
            .then(response => {
                console.log(response.data);
            })
            .catch(error => {
                console.error(error);
            });
        };

        return {
            equipment,
            registerEquipment,
        };
    },
};

</script>