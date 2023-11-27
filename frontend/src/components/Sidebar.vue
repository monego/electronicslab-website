<template>
  <el-row class="tac">
    <el-menu default-active="2" class="el-menu-vertical-demo" @open="handleOpen" @close="handleClose">
      <el-sub-menu index="1">
        <template #title>
          <el-icon>
            <location />
          </el-icon>
          <span>Atividades</span>
        </template>
        <el-menu-item index="1-1"><el-icon>
            <Goods />
          </el-icon>Painel de Requisições</el-menu-item>
        <el-menu-item index="1-2"><el-icon>
            <CreditCard />
          </el-icon>Solicitações de Compra</el-menu-item>
        <el-menu-item index="1-3"><el-icon>
            <Calendar />
          </el-icon>Jornada e Ocorrências</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="2">
        <template #title>
          <el-icon>
            <OfficeBuilding />
          </el-icon>
          <span>Salas & Equipamentos</span>
        </template>
        <el-menu-item index="2-1"><a href="/emprestimos"><el-icon>
              <Switch />
            </el-icon>Sistema de Empréstimos</a></el-menu-item>
        <el-menu-item index="2-2"><a href="/registros"><el-icon>
              <School />
            </el-icon>Sistema de Registros</a></el-menu-item>
        <el-menu-item index="2-3"><a href="/equipamentos"><el-icon>
            <Mouse />
          </el-icon>Equipamentos e componentes</a></el-menu-item>
      </el-sub-menu>
      <el-menu-item><el-icon>
          <DataLine />
        </el-icon>Estatísticas</el-menu-item>
    </el-menu>
  </el-row>
</template>
  
<script lang="ts" setup>
import {
  Calendar,
  CreditCard,
  DataBoard,
  DataLine,
  Document,
  Goods,
  Menu as IconMenu,
  Location,
  Mouse,
  OfficeBuilding,
  School,
  Search,
  Setting,
  Switch,
} from '@element-plus/icons-vue'
const handleOpen = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
</script>
