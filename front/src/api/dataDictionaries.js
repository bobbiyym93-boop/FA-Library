import { request } from './request'

export function getDataDictionaries() {
  return request('/api/v1/data-dictionaries')
}

export function updateDataDictionary(type, options) {
  return request(`/api/v1/data-dictionaries/${type}`, {
    method: 'PUT',
    body: JSON.stringify({ options })
  })
}
