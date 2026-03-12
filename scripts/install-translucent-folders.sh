#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UUID="translucent-folders@lucabrugaletta.github.io"
SRC_DIR="$ROOT_DIR/$UUID"
DIST_DIR="$ROOT_DIR/dist"
BUNDLE_PATH="$DIST_DIR/$UUID.shell-extension.zip"
SCHEMA_DIR="$SRC_DIR/schemas"

mkdir -p "$DIST_DIR"
glib-compile-schemas "$SCHEMA_DIR"

(
    cd "$SRC_DIR"
    rm -f "$BUNDLE_PATH"
    zip -qr "$BUNDLE_PATH" \
        metadata.json \
        extension.js \
        prefs.js \
        emulateX11WindowType.js \
        gnomeShellOverride.js \
        visibleArea.js \
        app \
        schemas
)

gnome-extensions install -f "$BUNDLE_PATH"
gnome-extensions info "$UUID" || true

echo
echo "Installed $UUID"
echo "Enable with: gnome-extensions enable $UUID"
echo "Disable with: gnome-extensions disable $UUID"
echo "If stock DING stays visible after enabling, log out/in once or disable ding@rastersoft.com manually once."
