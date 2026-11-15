<script setup>
import { initials } from '../utils/contacts'
import AppIcon from './AppIcon.vue'
defineProps({ contacts: { type: Array, required: true }, selectedId: [Number, String], busy: Boolean })
defineEmits(['select', 'favorite'])
</script>

<template>
  <div class="contact-list" aria-label="Contact list">
    <div v-for="(contact, index) in contacts" :key="contact.id" class="contact-row" :class="{ selected: selectedId === contact.id }">
      <button class="contact-select" :aria-pressed="selectedId === contact.id" @click="$emit('select', contact.id)">
      <span class="avatar" :class="`tone-${index % 3}`">{{ initials(contact.name) }}</span>
      <span class="contact-summary"><strong>{{ contact.name }}</strong><small>{{ contact.methods.length }} {{ contact.methods.length === 1 ? 'method' : 'methods' }}</small></span>
      <span class="primary-contact">{{ contact.methods[0]?.value || 'No contact method' }}</span>
      </button>
      <button class="favorite-button" :class="{ starred: contact.isFavorite }" :aria-label="`${contact.isFavorite ? 'Remove favorite: ' : 'Favorite: '}${contact.name}`" :aria-pressed="contact.isFavorite" :title="contact.isFavorite ? 'Remove from favorites' : 'Add to favorites'" :disabled="busy" @click="$emit('favorite', contact)"><AppIcon name="star" :size="17" /></button>
    </div>
  </div>
</template>
