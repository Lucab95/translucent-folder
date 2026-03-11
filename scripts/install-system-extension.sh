#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/ding-transparent-folders@lucabrugaletta.com"
SYSTEM_DIR="/usr/share/gnome-shell/extensions/ding@rastersoft.com"
BACKUP_DIR="${SYSTEM_DIR}.backup-$(date +%F)"

if [ ! -d "$BACKUP_DIR" ]; then
    sudo cp -a "$SYSTEM_DIR" "$BACKUP_DIR"
    echo "Created backup at $BACKUP_DIR"
else
    echo "Backup already exists at $BACKUP_DIR"
fi

sudo rsync -a --delete "$SRC_DIR/" "$SYSTEM_DIR/"

gnome-extensions disable transparent-folders@lucabrugaletta >/dev/null 2>&1 || true
gnome-extensions disable ding@rastersoft.com >/dev/null 2>&1 || true
gnome-extensions enable ding@rastersoft.com
gnome-extensions info ding@rastersoft.com
