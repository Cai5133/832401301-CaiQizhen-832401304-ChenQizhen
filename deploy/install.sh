#!/usr/bin/env bash
# Run from an extracted deployment bundle: sudo bash deploy/install.sh
set -euo pipefail
if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo: sudo bash deploy/install.sh" >&2
  exit 1
fi
source /etc/os-release
if [[ "${ID}" != ubuntu || "${VERSION_ID}" != 24.04 ]]; then
  echo "This installer targets Ubuntu 24.04. Check the OS before deploying." >&2
  exit 1
fi
BUNDLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "${BUNDLE_ROOT}/frontend/dist/index.html" ]]; then
  echo "Missing frontend/dist. Use the complete deployment bundle." >&2
  exit 1
fi
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3 python3-venv nginx curl rsync
id youlian >/dev/null 2>&1 || useradd --system --home /var/lib/youlian --shell /usr/sbin/nologin youlian
install -d -o youlian -g youlian -m 750 /var/lib/youlian /var/lib/youlian/backups
install -d -m 755 /opt/youlian/releases
RELEASE_PATH="/opt/youlian/releases/$(date -u +%Y%m%dT%H%M%SZ)-$$"
install -d -m 755 "${RELEASE_PATH}"
rsync -a --exclude=.venv --exclude=node_modules --exclude=.git --exclude='*.sqlite*' --exclude='*.db' "${BUNDLE_ROOT}/backend" "${BUNDLE_ROOT}/frontend" "${BUNDLE_ROOT}/deploy" "${RELEASE_PATH}/"
python3 -m venv "${RELEASE_PATH}/backend/.venv"
"${RELEASE_PATH}/backend/.venv/bin/python" -m pip install --index-url https://mirrors.cloud.tencent.com/pypi/simple -r "${RELEASE_PATH}/backend/requirements.txt"
if [[ ! -f /etc/youlian.env ]]; then
  printf '%s\n' 'ADDRESS_BOOK_DB=/var/lib/youlian/contacts.sqlite3' > /etc/youlian.env
  chmod 640 /etc/youlian.env
  chown root:youlian /etc/youlian.env
fi
ln -sfn "${RELEASE_PATH}" /opt/youlian/current
install -m 644 "${RELEASE_PATH}/deploy/youlian.service" /etc/systemd/system/youlian.service
install -m 644 "${RELEASE_PATH}/deploy/nginx.conf" /etc/nginx/sites-available/youlian
ln -sfn /etc/nginx/sites-available/youlian /etc/nginx/sites-enabled/youlian
if [[ -L /etc/nginx/sites-enabled/default ]]; then
  rm /etc/nginx/sites-enabled/default
fi
nginx -t
systemctl daemon-reload
systemctl enable --now youlian
systemctl restart youlian
systemctl enable --now nginx
systemctl reload nginx
for attempt in {1..30}; do
  if curl --fail --silent http://127.0.0.1/api/health; then
    echo
    echo "Deployment ready. Test http://PUBLIC_IP/ from another network."
    exit 0
  fi
  sleep 1
done
journalctl -u youlian -n 40 --no-pager
exit 1
