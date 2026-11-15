<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import BaseDialog from './BaseDialog.vue'
import { methodTypes, validateContact } from '../utils/contacts'

const props = defineProps({ contact: { type: Object, default: null }, busy: Boolean, error: String })
const emit = defineEmits(['save', 'cancel'])
let sequence = 0
const row = (item = {}) => ({ key: ++sequence, type: 'phone', label: '', value: '', ...item })
const draft = reactive({ name: props.contact?.name || '', isFavorite: props.contact?.isFavorite || false,
  methods: props.contact?.methods?.length ? props.contact.methods.map(item => row(item)) : [row()] })
const initial = JSON.stringify(draft)
const dirty = computed(() => JSON.stringify(draft) !== initial)
const methodCount = computed(() => draft.methods.filter(item => item.value.trim()).length)
const errors = ref({})
const form = ref(null)
const discard = ref(false)

async function save() {
  if (props.busy) return
  const result = validateContact(draft)
  errors.value = result.errors
  if (Object.keys(errors.value).length) {
    await nextTick()
    form.value.querySelector('[aria-invalid="true"]')?.focus()
    return
  }
  discard.value = false
  emit('save', result.payload)
}
function cancel() {
  if (props.busy) return
  if (dirty.value) discard.value = true
  else emit('cancel')
}
async function add() {
  draft.methods.push(row())
  await nextTick()
  form.value.querySelector('.method-editor:last-child .method-value')?.focus()
}
</script>

<template>
  <BaseDialog :title="contact ? 'Edit contact' : 'New contact'" description="Add the details that matter. Use multiple entries for any method." :busy="busy" wide @cancel="cancel">
    <form ref="form" novalidate @submit.prevent="save">
      <div class="modal-body">
        <div v-if="error" class="alert danger" role="alert">{{ error }}</div>
        <label class="field"><span>Full name <b class="required">*</b></span><input v-model="draft.name" name="name" placeholder="e.g. Alex Morgan" autocomplete="name" autofocus maxlength="101" :disabled="busy" :aria-invalid="Boolean(errors.name)" :aria-describedby="errors.name ? 'name-error' : undefined" /><small v-if="errors.name" id="name-error" class="field-error">{{ errors.name }}</small></label>
        <label class="favorite-check"><input v-model="draft.isFavorite" type="checkbox" :disabled="busy" /><span>★ Add to favorites</span><small>Keep this contact close</small></label>
        <div class="section-heading"><div><h3>Contact methods</h3><p>Add multiple entries per type. Empty rows are skipped.</p></div><button class="text-button" type="button" :disabled="busy" @click="add">+ Add method</button></div>
        <div v-if="!draft.methods.length" class="empty-methods">No methods yet. Save the name now and add details later.</div>
        <div v-for="(method, index) in draft.methods" :key="method.key" class="method-editor">
          <div class="method-editor-head"><label class="field type-field"><span>Type</span><select v-model="method.type" :aria-label="`Method ${index + 1} type`" :disabled="busy"><option v-for="type in methodTypes" :key="type.value" :value="type.value">{{ type.label }}</option></select></label><label class="field label-field"><span>Label <small>optional</small></span><input v-model="method.label" :aria-label="`Method ${index + 1} label`" placeholder="e.g. Work, Personal" maxlength="51" :disabled="busy" /></label><button type="button" class="icon-button remove-method" :aria-label="`Remove method ${index + 1}`" :disabled="busy" @click="draft.methods.splice(index, 1); errors = {}">×</button></div>
          <label class="field"><span class="sr-only">Method {{ index + 1 }} value</span><textarea v-if="method.type === 'address'" v-model="method.value" class="method-value" :aria-label="`Method ${index + 1} value`" placeholder="Enter a full address" rows="2" maxlength="1001" :disabled="busy" :aria-invalid="Boolean(errors[index])" :aria-describedby="errors[index] ? `method-error-${index}` : undefined"></textarea><input v-else v-model="method.value" class="method-value" :aria-label="`Method ${index + 1} value`" :inputmode="method.type === 'phone' ? 'tel' : method.type === 'email' ? 'email' : 'text'" :placeholder="method.type === 'phone' ? 'Phone number, country code or extension' : method.type === 'email' ? 'name@example.com' : 'Enter a social handle'" maxlength="1001" :disabled="busy" :aria-invalid="Boolean(errors[index])" :aria-describedby="errors[index] ? `method-error-${index}` : undefined" /><small v-if="errors[index]" :id="`method-error-${index}`" class="field-error">{{ errors[index] }}</small></label>
        </div>
      </div>
      <div v-if="discard" class="discard-prompt" role="alert"><span>You have unsaved changes. Discard them?</span><div><button type="button" class="secondary-button" @click="discard = false">Keep editing</button><button type="button" class="danger-button" @click="$emit('cancel')">Discard changes</button></div></div>
      <footer class="modal-footer"><span class="footer-hint">{{ methodCount }} {{ methodCount === 1 ? 'method' : 'methods' }}</span><button type="button" class="secondary-button" :disabled="busy" @click="cancel">Cancel</button><button type="submit" class="primary-button" :disabled="busy">{{ busy ? 'Saving…' : 'Save contact' }}</button></footer>
    </form>
  </BaseDialog>
</template>
