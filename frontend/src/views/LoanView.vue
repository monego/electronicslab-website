<!-- Empréstimos e Devoluções -->

<script lang="ts" setup>
import Sidebar from "../components/Sidebar.vue"
import {
    Check,
    Delete,
    Edit,
    Message,
    Search,
    Star,
} from '@element-plus/icons-vue'
</script>

<template>
    <div class="bg-[#eff1f5] flex">
        <Sidebar />
        <div class="w-full h-screen">
            <el-tabs type="border-card" class="demo-tabs">
                <el-tab-pane label="Empréstimo">
                    <div class="h-screen">
                        <div class="mb-3 xl:w-full">
                            <el-form label-position="right" label-width="100px" style="max-width: 460px">
                                <el-form-item label="Autenticação">
                                    <el-input />
                                </el-form-item>
                                <el-form-item label="Matrícula">
                                    <el-input />
                                </el-form-item>
                                <el-form-item label="Sala">
                                    <el-input />
                                </el-form-item>
                            </el-form>
                            <el-table :data="rows" style="width: 100%" max-height="250">
                                <el-table-column fixed prop="date" label="Patrimônio" width="190">
                                    <template #default>
                                        <el-input v-model="input" placeholder="Patrimônio... [opcional]" />
                                    </template>
                                </el-table-column>
                                <el-table-column prop="name" label="Descrição" width="250">
                                    <template #default>
                                        <el-input v-model="input" placeholder="Qual o equipamento..." />
                                    </template>
                                </el-table-column>
                                <el-table-column fixed="right" label="Excluir" width="100">
                                    <template #default="scope">
                                        <el-button link type="danger" :icon="Delete" circle
                                            @click.prevent="removeRow(scope.$index)" />
                                    </template>
                                </el-table-column>
                            </el-table>
                            <el-button @click="addRow">Adicionar item</el-button>
                            <el-button @click="registerLoan">Registrar
                                empréstimo</el-button>
                        </div>
                    </div>
                </el-tab-pane>
                <el-tab-pane label="Devolução">
                    <div class="h-screen">
                        <el-table :data="filterTableData" style="width: 100%">
                            <el-table-column label="Autenticação" prop="time" />
                            <el-table-column label="Nome" prop="name" />
                            <el-table-column label="Descrição" prop="enroll" />
                            <el-table-column label="Horário" prop="time" />
                            <el-table-column label="Devolução" prop="return">
                                <template #default>
                                    <el-button link type="primary" size="small" @click="handleClick">Devolver</el-button>
                                </template>
                            </el-table-column>
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
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>