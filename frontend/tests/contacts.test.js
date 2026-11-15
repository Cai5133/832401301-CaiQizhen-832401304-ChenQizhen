import test from 'node:test'
import assert from 'node:assert/strict'
import { validateContact, filterContacts, validateUpload, checkContact } from '../src/utils/contacts.js'
import { contactsApi, request } from '../src/api/contacts.js'

const phone = value => ({ type: 'phone', label: '', value })
const person = { id: 1, name: '测试联系人', isFavorite: true, methods: [phone('01000123456')] }

test('保留同类多条方式、前导零与特殊符号，并去除首尾空格', () => {
  const result = validateContact({ name: ' 测试甲 ', isFavorite: false, methods: [phone(' 01000123456 '), phone('+353 1 234 5678')] })
  assert.deepEqual(result.errors, {})
  assert.equal(result.payload.name, '测试甲')
  assert.deepEqual(result.payload.methods.map(item => item.value), ['01000123456', '+353 1 234 5678'])
})
test('空姓名和有备注却没有内容的行被拒绝', () => {
  const result = validateContact({ name: '  ', methods: [{ type: 'phone', label: '备用', value: '' }] })
  assert.ok(result.errors.name); assert.ok(result.errors[0])
})
test('未填写的新空行被忽略，可保存没有方式的联系人', () => {
  const result = validateContact({ name: '甲', methods: [phone('')] })
  assert.deepEqual(result.errors, {}); assert.deepEqual(result.payload.methods, [])
})
test('错误邮箱、过长姓名和不支持的方式类型被拒绝', () => {
  const result = validateContact({ name: '长'.repeat(101), methods: [{ type: 'email', label: '', value: 'bad@' }, { type: 'other', label: '', value: '123' }] })
  assert.ok(result.errors.name); assert.ok(result.errors[0]); assert.ok(result.errors[1])
})
test('搜索覆盖所有方式，收藏过滤不把非收藏混入', () => {
  const people = [person, { id: 2, name: '乙', isFavorite: false, methods: [{ type: 'email', label: '', value: 'Other@Example.com' }] }]
  assert.equal(filterContacts(people, '00123456', true).length, 1)
  assert.equal(filterContacts(people, 'other@example', false)[0].id, 2)
  assert.equal(filterContacts(people, 'other@example', true).length, 0)
})
test('拒绝空文件、错误扩展名和超过大小限制的工作簿', () => {
  assert.ok(validateUpload(null)); assert.ok(validateUpload({ name: 'test.csv', size: 100 }))
  assert.ok(validateUpload({ name: 'test.xlsx', size: 0 }))
  assert.ok(validateUpload({ name: 'test.xlsx', size: 5 * 1024 * 1024 + 1 }))
  assert.equal(validateUpload({ name: 'TEST.XLSX', size: 100 }), '')
})
test('接口边界拒绝格式错误的布尔值和联系方式', () => {
  assert.throws(() => checkContact({ ...person, isFavorite: 1 }))
  assert.throws(() => checkContact({ ...person, methods: [{ type: 'phone', value: 13800000000 }] }))
  assert.equal(checkContact({ ...person, methods: [{ type: 'phone', value: '000' }] }).methods[0].label, '')
})
test('204 删除响应没有 JSON，不产生解析错误', async t => {
  t.mock.method(globalThis, 'fetch', async () => new Response(null, { status: 204 }))
  assert.equal(await contactsApi.remove(1), null)
})
test('Excel 行错误保留状态码、行号和原因', async t => {
  t.mock.method(globalThis, 'fetch', async () => new Response(JSON.stringify({ detail: { message: '未写入数据', errors: [{ row: 3, column: '电话', reason: '格式错误' }] } }), { status: 422 }))
  await assert.rejects(() => request('/contacts/import'), error => error.status === 422 && error.rows[0].row === 3 && error.message === 'No data was saved.')
})
test('新增使用约定的 JSON 字段，不改变多项方式数组', async t => {
  let sent
  t.mock.method(globalThis, 'fetch', async (url, options) => { sent = { url, options }; return Response.json(person, { status: 201 }) })
  const draft = { name: '甲', isFavorite: true, methods: [phone('001'), phone('002')] }
  await contactsApi.create(draft)
  assert.equal(sent.url, '/api/contacts'); assert.equal(sent.options.method, 'POST')
  assert.deepEqual(JSON.parse(sent.options.body), draft)
})
test('上传使用 file 字段，不手写 multipart Content-Type', async t => {
  let sent
  t.mock.method(globalThis, 'fetch', async (url, options) => { sent = options; return Response.json({ imported: 1, errors: [] }) })
  await contactsApi.import(new File(['test'], 'test.xlsx'))
  assert.equal(sent.body.get('file').name, 'test.xlsx')
  assert.equal(sent.headers, undefined)
})
test('请求失败不自动重试或声称保存成功', async t => {
  let count = 0
  t.mock.method(globalThis, 'fetch', async () => { count++; throw new TypeError('network') })
  await assert.rejects(() => contactsApi.create({}), /Refresh the list before submitting again/)
  assert.equal(count, 1)
})
test('JSON 或 HTML 伪装成成功的下载不会保存成 Excel', async t => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ detail: '错误文件' }))
  await assert.rejects(() => contactsApi.download(), /valid Excel/)
})
test('导入响应损坏时提醒核对结果，不自动重复提交', async t => {
  t.mock.method(globalThis, 'fetch', async () => new Response('not json', { status: 200 }))
  await assert.rejects(() => contactsApi.import(new File(['test'], 'test.xlsx')), /Refresh the list before importing again/)
})

test('English UI localizes server errors while preserving row metadata', async t => {
  t.mock.method(globalThis, 'fetch', async () => Response.json({ detail: { message: '导入失败，未写入数据', errors: [{ row: 4, column: '电话', reason: '格式错误' }] } }, { status: 422 }))
  await assert.rejects(() => request('/contacts/import'), error => error.message === 'Import failed. No contacts were saved.' && error.rows[0].column === '电话' && error.rows[0].row === 4)
})
