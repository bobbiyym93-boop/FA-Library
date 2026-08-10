<script setup>
defineProps({form:{type:Object,required:true},saving:Boolean})
const emit=defineEmits(['close','save'])
</script>
<template>
  <div class="modal-backdrop" @click.self="emit('close')"><form class="case-dialog" @submit.prevent="emit('save')">
    <div class="dialog-header"><h2>编辑 Case</h2><button type="button" @click="emit('close')">×</button></div>
    <div class="form-grid"><label>Case ID<input v-model.trim="form.case_id" required /></label><label>Project<input v-model.trim="form.project" required /></label><label>Product<input v-model.trim="form.product" required /></label><label>Technology<input v-model.trim="form.technology" required /></label><label>Fail Type<input v-model.trim="form.fail_type" required /></label><label>Fail Model<input v-model.trim="form.fail_model" required /></label></div>
    <div class="dialog-actions"><button type="button" class="cancel" @click="emit('close')">取消</button><button class="save" :disabled="saving">{{ saving?'保存中…':'保存' }}</button></div>
  </form></div>
</template>
