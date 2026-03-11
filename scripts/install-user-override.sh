#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/ding-transparent-folders@lucabrugaletta.com"
DEST_DIR="$HOME/.local/share/gnome-shell/extensions/ding@rastersoft.com"

mkdir -p "$DEST_DIR"
rsync -a --delete "$SRC_DIR/" "$DEST_DIR/"

gnome-extensions disable transparent-folders@lucabrugaletta >/dev/null 2>&1 || true
gnome-extensions disable ding@rastersoft.com >/dev/null 2>&1 || true
gnome-extensions enable ding@rastersoft.com
gnome-extensions info ding@rastersoft.com
