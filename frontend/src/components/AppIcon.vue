<script setup>
import { BookUser, Users, Star, Search, Plus, Upload, Download, RefreshCw, ChevronRight, ChevronDown, Mail, Phone, MapPin, AtSign, Copy, Pencil, Trash2, X, Check, PanelLeft, FileSpreadsheet, Database } from '@lucide/vue'
defineProps({ name: String, size: { type: Number, default: 18 } })
const icons = { book: BookUser, users: Users, star: Star, search: Search, plus: Plus, upload: Upload, download: Download, refresh: RefreshCw, right: ChevronRight, down: ChevronDown, mail: Mail, phone: Phone, address: MapPin, social: AtSign, copy: Copy, edit: Pencil, trash: Trash2, close: X, check: Check, panel: PanelLeft, excel: FileSpreadsheet, database: Database }
</script>
<template><component :is="icons[name] || icons.book" :size="size" :stroke-width="1.65" class="app-icon" aria-hidden="true" /></template>
