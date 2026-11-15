# 832401301蔡奇真832401304陈颀桢

软件工程结对编程通讯录项目。蔡奇真（832401301）负责前端；陈颀桢（832401304）负责后端。

[作业要求](https://bbs.csdn.net/topics/620593436) · [课程社区](https://bbs.csdn.net/forums/2601_MU_SE_FZU)

截止时间：2026 年 11 月 17 日 23:59，北京时间。

## 当前版本

这是**前端交付版本**，最新代码在 `frontend` 分支。已完成联系人列表与详情、全部方式内容搜索、动态多方式新增和编辑、收藏与取消、删除确认、Excel 模板下载与导入导出界面、导入行错误展示，以及桌面和窄屏布局。

页面通过集中客户端调用约定的真实 HTTP 接口。已使用本机虚构数据接口检查交互，仍需连接陈颀桢的正式后端验证数据库持久化、导入回滚和最终端到端流程。正式后端尚未开发，完整系统与公网部署待双方联调后交付。

后端未启动时页面明确报错，不自动替换成假数据。VITE_PREVIEW_MODE 仅控制“本地演示”标记，不会替换请求或生成联系人。

## 运行前端

需要 Node.js 20.19+ 或 22.12+，建议当前 LTS；使用 pnpm 锁文件。

```powershell
git clone https://github.com/Cai5133/832401301-CaiQizhen-832401304-ChenQizhen.git
cd 832401301-CaiQizhen-832401304-ChenQizhen
git switch frontend
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

访问 http://127.0.0.1:5173 。未安装 pnpm 时可执行 `npm install --global pnpm`。也能用 `npm install` 和 `npm run dev` 本地运行；团队提交以现有 pnpm 锁文件为准，不混入第二份锁文件。

本机审阅时提供了单独的本地虚构数据服务，不属于正式后端。访问正在运行的 http://127.0.0.1:5173 可体验页面；服务停止后需要重新启动。该演示服务不随前端源码发布，也不替代后端同学的实现。

正式联调时复制 `frontend/.env.example` 为 `frontend/.env.local`，保持 `VITE_PREVIEW_MODE=false`，`API_PROXY_TARGET` 默认为 `http://127.0.0.1:8000`。两台电脑联调时改为后端同学局域网 IP，后端监听 `0.0.0.0:8000`。修改环境配置后重启前端；开发代理保留 `/api` 前缀。

构建：在 frontend 执行 `pnpm build`；预览：`pnpm preview`。dist 不提交。部署时由站点反向代理 `/api`，Vite 开发代理不会进入构建文件。

自动检查：在 frontend 执行 `pnpm test`，当前 15 项测试通过。已在不含 node_modules 的隔离副本中按锁文件重新安装并成功构建。具体检查与限制见 [验证记录](docs/verification.md) 与 [前端验收对照表](docs/frontend-acceptance.md)。

界面采用浅紫、薄荷青、奶油金配色和电话本插画的浅色布局，视觉参考与开源许可见 [界面参考说明](docs/design-references.md)。参考范围仅为界面，通讯录功能、接口与作业要求保持一致。

## 目录与分支

```text
frontend/    蔡奇真的 Vue 前端工程
backend/     陈颀桢的后端工程
docs/        接口 规范 分工 交接与进度
samples/     Excel 格式约定与后续虚构样例
```

只使用 `main`、`frontend`、`backend` 分支。两人使用本人 Git 身份提交，通过 PR 评审合并 main。

后端先读 [接手清单](docs/backend-handoff.md)、[接口契约](docs/api.md) 与 [Excel 格式](samples/README.md)。前端下一步见 [任务进度](docs/frontend-progress.md)。[代码规范](docs/code-style.md) 与 [分工](docs/division.md) 供双方共同遵守。

仓库公开，助教可以直接阅读。队友若需直接推送，由所有者在 Settings → Collaborators 邀请其 GitHub 用户名；也可 Fork 后提交 PR。

## 最终作业

完成后仍需发布版本、发起 PR、上传文档、录制完整视频。两人各自发布个人 CSDN 博客，每篇包含两人的 PSP 表、提交记录与数量、分工、贡献比例和实际问题解决过程，再在原帖底部“提交任务”中各自提交本人博客链接。当前交接不是最终完成。

本仓库按两人决定直接新建。若课程后续明确指定上游仓库，应按助教要求接入指定 Fork，不将新建仓库称为已完成 Fork。
