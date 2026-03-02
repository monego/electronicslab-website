<template>
  <q-item
    clickable
    tag="a"
    :href="link"
    class="essential-link q-mb-sm rounded-borders"
    active-class="essential-link-active"
  >
    <q-item-section v-if="icon" avatar class="link-icon-section">
      <q-icon :name="icon" size="24px" />
    </q-item-section>

    <q-item-section>
      <q-item-label class="text-weight-bold">{{ title }}</q-item-label>
      <q-item-label caption class="text-grey-6">{{ caption }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
defineOptions({
  name: 'EssentialLink',
});

export interface EssentialLinkProps {
  title: string;
  caption?: string;
  link?: string;
  icon?: string;
}

withDefaults(defineProps<EssentialLinkProps>(), {
  caption: '',
  link: '#',
  icon: '',
});
</script>

<style lang="scss" scoped>
.essential-link {
  transition: all 0.2s ease;
  color: #4b5563;
  padding: 12px 16px;
  border-radius: 12px !important;

  &:hover {
    background: rgba(25, 118, 210, 0.05);
    color: var(--q-primary);

    .link-icon-section {
      color: var(--q-primary);
    }
  }
}

.link-icon-section {
  color: #9ca3af;
  min-width: 44px;
}
</style>
