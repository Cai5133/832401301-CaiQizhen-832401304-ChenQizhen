<script setup>
import { ref } from 'vue'
import BaseDialog from './BaseDialog.vue'
import { validateUpload } from '../utils/contacts'
import { displayColumn, displayMessage } from '../utils/messages'
const props = defineProps({ busy: Boolean, downloading: Boolean, error: String, rowErrors: { type: Array, default: () => [] }, result: { type: Object, default: null } })
const emit = defineEmits(['cancel', 'import', 'template', 'clear-error'])
const file = ref(null)
const fileError = ref('')
const dragging = ref(false)
const input = ref(null)
function choose(candidate) {
  file.value = candidate || null
  fileError.value = candidate ? validateUpload(candidate) : ''
  emit('clear-error')
}
function drop(event) {
  dragging.value = false
  if (!props.busy && !props.result) choose(event.dataTransfer.files[0])
}
function submit() {
  if (props.busy || props.result) return
  fileError.value = validateUpload(file.value)
  if (!fileError.value) emit('import', file.value)
}
</script>

<template>
  <BaseDialog title="Import contacts" description="Bring your contacts into one place with an Excel workbook." :busy="busy || downloading" @cancel="$emit('cancel')">
    <div class="modal-body">
      <div v-if="result" class="import-success" role="status"><span>✓</span><h3>Imported {{ result.imported }} {{ result.imported === 1 ? 'contact' : 'contacts' }}</h3><p>{{ result.synced ? 'Your directory is up to date. Close this window to view your contacts.' : 'Import complete. Close this window and refresh the list.' }}</p></div>
      <template v-else>
        <div class="template-guide"><span class="file-icon" aria-hidden="true">X</span><div><strong>Start with the template</strong><p>Keep the template headers unchanged.</p></div><button class="text-button" :disabled="downloading || busy" @click="$emit('template')">{{ downloading ? 'Downloading…' : 'Download ↓' }}</button></div>
        <input ref="input" type="file" class="sr-only" accept=".xlsx" aria-label="Choose an Excel file" :disabled="busy" @change="choose($event.target.files[0]); $event.target.value = ''" />
        <button type="button" class="upload-zone" :class="{ dragging, invalid: fileError }" :disabled="busy" @click="input.click()" @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="drop"><span class="upload-symbol" aria-hidden="true">↥</span><strong>{{ file ? file.name : 'Choose a file or drop it here' }}</strong><small>{{ file ? `${(file.size / 1024).toFixed(1)} KB · Click to replace` : '.xlsx only · Up to 5 MB' }}</small></button>
        <p v-if="fileError" class="field-error" role="alert">{{ fileError }}</p>
        <div class="import-notes"><h3>Before you import</h3><ul><li>Use the Contacts worksheet, with one contact per row.</li><li>Keep all six original template headers and their order. They represent name, favorite, phone, email, social and address.</li><li>Use 1 or 0 for favorites. Store method values as JSON arrays, for example ["+1 202 555 0100"]. Use [] for an empty method.</li><li>Each import adds new contacts. Import a file only once to avoid duplicates.</li><li>If any row is invalid, no rows are saved. Fix the reported errors and try again.</li></ul></div>
      </template>
      <div v-if="error" class="alert danger" role="alert">{{ error }}</div>
      <div v-if="rowErrors.length" class="row-errors"><h3>Rows to review</h3><div class="error-table-wrap"><table><thead><tr><th>Excel row</th><th>Column</th><th>Issue</th></tr></thead><tbody><tr v-for="(item, index) in rowErrors" :key="index"><td>{{ item.row }}</td><td>{{ displayColumn(item.column) }}</td><td>{{ displayMessage(item.reason, 'Invalid cell value. Check this row against the template.') }}</td></tr></tbody></table></div></div>
    </div>
    <footer class="modal-footer"><span v-if="busy" class="footer-hint" role="status">Validating and importing…</span><button class="secondary-button" :disabled="busy || downloading" @click="$emit('cancel')">{{ result ? 'Close' : 'Cancel' }}</button><button v-if="!result" class="primary-button" :disabled="busy || downloading || !file || Boolean(fileError)" @click="submit">{{ busy ? 'Importing…' : 'Import contacts' }}</button></footer>
  </BaseDialog>
</template>
