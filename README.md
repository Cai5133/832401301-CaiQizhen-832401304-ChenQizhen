# 832401301蔡奇真832401304陈颀桢

软件工程结对编程通讯录项目。蔡奇真（832401301）负责前端；陈颀桢（832401304）负责后端。

[作业要求](https://bbs.csdn.net/topics/620593436) · [课程社区](https://bbs.csdn.net/forums/2601_MU_SE_FZU)

截止时间：2026 年 11 月 17 日 23:59，北京时间。

## 当前版本

这是**仓库建立与前后端交接版本**。已准备 Vue 前端骨架、联系人列表与详情、搜索和只看收藏、真实查询 API 调用、只读样例预览、接口客户端及共同开发说明。

尚未完成：新增与编辑表单、收藏状态修改、Excel 上传下载界面、后端服务、持久化和端到端联调。接口客户端已预留请求方法，仍需开发对应界面并验证。

样例模式默认关闭。后端未启动时页面明确报错，不自动替换成假数据。

## 运行前端

需要 Node.js 20.19+ 或 22.12+，建议当前 LTS；使用 pnpm 锁文件。

```powershell
git clone https://github.com/Cai5133/832401301-CaiQizhen-832401304-ChenQizhen.git
cd 832401301-CaiQizhen-832401304-ChenQizhen
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

访问 http://127.0.0.1:5173 。未安装 pnpm 时可执行 `npm install --global pnpm`。也能用 `npm install` 和 `npm run dev` 本地运行；团队提交以现有 pnpm 锁文件为准，不混入第二份锁文件。

后端未完成时：复制 `frontend/.env.example` 为 `frontend/.env.local`，将 `VITE_DEMO_MODE` 改为 `true`，重启前端，查看明确标注的**只读虚构样例**。

联调时将其设回 `false`，`API_PROXY_TARGET` 默认为 `http://127.0.0.1:8000`。两台电脑联调时改为后端同学局域网 IP，后端监听 `0.0.0.0:8000`。开发代理保留 `/api` 前缀。

构建：在 frontend 执行 `pnpm build`；预览：`pnpm preview`。dist 不提交。部署时由站点反向代理 `/api`，Vite 开发代理不会进入构建文件。

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
