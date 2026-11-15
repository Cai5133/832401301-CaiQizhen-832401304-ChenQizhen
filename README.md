# 832401301蔡奇真832401304陈颀桢

软件工程结对编程通讯录项目。蔡奇真（832401301）负责前端；陈颀桢（832401304）负责后端。

[作业要求](https://bbs.csdn.net/topics/620593436) · [课程社区](https://bbs.csdn.net/forums/2601_MU_SE_FZU) · [代码规范](docs/code-style.md)

截止时间：2026 年 11 月 17 日 23:59，北京时间。

## 当前进度

后端已实现联系人增删改查、姓名与方式搜索、收藏持久化、多种及同类型多条方式、Excel 模板与导入导出，并提供自动化测试和正常异常样例。

前端保留现有 Vue 查询界面：列表、详情、搜索和仅看收藏；新增编辑表单、收藏切换和 Excel 界面仍待前端同学完成。后端接口通过不代表整份作业已完成。完整记录见 [后端测试报告](docs/test-report.md) 与 [前端任务](docs/frontend-progress.md)。

## 启动后端

需要 Python 3.12。在 backend 建立虚拟环境后启动：

```bash
cd backend
python -m venv .venv
# macOS / Linux
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Windows 将 `.venv/bin/python` 换为 `.venv\Scripts\python.exe`。首次启动自动创建 SQLite 数据库。健康检查 http://127.0.0.1:8000/api/health ，交互接口文档 http://127.0.0.1:8000/docs 。初始化、虚构演示数据、独立测试库、环境变量及完整命令见 [后端说明](backend/README.md)。

## 启动前端

需要 Node.js 20.19+ 或 22.12+，使用 pnpm 锁文件。在另一个终端：

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

打开 http://127.0.0.1:5173 。`API_PROXY_TARGET` 默认 http://127.0.0.1:8000 ，保留 `/api` 前缀。`VITE_DEMO_MODE` 默认关闭，真实服务失败会明确报错。空库显示空列表；可按后端说明给独立演示库添加虚构联系人。

构建用 `pnpm build`，预览用 `pnpm preview`。部署时需站点反向代理 `/api`；开发代理不进入构建文件。

## 结构和协作

```text
frontend/    蔡奇真的 Vue 前端工程
backend/     陈颀桢的 FastAPI 后端与测试
docs/        契约 规范 分工 测试与博客材料
samples/     真实 xlsx 模板 正常与异常虚构样例
```

使用 main、frontend、backend 分支，个人功能 PR 到 main 后由另一人评审。使用本人 Git 身份，不强推覆盖他人改动。

[接口契约](docs/api.md) · [Excel 格式](samples/README.md) · [后端交接](docs/backend-handoff.md) · [分工](docs/division.md) · [后端博客草稿](docs/backend-blog.md)

## 完整交付待办

前端同学接完所有操作后，双方共同完成网页业务验收、桌面与窄屏检查、截图和完整视频，再发布最终项目版本。后端分支或后端版本仅表示后端交付。

两人分别发布和提交自己的 CSDN 博客。每篇附两人的真实 PSP、提交记录与数量、分工和合计 100% 的贡献比例。草稿中的待填写项必须根据实际情况完成。localhost 和局域网地址不计云部署。

本仓库直接新建；原作业要求 Fork，但原帖未提供明确上游链接。如课程另有指定仓库，应按助教要求接入，不能把当前仓库称为已完成 Fork。
