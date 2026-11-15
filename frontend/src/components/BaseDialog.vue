<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import AppIcon from './AppIcon.vue'
const props = defineProps({ title: String, description: String, busy: Boolean, wide: Boolean })
const emit = defineEmits(['cancel'])
const dialog = ref(null)
let previousOverflow
function cancel(event) {
  event?.preventDefault()
  if (!props.busy) emit('cancel')
}
onMounted(() => {
  previousOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  dialog.value.showModal()
})
onBeforeUnmount(() => {
  dialog.value?.close()
  document.body.style.overflow = previousOverflow
})
</script>

<template>
  <dialog ref="dialog" class="modal" :class="{ wide }" aria-labelledby="dialog-title" aria-describedby="dialog-description" @cancel="cancel">
    <header class="modal-header"><div><span class="eyebrow">YOULIAN / DIRECTORY</span><h2 id="dialog-title">{{ title }}</h2><p id="dialog-description">{{ description }}</p></div><button type="button" class="icon-button close" aria-label="Close dialog" :disabled="busy" @click="cancel"><AppIcon name="close" :size="17" /></button></header>
    <slot />
  </dialog>
</template>
