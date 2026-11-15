<script setup>
defineProps({ contact: { type: Object, default: null } })
const labels = { phone: '电话', email: '邮箱', social: '社交账号', address: '地址' }
</script>

<template>
  <section class="detail" aria-label="联系人详情">
    <template v-if="contact">
      <div class="detail-top"><span class="eyebrow">联系人详情</span><span v-if="contact.isFavorite" class="badge">★ 常用联系人</span></div>
      <div class="profile"><div class="profile-avatar">{{ contact.name.slice(-2) }}</div><h2>{{ contact.name }}</h2><p>{{ contact.methods.length }} 项联系方式</p></div>
      <div class="detail-divider"></div>
      <dl class="methods"><div v-for="(method, index) in contact.methods" :key="index"><dt>{{ labels[method.type] || method.type }}<span v-if="method.label"> · {{ method.label }}</span></dt><dd>{{ method.value }}</dd></div></dl>
      <p v-if="!contact.methods.length" class="muted">还没有填写联系方式</p>
    </template>
    <div v-else class="detail-placeholder"><span aria-hidden="true">◎</span><h2>从一次联系开始</h2><p>选择左侧联系人，查看详细信息。</p></div>
  </section>
</template>
