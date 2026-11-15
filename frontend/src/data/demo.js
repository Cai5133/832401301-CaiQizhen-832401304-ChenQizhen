// 只读界面样例。默认关闭，不替代后端持久化或真实联调。
export const demoContacts = [
  { id: 1, name: '林小满', isFavorite: true, methods: [
    { type: 'email', label: '工作', value: 'xiaoman@example.com' },
    { type: 'phone', label: '手机', value: '13800000001' },
    { type: 'address', label: '', value: '示例市花园路 12 号' },
  ] },
  { id: 2, name: '周予安', isFavorite: false, methods: [
    { type: 'email', label: '', value: 'yuan@example.com' },
    { type: 'social', label: '微信', value: 'demo_yuan' },
  ] },
  { id: 3, name: '陈知夏', isFavorite: true, methods: [
    { type: 'phone', label: '手机', value: '13800000002' },
    { type: 'phone', label: '备用', value: '01000000001' },
    { type: 'email', label: '', value: 'zhixia@example.com' },
  ] },
]
