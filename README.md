# Translucent Folders

Translucent Folders is a GNOME Shell extension that changes how desktop folders look on Ubuntu GNOME.

Instead of the standard folder icon, folders are rendered as soft translucent tiles that preview their contents before you open them. A single click expands the folder in place. A double click still opens it normally.

## What It Does

- turns desktop folders into translucent preview tiles
- shows folder contents directly on the closed folder icon
- opens an expanded folder preview on single click
- keeps normal folder opening on double click
- closes the expanded preview when you click away

## Settings

The extension has its own preferences page with controls for:

- preview items shown
- item names in expanded previews
- folder tile size

It also includes a separate button to open the regular DING desktop settings for general desktop icon behavior.

## Screenshots

| Closed folder | Expanded preview |
| --- | --- |
| ![Closed folder preview tile](Folder%20initial.png) | ![Expanded folder preview popover](Folder%20clicked.png) |

## Install

For local installation:

```bash
./scripts/install-translucent-folders.sh
gnome-extensions enable translucent-folders@lucabrugaletta.github.io
```

To open the extension preferences:

```bash
gnome-extensions prefs translucent-folders@lucabrugaletta.github.io
```

## Build Release Zip

```bash
./scripts/build-release.sh
```

This produces:

```text
dist/translucent-folders@lucabrugaletta.github.io.shell-extension.zip
```

That zip is the package to use for local testing, GitHub releases, and GNOME extension submission.

## Project Layout

- [`translucent-folders@lucabrugaletta.github.io/`](translucent-folders@lucabrugaletta.github.io): extension source
- [`scripts/build-release.sh`](scripts/build-release.sh): builds the release zip
- [`scripts/install-translucent-folders.sh`](scripts/install-translucent-folders.sh): installs the extension locally
- [`ATTRIBUTION.md`](ATTRIBUTION.md): upstream attribution
- [`COPYING`](COPYING): GPL license text

## Status

The extension is packaged as a standalone installable project and currently targets GNOME Shell 46 to 49.

The remaining open question is GNOME review policy: the extension still coordinates with stock `ding@rastersoft.com`, so `extensions.gnome.org` review may treat it as a special case.

## License

This project is derived from DING and distributed under GPL terms accordingly.
