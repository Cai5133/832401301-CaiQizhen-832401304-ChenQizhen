# 前后端接入说明

蔡奇真负责前端，陈颀桢负责后端。后端 PR #1 已合并，前端 PR #2 的真实接口联调在此版本完成。两端使用 [接口契约](api.md)，不使用独立虚构接口替代正式联调。

开发时启动后端 8000 和 Vite 5173，保持 VITE_PREVIEW_MODE=false、API_PROXY_TARGET=http://127.0.0.1:8000。生产时构建 frontend/dist，由后端同一端口提供网页与 /api；云端用 Nginx 代理到后端。

联系人请求 name、isFavorite、methods，方式 type 是 phone/email/social/address，同类型允许多条，号码为字符串。PUT 整体替换方式，收藏 PATCH 提交明确布尔值。所有写操作以正式接口响应为准，失败保留输入并展示错误。

Excel 固定 Contacts 和六个中文表头，JSON 字符串数组保存多值。label 不参与 v1 往返；导入新增、允许同名，重复上传会重复新增。任一行错误整批不写入，前端展示行号、列名和原因。

自动化、浏览器实际流程和重启验证见 [整体验收](integration-report.md)。公网部署步骤见 [部署说明](deployment.md)。最终完整视频、两篇个人博客、两人 PSP 与实际贡献比例仍须本人补充和提交。
