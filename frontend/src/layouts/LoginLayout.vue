<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
        <q-toolbar>
          <q-avatar square>
            <img src="/Icone.ico">
          </q-avatar>
          <q-toolbar-title>
                NUPEDEE
          </q-toolbar-title>
        </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

  </q-layout>
</template>

<script setup lang="ts">

defineOptions({
  name: 'LoginLayout',
});

</script>

<style lang="scss">
body {
  background-color: #eeeeee; /* Cinza claro */
}
</style>
