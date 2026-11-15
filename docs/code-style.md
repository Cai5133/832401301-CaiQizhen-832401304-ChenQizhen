# 代码规范

- Vue 组件 PascalCase，例如 ContactList.vue；JS 函数和变量 camelCase；常量 UPPER_SNAKE_CASE。
- JS、Vue、CSS 缩进 2 空格，JS 优先单引号；JSON 双引号。
- Python 缩进 4 空格、snake_case；对外 JSON 严格使用接口契约字段名。
- 注释解释业务选择和边界，不重复代码；不保留调试日志。
- 请求集中 frontend/src/api/contacts.js，组件不散落后端 IP；组件通过 props/emit 通信。
- 后端做最终校验和持久化。用户输入按文本显示，不当 HTML 执行。
- 不提交 node_modules、dist、.venv、环境密钥、真实联系人和临时数据库。
- 分支只使用 main、frontend、backend；个人功能提交 PR 到 main，另一人评审。
- 提交示例：feat(frontend): add contact form、feat(backend): persist favorites、docs: update API contract。
- 使用本人身份提交；合并冲突双方确认，不直接覆盖对方文件。
- 接口失败明确提示，不伪装成功。样例模式默认关闭，不替代真实测试。
- 测试写清步骤、预期、实际与版本，贡献比例和 PSP 如实填写。
