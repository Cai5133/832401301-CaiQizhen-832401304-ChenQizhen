# 通讯录后端

Python FastAPI + SQLite + openpyxl。提供联系人增删改查、搜索与收藏、真正的 Excel 模板和导入导出。负责人：832401304 陈颀桢。

## 安装与启动

使用 Python 3.12。在仓库根目录执行：

```bash
cd backend
python -m venv .venv
```

macOS / Linux：

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m app init
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Windows PowerShell：

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m app init
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

启动时也会自动建表，不需要手工执行 SQL。健康检查：http://127.0.0.1:8000/api/health ；Swagger：http://127.0.0.1:8000/docs 。开发时可加 `--reload`。两台电脑联调可用 `--host 0.0.0.0`，前端的 API_PROXY_TARGET 设为后端局域网地址。

前端在另一个终端执行 `cd frontend`、`pnpm install --frozen-lockfile`、`pnpm dev`，访问 http://127.0.0.1:5173 。保留 `/api` 代理前缀，并关闭 VITE_DEMO_MODE。

## 数据库与演示数据

默认数据库固定为 `backend/data/contacts.sqlite3`，与启动工作目录无关。每次连接都启用外键，删除联系人会级联删除方式。新增、编辑、导入都在事务中执行。

通过环境变量 ADDRESS_BOOK_DB 改路径；相对路径以 backend 为基准。`.env.example` 只是变量示例，不会自动加载。测试必须使用独立路径，不能把正式演示库当测试库。

```bash
# macOS / Linux：创建一个独立演示库并写入虚构数据
ADDRESS_BOOK_DB=data/demo.sqlite3 .venv/bin/python -m app seed
ADDRESS_BOOK_DB=data/demo.sqlite3 .venv/bin/python -m uvicorn app.main:app --port 8000
```

```powershell
# Windows PowerShell
$env:ADDRESS_BOOK_DB = "data/demo.sqlite3"
.venv\Scripts\python.exe -m app seed
.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

seed 仅在空数据库中插入一位虚构联系人，非空时拒绝执行。需要重新测试时使用新的数据库文件名。数据文件和虚拟环境不会提交到 Git。

## 接口与 Excel

完整字段与状态码见 [接口契约](../docs/api.md)。一名联系人可有多种方式、同类型多条；号码按字符串处理。收藏 PATCH 使用明确布尔状态，重复请求保持同一结果。

[Excel 格式及样例](../samples/README.md)：Contacts 工作表，六个中文表头，一人一行。多值使用 JSON 字符串数组，label 不参与 Excel v1 往返。导入新增、允许同名，重复上传会再次新增。任一行错误整批不写入，并返回 Excel 行号、列名和原因。

限制：上传 5 MB，ZIP 解压后 50 MB，每次 5000 位联系人，最多扫描 10000 行，每人 100 项方式。姓名 1–100 字，方式 value 1–2000 字、label 最多 100 字。导出遇到超过 Excel 单元格 32767 字的聚合字段会返回 422，不截断内容。禁止公式输入，导出以等号开头的姓名也写为文本。

开发推荐使用 Vite 代理，无需跨域设置。浏览器直连时可设置 `CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173`，只放行指定来源，并暴露下载文件名响应头。

## 测试和复现

```bash
# macOS / Linux，在 backend 内
.venv/bin/python -m pip install -r requirements-dev.lock.txt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/smoke_http.py
.venv/bin/python scripts/generate_samples.py
```

Windows 把 `.venv/bin/python` 换成 `.venv\Scripts\python.exe`。常规开发可安装 requirements-dev.txt；requirements-dev.lock.txt 记录本次验证的完整依赖版本。pytest 使用临时 SQLite；smoke_http.py 启动真实 HTTP 服务、重启进程并检查数据持久化，结束后清理隔离数据库。

[真实验证记录](../docs/test-report.md) 与 [前端交接清单](../docs/backend-handoff.md) 记录覆盖范围。前端新增编辑、收藏切换和 Excel 操作界面仍由前端同学完成。
