# 实际运行截图

全部联系人均为虚构。各阶段使用隔离 SQLite 库，浏览器请求均连接真实后端。

## 云端正式演示

2026 年 11 月 16 日，标准 Chromium 直接访问 http://43.139.206.206/，连接云端 SQLite 与 API。

| 图片 | 内容 |
| --- | --- |
| cloud-desktop.png | 通讯录主页面 |
| cloud-form.png | 新增两电话、邮箱、社交账号和地址 |
| cloud-detail.png | 编辑后联系人详情 |
| cloud-favorites.png | 收藏筛选 |
| cloud-import.png | Excel 导入与模板下载 |
| cloud-import-success.png | 正常文件新增 4 人 |
| cloud-import-error.png | 错误文件行号及字段提示 |
| cloud-mobile.png | 手机宽度列表 |
| cloud-delete.png | 删除二次确认 |
| cloud-modal-mobile.png | 手机新增弹窗 |
| git-history-bcb540b.png | 固定版本真实Git提交历史与作者统计 |
| github-commits-api.png | 直接打开GitHub公开API的提交记录 |
| cloud-server-reboot.png | 整机重启真实结果的整理展示 |
| cloud-health.png | 直接访问公网API健康状态 |

完整视频与打包素材见项目 Release，规格、费用与持久化验证见 [云端验收](../cloud-report.md)。

## 完整项目整合阶段

2026 年 11 月 15 日，以 FastAPI 同端口提供 Vue 生产构建与 /api，完成网页全流程验证，见 [整体验收](../integration-report.md)。

- integrated-desktop.png：整合后的桌面联系人列表。
- integrated-form.png：新增表单中的两条电话、邮箱、社交账号和地址。
- integrated-import-error.png：实际错误工作簿的行号及字段提示。
- integrated-mobile.png：390px 窄屏完整界面。

## 后端初次交付阶段

query-desktop.png 为 1440px 桌面经真实 Vite 代理查询 4 人；query-favorites.png 为收藏筛选显示 2 人；query-mobile.png 为 390px 窄屏；backend-api.png 为实际服务的 Swagger 页面。

该阶段页面保留当时的交接提示，表示当时操作表单尚未实现。保留这些图片作为历史证据，当前完整操作结果以 integrated 图片和整体验收为准。完整演示视频已在后续云端阶段录制。
