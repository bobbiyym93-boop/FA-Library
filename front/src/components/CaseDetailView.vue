<script setup>
defineProps({ form:{type:Object,required:true}, editing:Boolean, saving:Boolean, projectOptions:{type:Array,default:()=>[]}, productOptions:{type:Array,default:()=>[]}, technologyOptions:{type:Array,default:()=>[]} })
const emit=defineEmits(['close','edit','cancel-edit','save'])
</script>
<template>
  <main class="create-content">
    <div class="create-page-actions">
      <button type="button" class="home-danger-button" @click="editing?emit('cancel-edit'):emit('close')">取消</button>
      <button v-if="!editing" type="button" class="home-primary-button" @click="emit('edit')">编辑</button>
      <button v-else type="submit" form="detail-case-form" class="home-primary-button" :disabled="saving">{{ saving?'保存中…':'保存' }}</button>
    </div>
    <form id="detail-case-form" class="create-workspace" @submit.prevent="emit('save')">
      <section class="information-panel"><h1>Information</h1>
        <label class="field-label">Case ID <span>*</span><input v-model="form.case_id" class="field-control readonly" readonly /></label>
        <label class="field-label">Project <span>*</span><select v-model="form.project" class="field-control" :disabled="!editing" required><option v-for="option in projectOptions" :key="option" :value="option">{{ option }}</option></select></label>
        <label class="field-label">Product <span>*</span><select v-model="form.product" class="field-control" :disabled="!editing" required><option v-for="option in productOptions" :key="option" :value="option">{{ option }}</option></select></label>
        <label class="field-label">Technology <span>*</span><select v-model="form.technology" class="field-control" :disabled="!editing" required><option v-for="option in technologyOptions" :key="option" :value="option">{{ option }}</option></select></label>
        <label class="field-label">Fail Type<input v-model.trim="form.fail_type" class="field-control" :readonly="!editing" /></label>
        <label class="field-label">Fail Mode <span>*</span><input v-model.trim="form.fail_model" class="field-control" :readonly="!editing" required /></label>
      </section>
      <section class="analysis-panel"><h2>Root Cause</h2></section><section class="analysis-panel"><h2>Improvement</h2></section><section class="analysis-panel"><h2>Result</h2></section>
    </form>
  </main>
</template>
