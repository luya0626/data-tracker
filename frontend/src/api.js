import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// ===== Lines =====

export function getLines() {
  return api.get('/lines').then(r => r.data)
}

export function createLine(name, color) {
  return api.post('/lines', { name, color }).then(r => r.data)
}

export function updateLine(id, data) {
  return api.put(`/lines/${id}`, data).then(r => r.data)
}

export function deleteLine(id) {
  return api.delete(`/lines/${id}`).then(r => r.data)
}

// ===== Data Points =====

export function getDataPoints(startDate, endDate) {
  const params = {}
  if (startDate) params.start_date = startDate
  if (endDate) params.end_date = endDate
  return api.get('/data-points', { params }).then(r => r.data)
}

export function createOrUpdateDataPoint(lineId, date, value, tag) {
  return api.post('/data-points', { line_id: lineId, date, value, tag: tag || '' }).then(r => r.data)
}

export function updateDataPoint(id, data) {
  return api.put(`/data-points/${id}`, data).then(r => r.data)
}

export function deleteDataPoint(id) {
  return api.delete(`/data-points/${id}`).then(r => r.data)
}

