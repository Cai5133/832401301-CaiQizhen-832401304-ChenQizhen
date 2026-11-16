# 832401301蔡奇真832401304陈颀桢

软件工程结对编程通讯录。蔡奇真（832401301）负责 Vue 前端；陈颀桢（832401304）负责 FastAPI、SQLite 和 Excel 后端。

[作业要求](https://bbs.csdn.net/topics/620593436) · [课程社区](https://bbs.csdn.net/forums/2601_MU_SE_FZU) · [代码规范](docs/code-style.md) · [分工](docs/division.md)

截止时间：2026 年 11 月 17 日 23:59，北京时间。

## 功能

联系人新增、编辑、详情与删除；一人多种及同类型多条联系方式；收藏和快速筛选；按姓名或任意方式内容搜索；真正 .xlsx 模板下载、导入、导出与错误行提示。收藏和联系方式写入 SQLite，进程重启后保留。导入先校验整批，任何一行失败均不写入。

前后端都调用真实接口，不在请求失败时替换为虚构数据。VITE_PREVIEW_MODE 仅控制界面标记，不替换请求。界面视觉参考与许可见 [设计参考](docs/design-references.md)。

## 开发运行

Python 3.12、Node.js 20.19+ 或 22.12+，使用现有 pnpm 锁文件。

```bash
cd backend
python -m venv .venv
# macOS / Linux
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Windows 把 `.venv/bin/python` 换为 `.venv\Scripts\python.exe`。首次启动自动创建固定位置的数据库，详见 [后端说明](backend/README.md)。健康检查 http://127.0.0.1:8000/api/health ，接口文档 http://127.0.0.1:8000/docs 。

另开终端运行前端：

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

打开 http://127.0.0.1:5173 。API_PROXY_TARGET 默认 http://127.0.0.1:8000，保留 /api。VITE_PREVIEW_MODE 保持 false，空数据库会显示空列表。初始化、独立演示库和虚构数据见后端说明。

## 生产运行与云部署

先在 frontend 执行 `pnpm build`，后端会同时提供构建后的网页和 /api。单个地址即可访问完整系统，不需要启动 Vite 开发服务。

已部署到腾讯云 Ubuntu 24.04：[在线通讯录](http://43.139.206.206/)。2026 年 11 月 16 日通过公网完整操作、后端服务重启与服务器整机重启验证，见 [云端验收](docs/cloud-report.md)。试用至北京时间 2026 年 12 月 16 日 15:19，手动续费、未开启自动续费；到期后可能停机或释放。安装、持久化及备份步骤见 [云部署说明](docs/deployment.md)。

## 验证

```bash
# frontend
pnpm test
pnpm build
# backend，使用虚拟环境中的 python
python -m pip install -r requirements-dev.lock.txt
python -m pytest -q
python scripts/smoke_http.py
```

[后端报告](docs/test-report.md) · [前端验收](docs/frontend-acceptance.md) · [整体验收](docs/integration-report.md) · [接口契约](docs/api.md) · [Excel 格式和样例](samples/README.md)

## 目录与交付

frontend 为页面、backend 为后端与测试、samples 为虚构 Excel 样例、deploy 为生产部署配置、docs 为规范及证据。使用 main、frontend、backend 分支，保留个人真实提交历史，不强推覆盖他人改动。

后端 PR #1、前端及整合 PR #2 均已合并到 main，保留双方提交历史。公网部署、完整演示视频和关键页面截图已完成，见 [云端验收](docs/cloud-report.md)。两人的个人博客与实际 PSP、贡献比例和课程提交记录需本人按真实情况补齐。博客技术草稿见 [backend-blog.md](docs/backend-blog.md)。

原帖要求 Fork，但未附明确课程上游地址；如有另行指定仓库，应按助教要求接入。项目在创建时为独立团队仓库，不声称已经 Fork 了未确认的课程上游。
