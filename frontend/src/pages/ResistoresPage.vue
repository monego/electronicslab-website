<template>
  <q-page class="flex flex-center">
    <iframe
      src="/resistores/index.html"
      style="width: 100%; height: calc(100vh - 80px); border: none;"
      title="Calculador de Resistores"
    ></iframe>
  </q-page>
</template>

<script setup lang="ts">
defineOptions({
  name: 'ResistoresPage'
});
</script>

<style scoped>
.q-page {
  overflow: hidden;
}
</style>
