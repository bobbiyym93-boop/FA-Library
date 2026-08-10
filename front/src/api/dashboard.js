import { request } from './request'

export function getDashboardStatistics() {
  return request('/api/v1/dashboard/statistics')
}
