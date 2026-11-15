<script setup>
import BaseDialog from './BaseDialog.vue'
defineProps({ contact: Object, busy: Boolean, error: String })
defineEmits(['cancel', 'confirm'])
</script>
<template>
  <BaseDialog title="Delete contact" description="Review this action before continuing." :busy="busy" @cancel="$emit('cancel')"><div class="modal-body"><p class="delete-message">Delete <strong>{{ contact.name }}</strong>?</p><p class="muted">All contact methods and the favorite status will be removed. This action cannot be undone here.</p><div v-if="error" class="alert danger" role="alert">{{ error }}</div></div><footer class="modal-footer"><button autofocus class="secondary-button" :disabled="busy" @click="$emit('cancel')">Keep contact</button><button class="danger-button" :disabled="busy" @click="$emit('confirm')">{{ busy ? 'Deleting…' : 'Delete contact' }}</button></footer></BaseDialog>
</template>
