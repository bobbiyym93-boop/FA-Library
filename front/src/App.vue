<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { batchDeleteCases, createCase, deleteCase, getCaseOptions, getCases, getNextCaseId, updateCase } from './api/cases'
import { getDashboardStatistics } from './api/dashboard'
import AppHeader from './components/AppHeader.vue'
import AppSidebar from './components/AppSidebar.vue'
import CaseCreateView from './components/CaseCreateView.vue'
import CaseDetailView from './components/CaseDetailView.vue'
import CaseTable from './components/CaseTable.vue'
import CaseToolbar from './components/CaseToolbar.vue'
import DashboardCharts from './components/DashboardCharts.vue'
import DataDictionaryView from './components/DataDictionaryView.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'

const query=ref(''), selected=ref([]), currentPage=ref(1), cases=ref([]), loading=ref(false), saving=ref(false), errorMessage=ref(''), createPageOpen=ref(false), detailPageOpen=ref(false), detailEditing=ref(false), editingId=ref(null), detailSnapshot=ref(null)
const activeView=ref('cases')
const confirmState=reactive({open:false,title:'确认删除',message:'',action:null,confirming:false})
const pageSize=10
const pagination=reactive({total:0,totalPages:0})
const statistics=reactive({totalCases:0,products:[],projects:[]})
const caseOptions=reactive({projects:[],products:[],technologies:[]})
const emptyForm=()=>({case_id:'',project:'',product:'',technology:'',fail_type:'',fail_model:''})
const form=reactive(emptyForm())
let searchTimer

const projectOptions=computed(()=>caseOptions.projects)
const productOptions=computed(()=>caseOptions.products)
const technologyOptions=computed(()=>caseOptions.technologies)
const allSelected=computed(()=>cases.value.length>0&&cases.value.every(row=>selected.value.includes(row.id)))
const pageNumbers=computed(()=>{const total=pagination.totalPages;if(total<=5)return Array.from({length:total},(_,index)=>index+1);const start=Math.min(Math.max(currentPage.value-2,1),total-4);return Array.from({length:5},(_,index)=>start+index)})

async function loadCases(){loading.value=true;errorMessage.value='';try{const data=await getCases({page:currentPage.value,pageSize,keyword:query.value.trim()});cases.value=data.items;pagination.total=data.pagination.total;pagination.totalPages=data.pagination.total_pages;selected.value=[]}catch(error){errorMessage.value=error.message}finally{loading.value=false}}
async function loadStatistics(){try{const data=await getDashboardStatistics();statistics.totalCases=data.total_cases;statistics.products=data.product_distribution;statistics.projects=data.cases_by_project}catch(error){errorMessage.value=error.message}}
async function loadCaseOptions(){try{const data=await getCaseOptions();caseOptions.projects=data.projects;caseOptions.products=data.products;caseOptions.technologies=data.technologies}catch(error){errorMessage.value=error.message}}
async function refreshPage(){await Promise.all([loadCases(),loadStatistics()])}
function toggleAll(){selected.value=allSelected.value?[]:cases.value.map(row=>row.id)}
async function openCreate(){Object.assign(form,emptyForm());try{const data=await getNextCaseId();form.case_id=data.case_id;createPageOpen.value=true}catch(error){errorMessage.value=error.message}}
function cancelCreate(){createPageOpen.value=false;Object.assign(form,emptyForm())}
async function submitCreate(){saving.value=true;errorMessage.value='';try{await createCase(form);cancelCreate();await refreshPage()}catch(error){errorMessage.value=error.message}finally{saving.value=false}}
function includeCurrentOption(options,value){if(value&&!options.includes(value))options.push(value)}
function assignCase(row){editingId.value=row.id;includeCurrentOption(caseOptions.projects,row.project);includeCurrentOption(caseOptions.products,row.product);includeCurrentOption(caseOptions.technologies,row.technology);for(const key of Object.keys(form))delete form[key];Object.assign(form,{case_id:row.case_id,project:row.project,product:row.product,technology:row.technology,fail_type:row.fail_type||'',fail_model:row.fail_model})}
function openDetail(row){assignCase(row);detailSnapshot.value={...form};detailEditing.value=false;detailPageOpen.value=true}
function closeDetail(){detailPageOpen.value=false;detailEditing.value=false;detailSnapshot.value=null}
function startDetailEdit(){detailSnapshot.value={...form};detailEditing.value=true}
function cancelDetailEdit(){Object.assign(form,detailSnapshot.value);detailEditing.value=false}
async function saveDetail(){saving.value=true;errorMessage.value='';try{const updated=await updateCase(editingId.value,form);assignCase(updated);detailSnapshot.value={...form};detailEditing.value=false;await refreshPage()}catch(error){errorMessage.value=error.message}finally{saving.value=false}}
function openEdit(row){assignCase(row);detailSnapshot.value={...form};detailEditing.value=true;detailPageOpen.value=true}
function askConfirm(message,action){confirmState.message=message;confirmState.action=action;confirmState.open=true}
function closeConfirm(){if(confirmState.confirming)return;confirmState.open=false;confirmState.action=null}
async function confirmAction(){if(!confirmState.action)return;confirmState.confirming=true;try{await confirmState.action();confirmState.open=false;confirmState.action=null}catch(error){errorMessage.value=error.message}finally{confirmState.confirming=false}}
function removeCase(row){askConfirm(`删除后将无法恢复，确认删除 ${row.case_id}？`,async()=>{await deleteCase(row.id);if(cases.value.length===1&&currentPage.value>1)currentPage.value-=1;await refreshPage()})}
function removeSelected(){if(!selected.value.length)return;const ids=[...selected.value];askConfirm(`删除后将无法恢复，确认删除选中的 ${ids.length} 条记录？`,async()=>{await batchDeleteCases(ids);await refreshPage()})}
function goToPage(page){if(page<1||page>pagination.totalPages||page===currentPage.value)return;currentPage.value=page;loadCases()}
function navigate(view){activeView.value=view;createPageOpen.value=false;detailPageOpen.value=false;errorMessage.value=''}
watch(query,()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{currentPage.value=1;loadCases()},350)})
onMounted(()=>Promise.all([refreshPage(),loadCaseOptions()]))
</script>

<template>
  <div class="app-shell">
    <AppHeader/><AppSidebar :active-view="activeView" @navigate="navigate"/>
    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}<button @click="errorMessage=''">×</button></div>
    <ConfirmDialog :open="confirmState.open" :title="confirmState.title" :message="confirmState.message" :confirming="confirmState.confirming" @cancel="closeConfirm" @confirm="confirmAction"/>
    <DataDictionaryView v-if="activeView==='dictionary'" @updated="loadCaseOptions" @error="errorMessage=$event"/>
    <CaseCreateView v-else-if="createPageOpen" :form="form" :saving="saving" :project-options="projectOptions" :product-options="productOptions" :technology-options="technologyOptions" @cancel="cancelCreate" @submit="submitCreate"/>
    <CaseDetailView v-else-if="detailPageOpen" :form="form" :editing="detailEditing" :saving="saving" :project-options="projectOptions" :product-options="productOptions" :technology-options="technologyOptions" @close="closeDetail" @edit="startDetailEdit" @cancel-edit="cancelDetailEdit" @save="saveDetail"/>
    <main v-else class="content">
      <DashboardCharts :products="statistics.products" :projects="statistics.projects"/>
      <CaseToolbar v-model:query="query" :selected-count="selected.length" @create="openCreate" @delete-selected="removeSelected"/>
      <CaseTable v-model:selected="selected" :cases="cases" :loading="loading" :all-selected="allSelected" :total="pagination.total" :current-page="currentPage" :total-pages="pagination.totalPages" :page-numbers="pageNumbers" @toggle-all="toggleAll" @view="openDetail" @edit="openEdit" @delete="removeCase" @page="goToPage"/>
    </main>
  </div>
</template>
