import { request } from './request'

export function getCases({ page = 1, pageSize = 10, keyword = '' } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize })
  if (keyword) params.set('keyword', keyword)
  return request(`/api/v1/cases?${params}`)
}

export function createCase(payload) {
  return request('/api/v1/cases', { method: 'POST', body: JSON.stringify(payload) })
}

export function updateCase(id, payload) {
  return request(`/api/v1/cases/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
}

export function deleteCase(id) {
  return request(`/api/v1/cases/${id}`, { method: 'DELETE' })
}

export function batchDeleteCases(ids) {
  return request('/api/v1/cases/batch-delete', { method: 'POST', body: JSON.stringify({ ids }) })
}
