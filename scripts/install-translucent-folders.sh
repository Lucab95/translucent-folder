#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UUID="translucent-folders@lucabrugaletta.github.io"
DIST_DIR="$ROOT_DIR/dist"
BUNDLE_PATH="$DIST_DIR/$UUID.shell-extension.zip"

"$ROOT_DIR/scripts/build-release.sh" >/dev/null

gnome-extensions install -f "$BUNDLE_PATH"
gnome-extensions info "$UUID" || true

echo
echo "Installed $UUID"
echo "Enable with: gnome-extensions enable $UUID"
echo "Disable with: gnome-extensions disable $UUID"
echo "If stock DING stays visible after enabling, log out/in once or disable ding@rastersoft.com manually once."
