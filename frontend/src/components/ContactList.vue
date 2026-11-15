<script setup>
defineProps({ contacts: { type: Array, required: true }, selectedId: [Number, String] })
defineEmits(['select'])
</script>

<template>
  <div class="contact-list" aria-label="联系人列表">
    <button v-for="(contact, index) in contacts" :key="contact.id" class="contact-row"
      :class="{ selected: selectedId === contact.id }" :aria-pressed="selectedId === contact.id"
      @click="$emit('select', contact.id)">
      <span class="avatar" :class="`tone-${index % 3}`">{{ contact.name.slice(-2) }}</span>
      <span class="contact-summary"><strong>{{ contact.name }}</strong><small>{{ contact.methods[0]?.value || '暂无联系方式' }}</small></span>
      <span v-if="contact.isFavorite" class="star" aria-label="已收藏">★</span>
      <span class="chevron" aria-hidden="true">›</span>
    </button>
  </div>
</template>
