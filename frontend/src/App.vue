<script setup>
import { computed, onMounted, ref } from 'vue'
import ContactList from './components/ContactList.vue'
import ContactDetail from './components/ContactDetail.vue'
import { contactsApi } from './api/contacts'
import { demoContacts } from './data/demo'

const demo = import.meta.env.VITE_DEMO_MODE === 'true'
const contacts = ref([])
const selectedId = ref(null)
const search = ref('')
const favoritesOnly = ref(false)
const loading = ref(false)
const error = ref('')
const selected = computed(() => contacts.value.find(item => item.id === selectedId.value) || null)
const visible = computed(() => contacts.value.filter(contact => {
  const term = search.value.trim().toLocaleLowerCase()
  return (!favoritesOnly.value || contact.isFavorite) && (!term || contact.name.toLocaleLowerCase().includes(term) || contact.methods.some(method => method.value.toLocaleLowerCase().includes(term)))
}))
const favorites = computed(() => contacts.value.filter(item => item.isFavorite).length)

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (demo) contacts.value = structuredClone(demoContacts)
    else {
      const data = await contactsApi.list()
      if (!Array.isArray(data.items)) throw new Error('接口格式不符：缺少 items 数组，请核对接口文档')
      contacts.value = data.items
    }
    selectedId.value = contacts.value[0]?.id ?? null
  } catch (cause) {
    error.value = cause.message
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<template>
  <div class="workspace">
    <aside class="sidebar">
      <a class="brand" href="./"><span class="brand-icon" aria-hidden="true">联</span><span>有联<small>ADDRESS BOOK</small></span></a>
      <p class="nav-label">我的通讯录</p>
      <nav aria-label="联系人分类"><button :class="{ active: !favoritesOnly }" @click="favoritesOnly = false"><span aria-hidden="true">▤</span> 全部联系人 <b>{{ contacts.length }}</b></button><button :class="{ active: favoritesOnly }" @click="favoritesOnly = true"><span aria-hidden="true">☆</span> 收藏联系人 <b>{{ favorites }}</b></button></nav>
      <div class="sidebar-note"><span class="note-mark" aria-hidden="true">↗</span><strong>让每一次联系更简单</strong><p>把重要的人，放在随时能找到的地方。</p></div>
      <footer><span class="team-dot"></span> 蔡奇真 × 陈颀桢<small>软件工程 · 结对编程</small></footer>
    </aside>

    <main>
      <header class="page-header"><div><span class="eyebrow">YOUR PEOPLE, TOGETHER</span><h1>联系，近在眼前<span>。</span></h1><p>收好每一份联系方式，让重要的人保持联结。</p></div><div class="stage-label"><i></i>{{ demo ? '只读样例预览' : '前端交接初版' }}</div></header>
      <div class="stage-notice" role="note">{{ demo ? '当前为只读样例模式，联系人均为虚构数据。关闭样例模式后连接真实后端。' : '当前为工程骨架：已接入联系人查询契约。新增、编辑、收藏切换与 Excel 界面将在下一阶段完成。' }}</div>
      <section class="directory" aria-labelledby="directory-title">
        <div class="directory-toolbar"><div><h2 id="directory-title">{{ favoritesOnly ? '收藏联系人' : '全部联系人' }}<span>{{ visible.length }}</span></h2><p>{{ favoritesOnly ? '那些值得经常联系的人' : '每一位联系人，都有自己的位置' }}</p></div><label class="search"><span aria-hidden="true">⌕</span><input v-model="search" type="search" placeholder="搜索姓名、电话或邮箱" aria-label="搜索联系人" /></label></div>
        <div v-if="loading" class="state" role="status">正在读取联系人…</div>
        <div v-else-if="error" class="state error" role="alert"><h3>暂时无法读取联系人</h3><p>{{ error }}</p><p>请启动后端服务后重试，或参考 README 开启只读样例预览。</p><button class="primary-button" @click="load">重新加载</button></div>
        <div v-else class="directory-body"><section class="list-pane"><div class="list-caption"><span>姓名与主要联系方式</span><span>收藏</span></div><ContactList v-if="visible.length" :contacts="visible" :selected-id="selectedId" @select="selectedId = $event" /><div v-else class="state"><h3>{{ search ? '没有找到相关联系人' : '这里还没有联系人' }}</h3><p>{{ search ? '试试其他姓名或联系方式。' : '后端接入后，联系人会显示在这里。' }}</p></div><div class="list-footer">共 {{ visible.length }} 位联系人 <span>所有联系方式集中管理</span></div></section><ContactDetail :contact="selected" /></div>
      </section>
      <div class="page-foot"><span>有联通讯录</span><span>832401301 蔡奇真 · 832401304 陈颀桢</span></div>
    </main>
  </div>
</template>
