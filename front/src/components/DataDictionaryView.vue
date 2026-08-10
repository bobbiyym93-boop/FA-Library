<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { getDataDictionaries, updateDataDictionary } from '../api/dataDictionaries'
import ConfirmDialog from './ConfirmDialog.vue'

const emit=defineEmits(['updated','error'])
const labels={project:'Project',product:'Product',technology:'Technology'}
const dictionaries=reactive({project:[],product:[],technology:[]})
const loading=ref(false),saving=ref(false),modalOpen=ref(false),editing=ref(false)
const form=reactive({type:'project',options:[]})
const deleteState=reactive({open:false,row:null,confirming:false})
const rows=computed(()=>Object.keys(labels).map(type=>({type,label:labels[type],items:dictionaries[type]})))

async function load(){loading.value=true;try{const data=await getDataDictionaries();for(const type of Object.keys(labels))dictionaries[type]=data[type]||[]}catch(error){emit('error',error.message)}finally{loading.value=false}}
function openAdd(){editing.value=false;form.type='project';form.options=[''];modalOpen.value=true}
function openEdit(row){editing.value=true;form.type=row.type;form.options=row.items.map(item=>item.value);modalOpen.value=true}
function close(){modalOpen.value=false;form.options=[]}
function addOption(){form.options.push('')}
function removeOption(index){form.options.splice(index,1)}
async function save(){saving.value=true;try{const options=form.options.map(value=>value.trim()).filter(Boolean);await updateDataDictionary(form.type,options);close();await load();emit('updated')}catch(error){emit('error',error.message)}finally{saving.value=false}}
function clearDictionary(row){deleteState.row=row;deleteState.open=true}
function closeDelete(){if(deleteState.confirming)return;deleteState.open=false;deleteState.row=null}
async function confirmDelete(){if(!deleteState.row)return;deleteState.confirming=true;try{await updateDataDictionary(deleteState.row.type,[]);await load();emit('updated')}catch(error){emit('error',error.message)}finally{deleteState.confirming=false;deleteState.open=false;deleteState.row=null}}
onMounted(load)
</script>

<template>
  <main class="dictionary-content">
    <ConfirmDialog :open="deleteState.open" title="确认删除" :message="`删除后将无法恢复，确认删除 ${deleteState.row?.label||''} 的全部选项？`" :confirming="deleteState.confirming" @cancel="closeDelete" @confirm="confirmDelete"/>
    <header class="dictionary-heading"><h1>Data Dictionary</h1><p>Manage reusable dropdown options used across FA Library forms.</p></header>
    <div class="dictionary-toolbar"><button class="dictionary-add" @click="openAdd">+ Add Option</button></div>
    <section class="dictionary-table-card">
      <table class="dictionary-table">
        <thead><tr><th>Dictionary Type</th><th>Options</th><th>Operation</th></tr></thead>
        <tbody>
          <tr v-if="loading"><td colspan="3" class="empty">Loading…</td></tr>
          <tr v-for="row in rows" v-else :key="row.type">
            <td>{{ row.label }}</td>
            <td :title="row.items.map(item=>item.value).join(', ')">{{ row.items.map(item=>item.value).join(', ') || '—' }}</td>
            <td class="dictionary-actions"><button @click="openEdit(row)">Edit</button><button @click="clearDictionary(row)">Delete</button></td>
          </tr>
        </tbody>
      </table>
    </section>

    <div v-if="modalOpen" class="modal-backdrop" @mousedown.self="close">
      <section class="dictionary-dialog" role="dialog" aria-modal="true" aria-labelledby="dictionary-dialog-title">
        <header class="dictionary-dialog-header"><h2 id="dictionary-dialog-title">{{ editing?'Edit Dictionary':'Add Option' }}</h2><button aria-label="Close" @click="close">×</button></header>
        <form @submit.prevent="save">
          <div class="dictionary-dialog-body">
            <label>Dictionary Type<select v-model="form.type" :disabled="editing"><option v-for="(label,type) in labels" :key="type" :value="type">{{ label }}</option></select></label>
            <label>Options</label>
            <div class="dictionary-option-list">
              <div v-for="(_,index) in form.options" :key="index" class="dictionary-option-row"><input v-model="form.options[index]" required maxlength="100" :aria-label="`Option ${index+1}`"/><button type="button" @click="removeOption(index)">Remove</button></div>
            </div>
            <button type="button" class="dictionary-add-another" @click="addOption">+ Add another option</button>
          </div>
          <footer class="dictionary-dialog-footer"><button type="button" class="dictionary-cancel" @click="close">Cancel</button><button class="dictionary-save" :disabled="saving||!form.options.length">{{ saving?'Saving…':'Save Changes' }}</button></footer>
        </form>
      </section>
    </div>
  </main>
</template>
