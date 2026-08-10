<script setup>
defineProps({ form:{type:Object,required:true}, saving:Boolean, projectOptions:{type:Array,default:()=>[]}, productOptions:{type:Array,default:()=>[]}, technologyOptions:{type:Array,default:()=>[]} })
const emit=defineEmits(['cancel','submit'])
</script>
<template>
  <main class="create-content">
    <div class="create-page-actions"><button type="button" class="home-danger-button" @click="emit('cancel')">取消</button><button type="submit" form="create-case-form" class="home-primary-button" :disabled="saving">编辑</button></div>
    <form id="create-case-form" class="create-workspace" @submit.prevent="emit('submit')">
      <section class="information-panel"><h1>Information</h1>
        <label class="field-label">Case ID <span>*</span><input v-model="form.case_id" class="field-control readonly" readonly required /></label>
        <label class="field-label">Project <span>*</span><select v-model="form.project" class="field-control" required><option value="" disabled>Select project</option><option v-for="option in projectOptions" :key="option" :value="option">{{ option }}</option></select></label>
        <label class="field-label">Product <span>*</span><select v-model="form.product" class="field-control" required><option value="" disabled>Select product</option><option v-for="option in productOptions" :key="option" :value="option">{{ option }}</option></select></label>
        <label class="field-label">Technology <span>*</span><select v-model="form.technology" class="field-control" required><option value="" disabled>Select technology</option><option v-for="option in technologyOptions" :key="option" :value="option">{{ option }}</option></select></label>
        <label class="field-label">Fail Type<input v-model.trim="form.fail_type" class="field-control" required placeholder="Enter fail type" /></label>
        <label class="field-label">Fail Mode <span>*</span><input v-model.trim="form.fail_model" class="field-control" required placeholder="Enter fail mode" /></label>
        <div class="create-actions"><button type="button" class="home-danger-button" @click="emit('cancel')">取消</button><button class="home-primary-button" :disabled="saving">{{ saving?'提交中…':'提交' }}</button></div>
      </section>
      <section class="analysis-panel"><h2>Root Cause</h2></section><section class="analysis-panel"><h2>Improvement</h2></section><section class="analysis-panel"><h2>Result</h2></section>
    </form>
  </main>
</template>
