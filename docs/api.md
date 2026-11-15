# 通讯录接口契约 v1

开发前共同约定，不代表后端已实现。开发地址 http://127.0.0.1:8000 ，所有接口以 /api 开头。

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

id 由后端生成整数；name 去首尾空格后 1–100 字；isFavorite 为布尔值；methods 为数组，可为空，同类型可有多条。type 限定 phone、email、social、address；label 是可空字符串；value 是非空字符串。对外 JSON 始终使用这些驼峰字段名。

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

q 匹配姓名或方式内容；favorite 不传时查全部。暂不分页，total 等于筛选结果数量。PUT 整体替换方式列表。静态路由 /template、/export 先于 /{id} 注册。

## 错误与文件

普通错误 `{"detail":"联系人不存在"}`。400 文件不可读；404 联系人不存在；413 上传超限；422 字段或 Excel 行错误。前端兼容 FastAPI 默认 detail 数组。

导入失败 422，整批不写入：

```json
{"detail":{"message":"导入失败，未写入数据","errors":[{"row":3,"column":"电话","reason":"需要 JSON 字符串数组"}]}}
```

Excel 响应：Content-Type 为 application/vnd.openxmlformats-officedocument.spreadsheetml.sheet，Content-Disposition 为 attachment; filename="contacts.xlsx"。模板可用 contacts-template.xlsx。不将 JSON 错误按 200 返回给下载按钮。

字段或格式变更先双方确认，同步本文件、代码、模板和测试。
