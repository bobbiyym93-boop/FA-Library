<script setup>
defineProps({ query: { type: String, default: '' }, selectedCount: { type: Number, default: 0 } })
const emit = defineEmits(['update:query', 'create', 'delete-selected'])
</script>
<template>
  <section class="toolbar">
    <label class="search"><span>⌕</span><input :value="query" type="search" placeholder="Search" @input="emit('update:query', $event.target.value)" /></label>
    <div class="toolbar-actions"><button class="button primary" @click="emit('create')">新增</button><button class="button danger" :disabled="!selectedCount" @click="emit('delete-selected')">删除</button></div>
  </section>
</template>
