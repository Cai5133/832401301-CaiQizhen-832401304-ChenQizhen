<script setup>
import { initials } from '../utils/contacts'
import AppIcon from './AppIcon.vue'
defineProps({ contact: { type: Object, default: null }, busy: Boolean })
defineEmits(['edit', 'delete', 'favorite', 'copy'])
const labels = { phone: 'Phone', email: 'Email', social: 'Social', address: 'Address' }
</script>

<template>
  <section class="detail" aria-label="Contact details">
    <template v-if="contact">
      <div class="detail-top"><span class="eyebrow">Contact details</span><span class="contact-id">#{{ String(contact.id).padStart(3,'0') }}</span></div>
      <div class="profile"><div class="profile-avatar">{{ initials(contact.name) }}</div><h2>{{ contact.name }}</h2><p><span class="badge" v-if="contact.isFavorite"><AppIcon name="star" :size="11" />Favorited</span><span>{{ contact.methods.length }} {{ contact.methods.length === 1 ? 'method' : 'methods' }}</span></p></div>
      <div class="detail-divider"></div>
      <div class="detail-actions"><button class="secondary-button" :disabled="busy" @click="$emit('edit', contact)"><AppIcon name="edit" :size="14" />Edit</button><button class="secondary-button" :disabled="busy" :aria-pressed="contact.isFavorite" @click="$emit('favorite', contact)"><AppIcon name="star" :size="14" />{{ contact.isFavorite ? 'Favorited' : 'Favorite' }}</button><button class="text-button danger-text" :disabled="busy" @click="$emit('delete', contact)"><AppIcon name="trash" :size="14" />Delete</button></div>
      <div class="detail-section-title">Contact methods <span>{{ contact.methods.length }}</span></div>
      <dl class="methods"><div v-for="(method, index) in contact.methods" :key="index"><dt><AppIcon :name="method.type === 'email' ? 'mail' : method.type" :size="14" />{{ labels[method.type] || method.type }}<span v-if="method.label"> / {{ method.label }}</span></dt><dd><span>{{ method.value }}</span><button class="copy-button" :aria-label="`Copy ${labels[method.type] || 'contact methods'} ${method.value}`" title="Copy value" @click="$emit('copy', method.value)"><AppIcon name="copy" :size="13" /></button></dd></div></dl>
      <p v-if="!contact.methods.length" class="muted">No contact methods added yet.</p>
    </template>
    <div v-else class="detail-placeholder"><AppIcon name="book" :size="32" /><h2>No contact selected</h2><p>Select a record to see the details.</p></div>
  </section>
</template>
