<template>
    <div class="flex">
        <Sidebar />
        <div class="w-screen h-screen">
            <el-select v-model="value" multiple filterable allow-create default-first-option :reserve-keyword="false"
                placeholder="Laboratório">
                <el-option v-for="item in laboratorios" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-select v-model="value" multiple filterable allow-create default-first-option :reserve-keyword="false"
                placeholder="Disciplina">
                <el-option v-for="item in disciplinas" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-select v-model="value" multiple filterable allow-create default-first-option :reserve-keyword="false"
                placeholder="Professor">
                <el-option v-for="item in professores" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-button>Adicionar aulas</el-button>
        </div>
    </div>
</template>

<script lang="ts" setup>
import Sidebar from "../components/Sidebar.vue"

</script>

<script lang="ts">
export default {
    data() {
        return {

        }
    },
    methods: {

    }
}
</script>