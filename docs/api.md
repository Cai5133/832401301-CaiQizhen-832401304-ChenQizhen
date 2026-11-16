# 通讯录接口契约 v1

后端已按本契约实现；前端按本文件接入。开发地址 http://127.0.0.1:8000 ，所有接口以 /api 开头。

## 数据

```json
{
  "id": 1,
  "name": "测试联系人甲",
  "isFavorite": true,
  "methods": [
    { "type": "phone", "label": "手机", "value": "13800000000" },
    { "type": "phone", "label": "备用", "value": "01012345678" },
    { "type": "email", "label": "工作", "value": "demo@example.com" }
  ]
}
```

id 由后端生成整数；name 去首尾空格后 1–100 字；isFavorite 为布尔值；methods 为数组，可为空，同类型可有多条。type 限定 phone、email、social、address；label 是可空字符串；value 是去首尾空格后 1–2000 字的非空字符串；label 最多 100 字。每人最多 100 项方式，未知字段拒绝。isFavorite 只接受 JSON 布尔值。对外 JSON 始终使用这些驼峰字段名。

## 路由

| 方法 | 路径 | 请求 | 成功响应 |
| --- | --- | --- | --- |
| GET | /api/health | 无 | 200 `{"status":"ok"}` |
| GET | /api/contacts | q 可选；favorite=true 可选 | 200 `{"items":[联系人],"total":1}` |
| GET | /api/contacts/{id} | id | 200 联系人 |
| POST | /api/contacts | 联系人去掉 id | 201 完整联系人 |
| PUT | /api/contacts/{id} | 完整 name、isFavorite、methods | 200 完整联系人 |
| DELETE | /api/contacts/{id} | id | 204 无响应体 |
| PATCH | /api/contacts/{id}/favorite | `{"isFavorite":true}` 或 false | 200 完整联系人 |
| GET | /api/contacts/template | 无 | 200 .xlsx 模板 |
| GET | /api/contacts/export | 无 导出全部 | 200 contacts.xlsx |
| POST | /api/contacts/import | multipart/form-data，file 字段 | 200 `{"imported":3,"errors":[]}` |

q 去首尾空格，最多 2000 字，按字面子串匹配姓名或方式内容，支持 Unicode 大小写折叠，不把 SQL 通配符当模式；favorite 不传时查全部。暂不分页，total 等于筛选结果数量。PUT 整体替换方式列表。静态路由 /template、/export 先于 /{id} 注册。

## 错误与文件

普通错误 `{"detail":"联系人不存在"}`。400 文件不可读；404 联系人不存在；413 上传超限；422 字段或 Excel 行错误。前端兼容 FastAPI 默认 detail 数组。

导入失败 422，整批不写入：

```json
{"detail":{"message":"导入失败，未写入数据","errors":[{"row":3,"column":"电话","reason":"需要 JSON 字符串数组"}]}}
```

Excel 响应：Content-Type 为 application/vnd.openxmlformats-officedocument.spreadsheetml.sheet，Content-Disposition 为 attachment; filename="contacts.xlsx"。模板可用 contacts-template.xlsx。不将 JSON 错误按 200 返回给下载按钮。

字段或格式变更先双方确认，同步本文件、代码、模板和测试。

## 导入边界

上传字段 file，仅收 .xlsx，最大 5 MB；ZIP 解压总量最大 50 MB，ZIP 条目最多 1000；每次最多 5000 位联系人，最多扫描 10000 行。全部空白行跳过。仅接受 Contacts 工作表的六列数据；姓名为文本、收藏为 0/1。多值列接受 JSON 数组，元素为字符串，或含必填 value、可选 label 的对象；对象不接受额外字段，长度限制与联系人 API 一致。公式和 Excel 错误值拒绝。

模板含一位虚构示例，导入会将其新增；导出总是导出全部联系人。空导出也有完整表头，可再次导入并返回 imported: 0。Excel v1.1 保留原六列表头和 v1 字符串数组兼容性：有标签的方式导出为 {"label":"工作","value":"00123"}，无标签仍导出为字符串。导入恢复姓名、收藏、方式类型、标签与内容，不把数据库内部 ID 作为业务信息导出。导出若某一聚合单元格超过 Excel 的 32767 字限制，返回 422，不静默截断。

CORS_ORIGINS 可按需指定允许的浏览器来源。使用 Vite 代理时无需 CORS；直连跨域时响应暴露 Content-Disposition。
