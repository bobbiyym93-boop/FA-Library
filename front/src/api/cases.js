import { request } from './request'

const editableFields = ['project', 'product', 'technology', 'fail_type', 'fail_model']

function casePayload(payload) {
  return Object.fromEntries(editableFields.map(field => [field, payload[field]]))
}

export function getCases({ page = 1, pageSize = 10, keyword = '' } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize })
  if (keyword) params.set('keyword', keyword)
  return request(`/api/v1/cases?${params}`)
}

export function getCaseOptions() {
  return request('/api/v1/cases/options')
}

export function getNextCaseId() {
  return request('/api/v1/cases/next-case-id')
}

export function createCase(payload) {
  return request('/api/v1/cases', { method: 'POST', body: JSON.stringify(casePayload(payload)) })
}

export function updateCase(id, payload) {
  return request(`/api/v1/cases/${id}`, { method: 'PUT', body: JSON.stringify(casePayload(payload)) })
}

export function deleteCase(id) {
  return request(`/api/v1/cases/${id}`, { method: 'DELETE' })
}

export function batchDeleteCases(ids) {
  return request('/api/v1/cases/batch-delete', { method: 'POST', body: JSON.stringify({ ids }) })
}
