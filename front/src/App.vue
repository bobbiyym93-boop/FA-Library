<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { batchDeleteCases, createCase, deleteCase, getCases, updateCase } from './api/cases'
import { getDashboardStatistics } from './api/dashboard'

const deleteIcon = 'https://www.figma.com/api/mcp/asset/0190fa68-8e3e-437d-8db8-d6bc194bb24e.svg'
const editIcon = 'https://www.figma.com/api/mcp/asset/ae637a39-3eef-4263-904f-0a5cf1896695.svg'
const chartColors = ['#387deb', '#4db88c', '#f5a33d', '#a673e5', '#e56b6f', '#45a9c7']

const query = ref('')
const selected = ref([])
const currentPage = ref(1)
const pageSize = 10
const cases = ref([])
const pagination = reactive({ total: 0, totalPages: 0 })
const statistics = reactive({ totalCases: 0, products: [], projects: [] })
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const dialogOpen = ref(false)
const editingId = ref(null)
const form = reactive(emptyForm())
let searchTimer

function emptyForm() {
  return { case_id: '', project: '', product: '', technology: '', fail_type: '', fail_model: '' }
}

const allSelected = computed(() => cases.value.length > 0 && cases.value.every(row => selected.value.includes(row.id)))
const pageNumbers = computed(() => {
  const total = pagination.totalPages
  if (total <= 5) return Array.from({ length: total }, (_, index) => index + 1)
  const start = Math.min(Math.max(currentPage.value - 2, 1), total - 4)
  return Array.from({ length: 5 }, (_, index) => start + index)
})
const productTotal = computed(() => statistics.products.reduce((sum, item) => sum + item.value, 0))
const pieStyle = computed(() => {
  if (!productTotal.value) return { background: '#edf0f5' }
  let cursor = 0
  const slices = statistics.products.map((item, index) => {
    const start = cursor
    cursor += item.value / productTotal.value * 100
    return `${chartColors[index % chartColors.length]} ${start}% ${cursor}%`
  })
  return { background: `conic-gradient(${slices.join(',')})` }
})
const chartMax = computed(() => Math.max(1, ...statistics.projects.map(item => item.value)))

async function loadCases() {
  loading.value = true
  errorMessage.value = ''
  try {
    const data = await getCases({ page: currentPage.value, pageSize, keyword: query.value.trim() })
    cases.value = data.items
    pagination.total = data.pagination.total
    pagination.totalPages = data.pagination.total_pages
    selected.value = []
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

async function loadStatistics() {
  try {
    const data = await getDashboardStatistics()
    statistics.totalCases = data.total_cases
    statistics.products = data.product_distribution
    statistics.projects = data.cases_by_project
  } catch (error) {
    errorMessage.value = error.message
  }
}

async function refreshPage() {
  await Promise.all([loadCases(), loadStatistics()])
}

function toggleAll() {
  selected.value = allSelected.value ? [] : cases.value.map(row => row.id)
}

function openCreateDialog() {
  editingId.value = null
  Object.assign(form, emptyForm())
  dialogOpen.value = true
}

function openEditDialog(row) {
  editingId.value = row.id
  Object.assign(form, {
    case_id: row.case_id,
    project: row.project,
    product: row.product,
    technology: row.technology,
    fail_type: row.fail_type,
    fail_model: row.fail_model
  })
  dialogOpen.value = true
}

async function saveCase() {
  saving.value = true
  errorMessage.value = ''
  try {
    if (editingId.value) await updateCase(editingId.value, form)
    else await createCase(form)
    dialogOpen.value = false
    await refreshPage()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    saving.value = false
  }
}

async function removeCase(row) {
  if (!window.confirm(`确认删除 ${row.case_id}？`)) return
  try {
    await deleteCase(row.id)
    if (cases.value.length === 1 && currentPage.value > 1) currentPage.value -= 1
    await refreshPage()
  } catch (error) {
    errorMessage.value = error.message
  }
}

async function removeSelected() {
  if (!selected.value.length) return
  if (!window.confirm(`确认删除选中的 ${selected.value.length} 条记录？`)) return
  try {
    await batchDeleteCases(selected.value)
    await refreshPage()
  } catch (error) {
    errorMessage.value = error.message
  }
}

function goToPage(page) {
  if (page < 1 || page > pagination.totalPages || page === currentPage.value) return
  currentPage.value = page
  loadCases()
}

watch(query, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadCases()
  }, 350)
})

onMounted(refreshPage)
</script>

<template>
  <div class="app-shell">
    <header class="topbar"><div class="brand">HiPHI</div></header>
    <aside class="sidebar">
      <nav><button class="nav-parent"><span>⌄</span><span>Library</span></button><button class="nav-child active">FA Library</button></nav>
    </aside>

    <main class="content">
      <div v-if="errorMessage" class="error-banner">{{ errorMessage }}<button @click="errorMessage = ''">×</button></div>

      <section class="charts" aria-label="Dashboard charts">
        <article class="card product-chart">
          <h2>Product Distribution</h2>
          <div class="product-chart-body">
            <div class="pie" :style="pieStyle" :aria-label="`${productTotal} cases by product`"></div>
            <ul class="legend">
              <li v-for="(item, index) in statistics.products" :key="item.name">
                <i :style="{ background: chartColors[index % chartColors.length] }"></i>
                <span>{{ item.name }}&nbsp;&nbsp;{{ item.value }} ({{ productTotal ? Math.round(item.value / productTotal * 100) : 0 }}%)</span>
              </li>
              <li v-if="!statistics.products.length" class="muted">暂无数据</li>
            </ul>
          </div>
        </article>

        <article class="card bar-chart">
          <h2>Cases by Project</h2><span class="axis-title-y">Case count</span>
          <div class="plot dynamic-plot">
            <div class="grid-line top"></div><div class="grid-line middle"></div><div class="grid-line bottom"></div>
            <div v-for="item in statistics.projects" :key="item.name" class="bar-column">
              <div class="bar" :style="{ height: `${Math.max(4, item.value / chartMax * 86)}px` }" :title="`${item.name}: ${item.value}`"></div><span>{{ item.name }}</span>
            </div>
            <span v-if="!statistics.projects.length" class="chart-empty">暂无数据</span>
          </div>
          <span class="axis-title-x">Project</span>
        </article>
      </section>

      <section class="toolbar">
        <label class="search"><span>⌕</span><input v-model="query" type="search" placeholder="Search" /></label>
        <div class="toolbar-actions"><button class="button primary" @click="openCreateDialog">新增</button><button class="button danger" :disabled="!selected.length" @click="removeSelected">删除</button></div>
      </section>

      <section class="table-area">
        <div class="table-card">
          <div class="table-scroll">
            <table>
              <thead><tr><th class="check"><input type="checkbox" :checked="allSelected" @change="toggleAll" /></th><th>Case ID</th><th>Project</th><th>Product</th><th>Technology</th><th>Fail Type</th><th>Fail Model</th><th>Operation</th></tr></thead>
              <tbody>
                <tr v-for="row in cases" :key="row.id">
                  <td class="check"><input v-model="selected" type="checkbox" :value="row.id" /></td>
                  <td><a href="#" @click.prevent="openEditDialog(row)">{{ row.case_id }}</a></td><td>{{ row.project }}</td><td>{{ row.product }}</td><td>{{ row.technology }}</td><td>{{ row.fail_type }}</td><td>{{ row.fail_model }}</td>
                  <td><div class="row-actions"><button title="删除" @click="removeCase(row)"><img :src="deleteIcon" alt="删除" /></button><button title="编辑" @click="openEditDialog(row)"><img :src="editIcon" alt="编辑" /></button></div></td>
                </tr>
                <tr v-if="loading"><td colspan="8" class="empty">正在加载…</td></tr>
                <tr v-else-if="!cases.length"><td colspan="8" class="empty">暂无匹配数据</td></tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="pagination">
          <span>Total {{ pagination.total }}</span><button :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">Prev</button>
          <button v-for="page in pageNumbers" :key="page" :class="{ current: currentPage === page }" @click="goToPage(page)">{{ page }}</button>
          <button :disabled="currentPage >= pagination.totalPages" @click="goToPage(currentPage + 1)">Next</button>
        </div>
      </section>
    </main>

    <div v-if="dialogOpen" class="modal-backdrop" @click.self="dialogOpen = false">
      <form class="case-dialog" @submit.prevent="saveCase">
        <div class="dialog-header"><h2>{{ editingId ? '编辑 Case' : '新增 Case' }}</h2><button type="button" @click="dialogOpen = false">×</button></div>
        <div class="form-grid">
          <label>Case ID<input v-model.trim="form.case_id" required placeholder="C-2026-0812" /></label>
          <label>Project<input v-model.trim="form.project" required placeholder="Phoenix" /></label>
          <label>Product<input v-model.trim="form.product" required placeholder="Alpha X" /></label>
          <label>Technology<input v-model.trim="form.technology" required placeholder="5G" /></label>
          <label>Fail Type<input v-model.trim="form.fail_type" required placeholder="Performance" /></label>
          <label>Fail Model<input v-model.trim="form.fail_model" required placeholder="FM-023" /></label>
        </div>
        <div class="dialog-actions"><button type="button" class="cancel" @click="dialogOpen = false">取消</button><button class="save" :disabled="saving">{{ saving ? '保存中…' : '保存' }}</button></div>
      </form>
    </div>
  </div>
</template>
