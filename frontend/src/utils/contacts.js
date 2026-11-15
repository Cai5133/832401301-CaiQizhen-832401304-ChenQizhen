export const methodTypes = [
  { value: 'phone', label: 'Phone' },
  { value: 'email', label: 'Email' },
  { value: 'social', label: 'Social' },
  { value: 'address', label: 'Address' },
]

export function validateContact(draft) {
  const errors = {}
  const name = draft.name.trim()
  if (!name) errors.name = 'Enter a contact name.'
  else if (name.length > 100) errors.name = 'Use 100 characters or fewer for the name.'
  const methods = []
  draft.methods.forEach((method, index) => {
    const value = method.value.trim()
    const label = method.label.trim()
    if (!value && !label) return // Ignore new rows that are still empty.
    if (!value) errors[index] = 'Enter a value or remove this row.'
    else if (value.length > 1000) errors[index] = 'Use 1,000 characters or fewer for the value.'
    else if (!methodTypes.some(item => item.value === method.type)) errors[index] = 'Choose a valid contact method.'
    else if (method.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) errors[index] = 'Enter a valid email, such as name@example.com.'
    if (label.length > 50) errors[index] = 'Use 50 characters or fewer for the label.'
    methods.push({ type: method.type, label, value })
  })
  return { errors, payload: { name, isFavorite: Boolean(draft.isFavorite), methods } }
}

export function filterContacts(contacts, query, favoritesOnly) {
  const term = query.trim().toLocaleLowerCase()
  return contacts.filter(contact => (!favoritesOnly || contact.isFavorite) && (!term ||
    contact.name.toLocaleLowerCase().includes(term) || contact.methods.some(method => method.value.toLocaleLowerCase().includes(term))))
}

export function validateUpload(file) {
  if (!file) return 'Choose an Excel file first.'
  if (!/\.xlsx$/i.test(file.name)) return 'Only .xlsx files are supported. Convert your file to an Excel workbook.'
  if (file.size === 0) return 'This file is empty. Choose another file.'
  if (file.size > 5 * 1024 * 1024) return 'Choose a file no larger than 5 MB.'
  return ''
}

export function checkContact(contact) {
  const valid = contact && Number.isInteger(contact.id) && typeof contact.name === 'string' &&
    contact.name.trim() && typeof contact.isFavorite === 'boolean' && Array.isArray(contact.methods) &&
    contact.methods.every(method => methodTypes.some(type => type.value === method.type) &&
      typeof method.value === 'string' && (method.label == null || typeof method.label === 'string'))
  if (!valid) throw new Error('The server returned an invalid contact. Please check the API.')
  return { ...contact, methods: contact.methods.map(method => ({ ...method, label: method.label || '' })) }
}

export function initials(name) {
  const parts = name.trim().split(/\s+/)
  return (parts.length > 1 ? parts[0][0] + parts[parts.length - 1][0] : parts[0].slice(0, 2)).toUpperCase()
}
