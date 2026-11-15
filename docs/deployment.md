# 腾讯云服务器部署

目标为腾讯云轻量或 CVM 的 Ubuntu 24.04，建议 2 核 2GB 以上和公网 IPv4。整合版本仅运行一个 FastAPI 进程，由它提供前端构建和 /api，Nginx 对外监听 80。数据库固定在 /var/lib/youlian，应用更新及重启不会重新建空库。

## 实例和费用

优先使用账号已具备资格的免费试用，在订单页确认具体规格、试用期限、流量和应付金额。试用不代表永久免费。实例以手动续费为准，试用到期后按用户决定续费或备份下线，流量限制以套餐为准。此文件不宣称公网部署已经完成，实际结果见 [整体验收](integration-report.md)。

## 部署

先在本地 frontend 执行 pnpm install --frozen-lockfile、pnpm test 和 pnpm build，打包 backend/app、backend/requirements.txt、frontend/dist 以及 deploy，上传服务器并解压。

```bash
# 在解压目录执行
sudo bash deploy/install.sh
```

安装器针对新 Ubuntu 24.04 服务器，安装 Python 与 Nginx，创建无登录权限的 youlian 服务账号，将应用版本保存在 /opt/youlian/releases，并通过 current 指向当前版本。仅替换 Nginx 的默认站点。后端依赖通过腾讯云 PyPI 镜像安装。

云控制台防火墙放行 TCP 80；SSH 22 根据维护来源放行。后端仅监听本机 8000，无需将 8000 对外开放。若系统防火墙已启用，也需允许对应端口。

```bash
curl --fail http://127.0.0.1/api/health
sudo systemctl status youlian --no-pager
sudo journalctl -u youlian -n 80 --no-pager
```

从外部浏览器访问 http://公网IP/，验证新增两电话及邮箱、收藏、导出与导入，重启 youlian 后确认数据库和收藏保留。只有云服务器公网地址能从外网正常使用后，才记录云部署完成。

## 更新、备份和恢复

更新前执行 `sudo bash /opt/youlian/current/deploy/backup.sh`，备份在 /var/lib/youlian/backups。新版本用同一安装器安装到新的 releases 目录，原数据库继续使用。切换 current 回到旧目录并重启服务可回退应用版本。

恢复数据库前停止服务，保留现有库副本，再复制选定备份为 /var/lib/youlian/contacts.sqlite3，设置所有者 youlian:youlian，最后启动服务。备份中可能包含用户输入，保存在服务器或本机受控目录，不提交到公开仓库。

只有已有可用域名且按服务商要求配置后再启用 HTTPS。未配置域名的试用验收使用公网 IP，不把本地隧道称为云服务器。当前通讯录为课程演示，不含多用户账户隔离，演示数据全部虚构。
