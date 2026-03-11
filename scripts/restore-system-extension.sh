#!/usr/bin/env bash
set -euo pipefail

SYSTEM_DIR="/usr/share/gnome-shell/extensions/ding@rastersoft.com"

LATEST_BACKUP="$(find /usr/share/gnome-shell/extensions -maxdepth 1 -type d -name 'ding@rastersoft.com.backup-*' | sort | tail -n 1)"

if [ -z "${LATEST_BACKUP:-}" ]; then
    echo "No system DING backup found."
    exit 1
fi

sudo rsync -a --delete "$LATEST_BACKUP/" "$SYSTEM_DIR/"

gnome-extensions disable ding@rastersoft.com >/dev/null 2>&1 || true
gnome-extensions enable ding@rastersoft.com
gnome-extensions info ding@rastersoft.com
