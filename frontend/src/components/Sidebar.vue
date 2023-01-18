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
        <el-menu-item index="2-3"><el-icon>
            <Mouse />
          </el-icon>Gerenciamento de Patrimônios</el-menu-item>
        <el-menu-item index="2-4"><el-icon>
            <Mouse />
          </el-icon>Verificação Patrimonial</el-menu-item>
        <el-menu-item index="2-5"><el-icon>
            <Mouse />
          </el-icon>Relação equip. e componentes</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="3">
        <template #title>
          <el-icon>
            <Calendar />
          </el-icon>
          <span>Aulas & Consultas</span>
        </template>
        <el-menu-item index="3-1"><el-icon>
            <DataBoard />
          </el-icon>Autorizar Aulas Pendentes</el-menu-item>
        <el-menu-item index="3-2"><el-icon>
            <DataBoard />
          </el-icon><a href="/cadastrar-aulas">Cadastrar Aulas</a></el-menu-item>
        <el-menu-item index="3-3"><el-icon>
            <Search />
          </el-icon>Consultar Aulas Marcadas</el-menu-item>
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
