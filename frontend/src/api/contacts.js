const BASE = '/api'

function explain(detail) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map(item => item.msg || '字段格式错误').join('；')
  return detail?.message || '请求失败，请稍后重试'
}

export async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${BASE}${path}`, options)
  } catch {
    throw new Error('无法连接服务，请检查后端是否启动')
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const error = new Error(explain(body.detail))
    error.status = response.status
    error.rows = body.detail?.errors || []
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
  return response ? response.json() : null
}

export const contactsApi = {
  async list({ q = '', favorite = false, signal } = {}) {
    const params = new URLSearchParams()
    if (q.trim()) params.set('q', q.trim())
    if (favorite) params.set('favorite', 'true')
    const response = await request(`/contacts${params.size ? `?${params}` : ''}`, { signal })
    return response.json()
  },
  async get(id) { return (await request(`/contacts/${encodeURIComponent(id)}`)).json() },
  create: contact => json('/contacts', 'POST', contact),
  update: (id, contact) => json(`/contacts/${encodeURIComponent(id)}`, 'PUT', contact),
  remove: id => request(`/contacts/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  favorite: (id, isFavorite) => json(`/contacts/${encodeURIComponent(id)}/favorite`, 'PATCH', { isFavorite }),
  async import(file) {
    const body = new FormData()
    body.append('file', file)
    return (await request('/contacts/import', { method: 'POST', body })).json()
  },
  async download(kind = 'export') {
    if (!['export', 'template'].includes(kind)) throw new Error('未知下载类型')
    const response = await request(`/contacts/${kind}`)
    const url = URL.createObjectURL(await response.blob())
    const a = document.createElement('a')
    a.href = url
    a.download = kind === 'template' ? 'contacts-template.xlsx' : 'contacts.xlsx'
    document.body.append(a)
    a.click()
    a.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  },
}
