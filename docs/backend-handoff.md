# 后端交付与前端接入

后端负责人：832401304 陈颀桢。已按 [接口契约](api.md) 实现全部十个接口。启动命令、数据库与测试见 [后端 README](../backend/README.md)。

## 前端同学接入顺序

1. 拉取 backend 分支或在 PR 评审后合入 main，运行后端健康检查和 `/docs`。
2. 前端保持 `VITE_DEMO_MODE=false`，代理目标 http://127.0.0.1:8000，不移除 `/api`。
3. 用现有 contactsApi.create/update 接新增编辑表单，一人可动态增加同类型方式。提交前删除未填写的方式行。
4. 用 contactsApi.favorite(id, true/false) 接收藏切换；失败时保留原状态，收藏页取消成功后移除条目。
5. 下载模板、导出分别调用 contactsApi.download('template'/'export')。上传调用 contactsApi.import(file)。
6. 导入前提示：只支持 .xlsx、最大 5 MB，新增模式会重复添加；失败时展示 error.rows 中的 row、column、reason。所有行均有效才写入。
7. 保存成功后重新查询列表；验证服务器断开、404、默认 422 数组和 Excel 422 detail 对象的提示。

## 数据规则

name 必填去空格；isFavorite 必须布尔值；methods 可为空。方式 type 为 phone/email/social/address，label 默认空字符串，value 非空字符串，国际号码和前导零原样保留。PUT 整体替换 methods，不是追加。

Excel 固定工作表 Contacts 和六列，见 [样例](../samples/README.md)。label 不导出、导入后为空，方式 value 全部保留。静态路由先注册，不会把 export/template 当作 id。

## 验收状态

后端自动化和真实 HTTP 重启验证结果见 [测试报告](test-report.md)。前端现有查询页面已能对接后端；新增编辑、收藏切换、导入导出等操作仍需完成界面与完整人工验收。

待双方实际操作：网页新增两部电话与邮箱 → 编辑 → 收藏与取消 → 导出并在 Excel 打开 → 导入空库 → 刷新及重启服务 → 错误文件提示。不得将接口测试写成已通过完整网页操作。

后端变更提交到 backend，通过 PR 评审进入 main。最终发布、完整视频、两篇个人博客和 PSP 仍按实际完成情况记录。
