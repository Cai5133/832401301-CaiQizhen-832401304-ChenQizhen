# 给陈颀桢的后端接手清单

蔡奇真负责前端，陈颀桢负责后端。当前前端是交接骨架，后端还没有实现。

## 1 取得代码

```powershell
git clone https://github.com/Cai5133/832401301-CaiQizhen-832401304-ChenQizhen.git
cd 832401301-CaiQizhen-832401304-ChenQizhen
git switch backend
```

设置本人的 Git 作者姓名和可关联本人 GitHub 的邮箱。没有推送权限时，把自己的 GitHub 用户名发给蔡奇真，由所有者添加协作者；或 Fork 后提 PR。

## 2 先打通查询

1. 在 backend 目录实现服务。建议 FastAPI + SQLite + openpyxl，也可用自己熟悉的框架，但接口必须一致。
2. 默认 8000 端口，`GET /api/health` 返回 `{"status":"ok"}`。
3. `GET /api/contacts` 先返回 `{"items":[],"total":0}`，让前端看到空列表。
4. 再加入虚构联系人，确认前端能显示所有联系方式。
5. 把依赖、初始化步骤、启动命令和地址写进 backend/README.md，发送给前端同学。

## 3 做数据和收藏

按 docs/api.md 建联系人和联系方式两张表。一人可以有多种方式，也可以有两部电话。电话号码按字符串保存；收藏要写入数据库，服务重启不丢。新增、编辑、删除和导入用事务，不留下部分数据。实现查询、详情、POST、PUT、DELETE、收藏 PATCH、q 搜索和 favorite 筛选。

## 4 做 Excel

按 samples/README.md 的 Contacts 工作表和中文表头实现模板、导出与导入。一人一行，多值使用 JSON 字符串数组。上传字段为 file，只收 .xlsx，建议上限 5 MB、5000 条。先验证整批，再写入；一行失败整批回滚，返回行号、列名和原因。新增模式允许同名，重复上传会再次新增。

后端负责提供真实模板、正常与异常 Excel 样例。所有数据虚构，不放真实同学联系方式。

## 5 联调与交付

提供：源码、依赖版本、初始化或迁移方式、启动命令、服务地址、Excel 样例和真实测试结果。前端在 .env.local 修改 API_PROXY_TARGET；不要取消 /api 前缀。

共同验收：网页新增联系人 → 两部电话及邮箱 → 编辑 → 收藏及取消 → Excel 导出打开 → 导入空测试库 → 重启后数据还在。再检查错误导入与服务断开提示。

每完成一项真实功能提交一次，推送 backend，发 PR 到 main。不要提交 .venv、密钥、真实联系人或临时数据库。
