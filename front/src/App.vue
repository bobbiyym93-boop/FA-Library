<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { batchDeleteCases, createCase, deleteCase, getCases, updateCase } from './api/cases'
import { getDashboardStatistics } from './api/dashboard'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'
import CaseCreateView from './components/CaseCreateView.vue'
import CaseEditDialog from './components/CaseEditDialog.vue'
import CaseTable from './components/CaseTable.vue'
import CaseToolbar from './components/CaseToolbar.vue'
import DashboardCharts from './components/DashboardCharts.vue'

const query=ref(''), selected=ref([]), currentPage=ref(1), cases=ref([]), loading=ref(false), saving=ref(false), errorMessage=ref(''), dialogOpen=ref(false), createPageOpen=ref(false), editingId=ref(null)
const pageSize=10
const pagination=reactive({total:0,totalPages:0})
const statistics=reactive({totalCases:0,products:[],projects:[]})
const emptyForm=()=>({case_id:'',project:'',product:'',technology:'',fail_type:'',fail_model:''})
const form=reactive(emptyForm())
let searchTimer

const projectOptions=computed(()=>statistics.projects.length?statistics.projects.map(item=>item.name):['Phoenix','Orion','Aurora'])
const productOptions=computed(()=>statistics.products.length?statistics.products.map(item=>item.name):['Alpha X','Beta Pro','Gamma'])
const technologyOptions=['5G','Wi-Fi','Bluetooth','Power','Software']
const allSelected=computed(()=>cases.value.length>0&&cases.value.every(row=>selected.value.includes(row.id)))
const pageNumbers=computed(()=>{const total=pagination.totalPages;if(total<=5)return Array.from({length:total},(_,index)=>index+1);const start=Math.min(Math.max(currentPage.value-2,1),total-4);return Array.from({length:5},(_,index)=>start+index)})

function generateCaseId(){const now=new Date();const date=[now.getFullYear(),String(now.getMonth()+1).padStart(2,'0'),String(now.getDate()).padStart(2,'0')].join('');return `FA${date}001`}
async function loadCases(){loading.value=true;errorMessage.value='';try{const data=await getCases({page:currentPage.value,pageSize,keyword:query.value.trim()});cases.value=data.items;pagination.total=data.pagination.total;pagination.totalPages=data.pagination.total_pages;selected.value=[]}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
async function loadStatistics(){try{const data=await getDashboardStatistics();statistics.totalCases=data.total_cases;statistics.products=data.product_distribution;statistics.projects=data.cases_by_project}catch(error){errorMessage.value=error.message}}
async function refreshPage(){await Promise.all([loadCases(),loadStatistics()])}
function toggleAll(){selected.value=allSelected.value?[]:cases.value.map(row=>row.id)}
function openCreate(){Object.assign(form,emptyForm());form.case_id=generateCaseId();createPageOpen.value=true}
function cancelCreate(){createPageOpen.value=false;Object.assign(form,emptyForm())}
async function submitCreate(){saving.value=true;errorMessage.value='';try{await createCase(form);cancelCreate();await refreshPage()}catch(error){errorMessage.value=error.message}finally{saving.value=false}}
function openEdit(row){editingId.value=row.id;Object.assign(form,{case_id:row.case_id,project:row.project,product:row.product,technology:row.technology,fail_type:row.fail_type,fail_model:row.fail_model});dialogOpen.value=true}
async function saveEdit(){saving.value=true;errorMessage.value='';try{await updateCase(editingId.value,form);dialogOpen.value=false;await refreshPage()}catch(error){errorMessage.value=error.message}finally{saving.value=false}}
async function removeCase(row){if(!window.confirm(`确认删除 ${row.case_id}？`))return;try{await deleteCase(row.id);if(cases.value.length===1&&currentPage.value>1)currentPage.value-=1;await refreshPage()}catch(error){errorMessage.value=error.message}}
async function removeSelected(){if(!selected.value.length||!window.confirm(`确认删除选中的 ${selected.value.length} 条记录？`))return;try{await batchDeleteCases(selected.value);await refreshPage()}catch(error){errorMessage.value=error.message}}
function goToPage(page){if(page<1||page>pagination.totalPages||page===currentPage.value)return;currentPage.value=page;loadCases()}
watch(query,()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{currentPage.value=1;loadCases()},350)})
onMounted(refreshPage)
</script>

<template>
  <div class="app-shell">
    <AppHeader/><AppSidebar/>
    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}<button @click="errorMessage=''">×</button></div>
    <CaseCreateView v-if="createPageOpen" :form="form" :saving="saving" :project-options="projectOptions" :product-options="productOptions" :technology-options="technologyOptions" @cancel="cancelCreate" @submit="submitCreate"/>
    <main v-else class="content">
      <DashboardCharts :products="statistics.products" :projects="statistics.projects"/>
      <CaseToolbar v-model:query="query" :selected-count="selected.length" @create="openCreate" @delete-selected="removeSelected"/>
      <CaseTable v-model:selected="selected" :cases="cases" :loading="loading" :all-selected="allSelected" :total="pagination.total" :current-page="currentPage" :total-pages="pagination.totalPages" :page-numbers="pageNumbers" @toggle-all="toggleAll" @edit="openEdit" @delete="removeCase" @page="goToPage"/>
    </main>
    <CaseEditDialog v-if="dialogOpen" :form="form" :saving="saving" @close="dialogOpen=false" @save="saveEdit"/>
  </div>
</template>
