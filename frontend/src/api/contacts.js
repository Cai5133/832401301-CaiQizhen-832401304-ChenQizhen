import { displayMessage } from '../utils/messages.js'
const BASE = '/api'

export function explain(detail) {
  if (typeof detail === 'string') return displayMessage(detail)
  if (Array.isArray(detail)) return detail.map(item => [item.loc?.slice(1).join(' / '), displayMessage(item.msg, 'Invalid field value')].filter(Boolean).join(': ')).join('; ')
  return displayMessage(detail?.message, 'The request failed. Please try again.')
}

export async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${BASE}${path}`, { ...options, signal: options.signal || AbortSignal.timeout(30000) })
  } catch (cause) {
    if (cause.name === 'AbortError' && options.signal?.aborted) throw cause
    const writing = options.method && !['GET', 'HEAD'].includes(options.method)
    throw new Error(writing ? 'The connection was interrupted or timed out. Your changes may have been saved. Refresh the list before submitting again.' : 'The server could not be reached or timed out. Check the connection and try again.')
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const error = new Error(explain(body.detail || body.message || (response.status >= 500 ? 'The service is temporarily unavailable. Please try again later.' : `Request failed (${response.status})`)))
    error.status = response.status
    error.rows = Array.isArray(body.detail?.errors) ? body.detail.errors : []
    throw error
  }
  if (response.status === 204) return null
  return response
}

async function json(path, method, body) {
  const response = await request(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response) return null
  try { return await response.json() } catch { throw new Error('Invalid server response. Your changes may have been saved. Refresh the list before submitting again.') }
}

export const contactsApi = {
  async list({ q = '', favorite = false, signal } = {}) {
    const params = new URLSearchParams()
    if (q.trim()) params.set('q', q.trim())
    if (favorite) params.set('favorite', 'true')
    const response = await request(`/contacts${params.size ? `?${params}` : ''}`, { signal })
    try { return await response.json() } catch { throw new Error('The server returned an invalid contact response. Please check the API.') }
  },
  async get(id) { return (await request(`/contacts/${encodeURIComponent(id)}`)).json() },
  create: contact => json('/contacts', 'POST', contact),
  update: (id, contact) => json(`/contacts/${encodeURIComponent(id)}`, 'PUT', contact),
  remove: id => request(`/contacts/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  favorite: (id, isFavorite) => json(`/contacts/${encodeURIComponent(id)}/favorite`, 'PATCH', { isFavorite }),
  async import(file) {
    const body = new FormData()
    body.append('file', file)
    const response = await request('/contacts/import', { method: 'POST', body })
    try { return await response.json() } catch { throw new Error('Invalid import response. Refresh the list before importing again.') }
  },
  async download(kind = 'export') {
    if (!['export', 'template'].includes(kind)) throw new Error('Unknown download type')
    const response = await request(`/contacts/${kind}`)
    const blob = await response.blob()
    const signature = new Uint8Array(await blob.slice(0, 4).arrayBuffer())
    if (signature[0] !== 0x50 || signature[1] !== 0x4b || signature[2] !== 0x03 || signature[3] !== 0x04) {
      throw new Error('The server did not return a valid Excel file. Please check the download API.')
    }
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = kind === 'template' ? 'contacts-template.xlsx' : 'contacts.xlsx'
    document.body.append(a)
    a.click()
    a.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  },
}
