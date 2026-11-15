# 实际运行截图

全部联系人均为虚构。各阶段使用隔离 SQLite 库，浏览器请求均连接真实后端。

## 完整项目整合阶段

2026 年 11 月 15 日，以 FastAPI 同端口提供 Vue 生产构建与 /api，完成网页全流程验证，见 [整体验收](../integration-report.md)。

- integrated-desktop.png：整合后的桌面联系人列表。
- integrated-form.png：新增表单中的两条电话、邮箱、社交账号和地址。
- integrated-import-error.png：实际错误工作簿的行号及字段提示。
- integrated-mobile.png：390px 窄屏完整界面。

## 后端初次交付阶段

query-desktop.png 为 1440px 桌面经真实 Vite 代理查询 4 人；query-favorites.png 为收藏筛选显示 2 人；query-mobile.png 为 390px 窄屏；backend-api.png 为实际服务的 Swagger 页面。

该阶段页面保留当时的交接提示，表示当时操作表单尚未实现。保留这些图片作为历史证据，当前完整操作结果以 integrated 图片和整体验收为准。完整演示视频仍需录制。
