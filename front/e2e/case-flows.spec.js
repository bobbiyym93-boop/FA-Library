import { expect, test } from '@playwright/test'

function makeCases(count = 12) {
  return Array.from({ length: count }, (_, index) => ({
    id: index + 1,
    case_id: `FA20260810${String(index + 1).padStart(3, '0')}`,
    project: `Project${index % 3 + 1}`,
    product: `Product${index % 3 + 1}`,
    technology: `Technology${index % 3 + 1}`,
    fail_type: index % 2 ? 'Visual' : null,
    fail_model: `Mode ${index + 1}`
  }))
}

async function mockApi(page) {
  const state = { cases: makeCases(), requests: [], dictionaries: { project:['Project1','Project2','Project3'], product:['Product1','Product2','Product3'], technology:['Technology1','Technology2','Technology3'] } }
  await page.route('**/api/v1/**', async route => {
    const request = route.request()
    const url = new URL(request.url())
    const path = url.pathname
    const method = request.method()
    state.requests.push({ method, path, query: url.search })
    const respond = (data, status = 200) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify({ code: 0, message: 'success', data }) })

    if (path === '/api/v1/cases/options') return respond({ projects:state.dictionaries.project, products:state.dictionaries.product, technologies:state.dictionaries.technology })
    if (path === '/api/v1/data-dictionaries' && method === 'GET') return respond(Object.fromEntries(Object.entries(state.dictionaries).map(([type,values])=>[type,values.map((value,index)=>({id:index+1,dictionary_type:type,value,sort_order:index}))])))
    const dictionaryMatch=path.match(/^\/api\/v1\/data-dictionaries\/(project|product|technology)$/)
    if(dictionaryMatch&&method==='PUT'){state.dictionaries[dictionaryMatch[1]]=request.postDataJSON().options;return respond(state.dictionaries[dictionaryMatch[1]].map((value,index)=>({id:index+1,dictionary_type:dictionaryMatch[1],value,sort_order:index})))}
    if (path === '/api/v1/cases/next-case-id') return respond({ case_id: 'FA20260810013' })
    if (path === '/api/v1/dashboard/statistics') return respond({ total_cases: state.cases.length, product_distribution: [{ name: 'Product1', value: state.cases.length }], cases_by_project: [{ name: 'Project1', value: state.cases.length }] })
    if (path === '/api/v1/cases/batch-delete' && method === 'POST') { const ids = request.postDataJSON().ids; state.cases = state.cases.filter(item => !ids.includes(item.id)); return respond({ deleted: ids.length }) }
    if (path === '/api/v1/cases' && method === 'POST') { const item = { ...request.postDataJSON(), id: 13, case_id: 'FA20260810013' }; state.cases.unshift(item); return respond(item, 201) }
    if (path === '/api/v1/cases' && method === 'GET') {
      const keyword = (url.searchParams.get('keyword') || '').toLowerCase()
      const pageNumber = Number(url.searchParams.get('page') || 1)
      const pageSize = Number(url.searchParams.get('page_size') || 10)
      const filtered = state.cases.filter(item => Object.values(item).some(value => String(value ?? '').toLowerCase().includes(keyword)))
      const start = (pageNumber - 1) * pageSize
      return respond({ items: filtered.slice(start, start + pageSize), pagination: { page: pageNumber, page_size: pageSize, total: filtered.length, total_pages: Math.ceil(filtered.length / pageSize) } })
    }
    const match = path.match(/^\/api\/v1\/cases\/(\d+)$/)
    if (match && method === 'PUT') { const body=request.postDataJSON();const allowed=['project','product','technology','fail_type','fail_model'];if(Object.keys(body).some(key=>!allowed.includes(key)))return route.fulfill({status:400,contentType:'application/json',body:JSON.stringify({code:4001,message:`unknown fields: ${Object.keys(body).filter(key=>!allowed.includes(key)).join(', ')}`,data:null})});const index = state.cases.findIndex(item => item.id === Number(match[1])); state.cases[index] = { ...state.cases[index], ...body, case_id: state.cases[index].case_id, created_at:'2026-08-10T00:00:00Z', updated_at:'2026-08-10T01:00:00Z' }; return respond(state.cases[index]) }
    return respond(null, 404)
  })
  return state
}

test.beforeEach(async ({ page }) => {
  await mockApi(page)
  await page.goto('/')
  await expect(page.getByText('FA20260810001')).toBeVisible()
})

test('新增 Case 使用后端选项和编号预览', async ({ page }) => {
  await page.getByRole('button', { name: '新增' }).click()
  await expect(page.getByLabel('Case ID *')).toHaveValue('FA20260810013')
  await expect(page.getByLabel('Project *').locator('option')).toHaveCount(4)
  await page.getByLabel('Project *').selectOption('Project2')
  await page.getByLabel('Product *').selectOption('Product3')
  await page.getByLabel('Technology *').selectOption('Technology1')
  await page.getByLabel('Fail Mode *').fill('New Mode')
  await page.getByRole('button', { name: '提交', exact: true }).click()
  await expect(page.getByText('FA20260810013')).toBeVisible()
})

test('点击 Case ID 打开只读详情', async ({ page }) => {
  await page.getByRole('link', { name: 'FA20260810001' }).click()
  await expect(page.getByLabel('Case ID *')).toHaveValue('FA20260810001')
  await expect(page.getByLabel('Project *')).toBeDisabled()
  await expect(page.getByRole('button', { name: '编辑' })).toBeVisible()
})

test('Operation 编辑页面可保存修改', async ({ page }) => {
  await page.locator('tbody tr').first().getByTitle('编辑').click()
  await page.getByLabel('Product *').selectOption('Product2')
  await page.getByLabel('Fail Mode *').fill('Updated Mode')
  await page.getByRole('button', { name: '保存' }).click()
  await expect(page.getByLabel('Product *')).toBeDisabled()
  await expect(page.getByLabel('Fail Mode *')).toHaveValue('Updated Mode')
  await page.getByRole('button', { name: '编辑' }).click()
  await page.getByLabel('Fail Mode *').fill('Updated Again')
  await page.getByRole('button', { name: '保存' }).click()
  await expect(page.getByLabel('Fail Mode *')).toHaveValue('Updated Again')
  await expect(page.getByText(/unknown fields/)).toBeHidden()
})

test('搜索由后端过滤列表', async ({ page }) => {
  await page.getByPlaceholder('Search').fill('Mode 12')
  await expect(page.getByText('FA20260810012')).toBeVisible()
  await expect(page.getByText('FA20260810001')).toBeHidden()
})

test('分页可加载第二页', async ({ page }) => {
  await page.getByRole('button', { name: '2', exact: true }).click()
  await expect(page.getByText('FA20260810011')).toBeVisible()
  await expect(page.getByText('FA20260810001')).toBeHidden()
})

test('批量删除选中的 Case', async ({ page }) => {
  await page.locator('tbody tr').nth(0).locator('input[type="checkbox"]').check()
  await page.locator('tbody tr').nth(1).locator('input[type="checkbox"]').check()
  await page.locator('.toolbar-actions .danger').click()
  await expect(page.getByRole('alertdialog')).toContainText('确认删除选中的 2 条记录')
  await page.getByRole('button', { name: '确认删除' }).click()
  await expect(page.getByText('FA20260810001')).toBeHidden()
  await expect(page.getByText('FA20260810002')).toBeHidden()
})

test('数据字典编辑后同步到 Case 下拉选项', async ({ page }) => {
  await page.getByRole('button', { name: 'Data Dictionary' }).click()
  await expect(page.getByRole('heading', { name: 'Data Dictionary' })).toBeVisible()
  await page.locator('.dictionary-table tbody tr').first().getByRole('button', { name: 'Edit' }).click()
  await page.getByLabel('Option 1').fill('Phoenix')
  await page.getByRole('button', { name: 'Save Changes' }).click()
  await expect(page.locator('.dictionary-table tbody tr').first()).toContainText('Phoenix')
  await page.getByRole('button', { name: 'FA Library' }).click()
  await page.getByRole('button', { name: '新增' }).click()
  await expect(page.getByLabel('Project *').locator('option')).toContainText(['Select project','Phoenix','Project2','Project3'])
})
