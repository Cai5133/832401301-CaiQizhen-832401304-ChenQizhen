<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import ContactList from './components/ContactList.vue'
import ContactDetail from './components/ContactDetail.vue'
import ContactForm from './components/ContactForm.vue'
import ImportDialog from './components/ImportDialog.vue'
import DeleteDialog from './components/DeleteDialog.vue'
import AppIcon from './components/AppIcon.vue'
import BookIllustration from './components/BookIllustration.vue'
import { contactsApi } from './api/contacts'
import { checkContact, filterContacts } from './utils/contacts'

const preview = import.meta.env.VITE_PREVIEW_MODE === 'true'
const contacts = ref([])
const selectedId = ref(null)
const search = ref('')
const favoritesOnly = ref(false)
const loading = ref(true)
const refreshing = ref(false)
const loadError = ref('')
const refreshError = ref('')
const mutation = ref('')
const downloading = ref('')
const modal = ref('')
const editing = ref(null)
const deleting = ref(null)
const formError = ref('')
const importError = ref('')
const importRows = ref([])
const importResult = ref(null)
const deleteError = ref('')
const toast = ref(null)
let toastTimer
const busy = computed(() => Boolean(mutation.value) || refreshing.value)
const visible = computed(() => filterContacts(contacts.value, search.value, favoritesOnly.value))
const selected = computed(() => visible.value.find(item => item.id === selectedId.value) || null)
const favoriteCount = computed(() => contacts.value.filter(item => item.isFavorite).length)
const multipleCount = computed(() => contacts.value.filter(item => item.methods.length > 1).length)

watch(visible, items => {
  if (!items.some(item => item.id === selectedId.value)) selectedId.value = items[0]?.id ?? null
})
function notify(message, type = 'success') {
  clearTimeout(toastTimer)
  toast.value = { message, type }
  toastTimer = setTimeout(() => { toast.value = null }, type === 'error' ? 10000 : 5000)
}

async function load(initial = false) {
  if (refreshing.value) return false
  if (initial) loading.value = true
  refreshing.value = true
  try {
    const data = await contactsApi.list()
    if (!Array.isArray(data.items)) throw new Error('The server response is missing the contact list.')
    const items = data.items.map(checkContact)
    if (new Set(items.map(item => item.id)).size !== items.length) throw new Error('The server returned duplicate contact IDs. Please check the API.')
    contacts.value = items
    loadError.value = ''
    refreshError.value = ''
    return true
  } catch (cause) {
    if (initial || loadError.value) loadError.value = cause.message
    else refreshError.value = `${cause.message}. Your previously loaded contacts are still shown.`
    return false
  } finally {
    refreshing.value = false
    loading.value = false
  }
}
function openForm(contact = null) {
  if (busy.value) return
  editing.value = contact
  formError.value = ''
  modal.value = 'form'
}
async function saveContact(payload) {
  if (mutation.value) return
  mutation.value = 'save'
  formError.value = ''
  try {
    const result = editing.value ? await contactsApi.update(editing.value.id, payload) : await contactsApi.create(payload)
    const contact = checkContact(result)
    const index = contacts.value.findIndex(item => item.id === contact.id)
    if (index < 0) contacts.value = [...contacts.value, contact]
    else contacts.value = contacts.value.map(item => item.id === contact.id ? contact : item)
    if (!editing.value) { search.value = ''; favoritesOnly.value = false }
    selectedId.value = contact.id
    modal.value = ''
    const synced = await load()
    notify(synced ? `${contact.name} saved` : 'Saved successfully. Refresh the list to verify your changes.', synced ? 'success' : 'error')
  } catch (cause) { formError.value = cause.message } finally { mutation.value = '' }
}
async function toggleFavorite(contact) {
  if (busy.value) return
  mutation.value = 'favorite'
  try {
    const updated = checkContact(await contactsApi.favorite(contact.id, !contact.isFavorite))
    contacts.value = contacts.value.map(item => item.id === updated.id ? updated : item)
    notify(updated.isFavorite ? `${updated.name} added to favorites` : `${updated.name} removed from favorites`)
  } catch (cause) { notify(cause.message, 'error') } finally { mutation.value = '' }
}
function openDelete(contact) {
  if (busy.value) return
  deleting.value = contact
  deleteError.value = ''
  modal.value = 'delete'
}
async function removeContact() {
  if (mutation.value) return
  mutation.value = 'delete'
  deleteError.value = ''
  try {
    await contactsApi.remove(deleting.value.id)
    contacts.value = contacts.value.filter(item => item.id !== deleting.value.id)
    modal.value = ''
    notify('Contact deleted')
  } catch (cause) { deleteError.value = cause.message } finally { mutation.value = '' }
}
function openImport() {
  importError.value = ''; importRows.value = []; importResult.value = null; modal.value = 'import'
}
async function importContacts(file) {
  if (mutation.value || importResult.value) return
  mutation.value = 'import'
  importError.value = ''; importRows.value = []
  try {
    const result = await contactsApi.import(file)
    if (!Number.isInteger(result.imported) || result.imported < 0 || !Array.isArray(result.errors) || result.errors.length) {
      throw new Error('Unexpected import response. Refresh the list before importing again.')
    }
    importResult.value = { ...result, synced: false } // The import succeeded; a failed refresh must not allow a duplicate upload.
    search.value = ''; favoritesOnly.value = false
    const synced = await load()
    importResult.value.synced = synced
    if (!synced) importError.value = 'Import completed, but the list could not refresh. Close this window and refresh the list before importing again.'
    else notify(`Imported ${result.imported} ${result.imported === 1 ? 'contact' : 'contacts'}`)
  } catch (cause) {
    importError.value = cause.message
    importRows.value = cause.rows || []
  } finally { mutation.value = '' }
}
async function download(kind) {
  if (downloading.value) return
  downloading.value = kind
  try {
    await contactsApi.download(kind)
    notify(kind === 'template' ? 'Template download started' : 'Contact export started')
  } catch (cause) {
    if (modal.value === 'import') importError.value = cause.message
    else notify(cause.message, 'error')
  } finally { downloading.value = '' }
}
async function copy(value) {
  try { await navigator.clipboard.writeText(value); notify('Copied to clipboard') }
  catch { notify('Clipboard access is unavailable. Select and copy the text manually.', 'error') }
}
onMounted(() => load(true))
onBeforeUnmount(() => clearTimeout(toastTimer))
</script>

<template>
  <div class="workspace">
    <aside class="sidebar">
      <a class="brand" href="./"><span class="brand-icon"><AppIcon name="book" :size="23" /></span><span>YOULIAN<small>Contact workspace</small></span></a>
      <p class="nav-label">DIRECTORY</p>
      <nav aria-label="Contact categories"><button :class="{ active: !favoritesOnly }" :aria-pressed="!favoritesOnly" @click="favoritesOnly = false"><AppIcon name="users" /> All contacts <b>{{ contacts.length }}</b></button><button :class="{ active: favoritesOnly }" :aria-pressed="favoritesOnly" @click="favoritesOnly = true"><AppIcon name="star" /> Favorites <b>{{ favoriteCount }}</b></button></nav>
      <p class="nav-label tools-label">DATA TOOLS</p><div class="sidebar-tools"><button :disabled="busy || loading" @click="openImport"><AppIcon name="upload" />Import Excel</button><button :disabled="busy || loading || Boolean(downloading) || Boolean(loadError)" @click="download('export')"><AppIcon name="download" />Export Excel</button></div>
      <div class="project-members"><p class="nav-label">PROJECT TEAM</p><div><span class="member-avatar">CQ</span><span>Cai Qizhen<small>832401301</small></span><b>FE</b></div><div><span class="member-avatar">CQ</span><span>Chen Qizhen<small>832401304</small></span><b>BE</b></div></div>
    </aside>
    <main>
      <div class="workspace-bar"><div><AppIcon name="panel" :size="17" /><span class="bar-separator"></span><span>Workspace</span><AppIcon name="right" :size="13" /><strong>Contacts</strong></div><span class="stage-label" :class="{ offline: loadError }"><i></i>{{ preview ? 'Local preview' : loadError ? 'Connection unavailable' : 'Contact management' }}</span></div>
      <header class="page-header"><div class="hero-copy"><span class="eyebrow"><i></i>YOUR PEOPLE, CONNECTED</span><h1>A place for<br />every connection.</h1><p>Keep the people who matter, beautifully organized.</p></div><div class="hero-visual"><BookIllustration /><div class="header-count"><AppIcon name="users" :size="15" /><strong>{{ String(contacts.length).padStart(2,'0') }}</strong><span>{{ contacts.length === 1 ? 'contact' : 'contacts' }}, one little book</span></div></div></header>
      <section class="overview" aria-label="Directory overview"><div><AppIcon name="users" :size="16" /><span>All contacts</span><strong>{{ String(contacts.length).padStart(2,'0') }}</strong></div><div><AppIcon name="star" :size="16" /><span>Favorites</span><strong>{{ String(favoriteCount).padStart(2,'0') }}</strong></div><div><AppIcon name="book" :size="16" /><span>Multiple methods</span><strong>{{ String(multipleCount).padStart(2,'0') }}</strong></div></section>
      <section class="directory" aria-labelledby="directory-title" :aria-busy="loading || refreshing">
        <div class="directory-toolbar"><div><h2 id="directory-title">{{ favoritesOnly ? 'Favorites' : 'All contacts' }}<span>{{ visible.length }}</span></h2></div><div class="toolbar-actions"><button class="secondary-button" :disabled="busy || loading" @click="openImport"><AppIcon name="upload" :size="15" />Import</button><button class="secondary-button" :disabled="busy || loading || Boolean(downloading) || Boolean(loadError)" @click="download('export')"><AppIcon name="download" :size="15" />{{ downloading === 'export' ? 'Exporting…' : 'Export all' }}</button><button class="primary-button" :disabled="busy || loading || Boolean(loadError)" @click="openForm()"><AppIcon name="plus" :size="16" />New contact</button></div></div>
        <div class="search-toolbar"><label class="search"><AppIcon name="search" :size="16" /><input v-model="search" type="search" placeholder="Search name, phone or email…" aria-label="Search contacts" /></label><span class="results-label">{{ search ? 'Search results' : 'All records' }} · {{ visible.length }}</span><button class="text-button refresh-button" :disabled="busy || loading" @click="load(Boolean(loadError))"><AppIcon name="refresh" :size="15" />{{ refreshing && !loading ? 'Refreshing…' : 'Refresh' }}</button></div>
        <div v-if="refreshError" class="alert warning" role="alert">{{ refreshError }}</div>
        <div v-if="loading" class="state" role="status"><div class="spinner"></div><h3>Loading contacts</h3><p>Retrieving your contact directory.</p></div>
        <div v-else-if="loadError" class="state error" role="alert"><span class="empty-symbol" aria-hidden="true">↻</span><h3>Unable to load contacts</h3><p>{{ loadError }}</p><button class="primary-button" @click="load(true)">Reconnect</button></div>
        <div v-else class="directory-body"><section class="list-pane"><div class="list-caption"><span>Contacts</span><span>Primary contact</span><span>Favorite</span></div><ContactList v-if="visible.length" :contacts="visible" :selected-id="selectedId" :busy="busy" @select="selectedId = $event" @favorite="toggleFavorite" /><div v-else class="state"><span class="empty-symbol" aria-hidden="true"><AppIcon :name="favoritesOnly ? 'star' : 'users'" :size="30" /></span><h3>{{ search ? 'No matching contacts' : favoritesOnly ? 'No favorites yet' : 'Your directory is empty' }}</h3><p>{{ search ? 'Try another keyword or clear your search.' : favoritesOnly ? 'Select a star to keep someone close.' : 'Add your first contact to get started.' }}</p><button v-if="search" class="secondary-button" @click="search = ''">Clear search</button><button v-else-if="!favoritesOnly" class="primary-button" :disabled="busy" @click="openForm()"><AppIcon name="plus" :size="15" />New contact</button></div><div class="list-footer" aria-live="polite"><span>Showing {{ visible.length }} of {{ contacts.length }} {{ contacts.length === 1 ? 'contact' : 'contacts' }}</span><span>Select a contact to view details</span></div></section><ContactDetail :contact="selected" :busy="busy" @edit="openForm" @delete="openDelete" @favorite="toggleFavorite" @copy="copy" /></div>
      </section>
      <div class="page-foot"><span><i></i>{{ preview ? 'Local preview · Fictional sample contacts' : 'YOULIAN / Contact management' }}</span><span>.xlsx import & export</span></div>
    </main>
    <ContactForm v-if="modal === 'form'" :contact="editing" :busy="mutation === 'save'" :error="formError" @save="saveContact" @cancel="modal = ''" />
    <ImportDialog v-if="modal === 'import'" :busy="mutation === 'import'" :downloading="downloading === 'template'" :error="importError" :row-errors="importRows" :result="importResult" @cancel="modal = ''" @import="importContacts" @template="download('template')" @clear-error="importError = ''; importRows = []" />
    <DeleteDialog v-if="modal === 'delete'" :contact="deleting" :busy="mutation === 'delete'" :error="deleteError" @confirm="removeContact" @cancel="modal = ''" />
    <div class="toast-region" aria-live="polite" aria-atomic="true"><div v-if="toast" class="toast" :class="toast.type"><span aria-hidden="true">{{ toast.type === 'error' ? '!' : '✓' }}</span><p>{{ toast.message }}</p><button aria-label="Dismiss notification" @click="toast = null">×</button></div></div>
  </div>
</template>
