// Preserve API payloads; localize only text rendered in the interface.
const messages = {
  '请求内容不正确': 'The request contains invalid data.',
  '服务暂时不可用，请稍后重试': 'The service is temporarily unavailable. Please try again later.',
  '请填写姓名': 'Enter a contact name.',
  '接口不存在': 'This API endpoint is unavailable.',
  '联系人不存在': 'This contact no longer exists. Refresh the list.',
  '收藏值必须为布尔值': 'The favorite value must be true or false.',
  '方法不支持': 'This action is not supported.',
  '文件超过 5 MB': 'Choose a file no larger than 5 MB.',
  '缺少 file 文件字段': 'No workbook was attached. Choose a file and try again.',
  '无法读取 Excel 文件，请检查文件是否损坏': 'The workbook could not be read. Check that it is a valid .xlsx file.',
  '缺少 Contacts 工作表': 'The workbook must contain a worksheet named Contacts.',
  '表头与模板不一致，请使用标准模板': 'The column headers do not match. Use the downloaded template unchanged.',
  '只能填 1 或 0': 'Use 1 or 0.',
  '最多导入 5000 条': 'Import no more than 5,000 contacts at a time.',
  '导入失败，未写入数据': 'Import failed. No contacts were saved.',
  '未写入数据': 'No data was saved.',
  '格式错误': 'Invalid format.',
}

export function displayMessage(value, fallback = 'The request could not be completed. Check your input and try again.') {
  if (typeof value !== 'string' || !value.trim()) return fallback
  if (messages[value]) return messages[value]
  if (value.startsWith('需要 JSON 字符串数组')) return 'Use a JSON array of strings, such as ["+1 202 555 0100"].'
  return /\p{Script=Han}/u.test(value) ? fallback : value
}

export function displayColumn(column) {
  return ({ '姓名': 'Name', '收藏': 'Favorite', '电话': 'Phone', '邮箱': 'Email', '社交账号': 'Social', '地址': 'Address' })[column] || displayMessage(column, 'Cell')
}
