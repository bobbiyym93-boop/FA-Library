<script setup>
defineProps({ open:Boolean, title:{type:String,default:'Confirm'}, message:{type:String,default:''}, confirming:Boolean })
const emit=defineEmits(['cancel','confirm'])
</script>

<template>
  <div v-if="open" class="modal-backdrop" @mousedown.self="emit('cancel')">
    <section class="confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-message">
      <header class="confirm-dialog-header"><h2 id="confirm-title">{{ title }}</h2><button aria-label="Close" @click="emit('cancel')">×</button></header>
      <p id="confirm-message" class="confirm-dialog-message">{{ message }}</p>
      <footer class="confirm-dialog-footer"><button class="confirm-cancel" :disabled="confirming" @click="emit('cancel')">取消</button><button class="confirm-danger" :disabled="confirming" @click="emit('confirm')">{{ confirming?'处理中…':'确认删除' }}</button></footer>
    </section>
  </div>
</template>
