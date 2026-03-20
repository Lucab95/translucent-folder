# Translucent Folders

Translucent Folders is the desktop-folders part of a broader Ubuntu GNOME desktop experience project.

Today the repository contains two connected pieces:

- `Translucent Folders`: the GNOME Shell extension that changes desktop folder presentation
- `Desktop Atelier`: a companion app for desktop cleanup, organization, and motion wallpaper control

## Translucent Folders

Translucent Folders changes how desktop folders look on Ubuntu GNOME.

Instead of the standard folder icon, folders are rendered as soft translucent tiles that preview their contents before you open them. A single click expands the folder in place. A double click still opens it normally.

### What It Does

- turns desktop folders into translucent preview tiles
- shows folder contents directly on the closed folder icon
- opens an expanded folder preview on single click
- keeps normal folder opening on double click
- closes the expanded preview when you click away

### Settings

The extension has its own preferences page with controls for:

- preview items shown
- item names in expanded previews
- folder tile size

It also includes a separate button to open the regular DING desktop settings for general desktop icon behavior.

### Screenshots

| Closed folder | Expanded preview |
| --- | --- |
| ![Closed folder preview tile](Folder%20initial.png) | ![Expanded folder preview popover](Folder%20clicked.png) |

### Install

```bash
./scripts/install-translucent-folders.sh
gnome-extensions enable translucent-folders@lucabrugaletta.github.io
```

To open the extension preferences:

```bash
gnome-extensions prefs translucent-folders@lucabrugaletta.github.io
```

### Build Release Zip

```bash
./scripts/build-release.sh
```

This produces:

```text
dist/translucent-folders@lucabrugaletta.github.io.shell-extension.zip
```

That zip is the package to use for local testing, GitHub releases, and GNOME extension submission.

## Desktop Atelier

Desktop Atelier is the companion control app for the same workflow.

It focuses on two things:

- helping you clean up and reorganize a messy desktop
- managing the practical path to video wallpaper on GNOME

Current organizer features:

- scan the desktop and surface stale items
- suggest grouping loose files by category
- flag large files and exact duplicates
- archive old desktop items into a dated archive folder
- trash empty folders

Current wallpaper features:

- select a video to use as wallpaper
- detect a GNOME-friendly wallpaper backend
- launch the backend when available
- show install guidance when the backend is missing

Run the app with:

```bash
./scripts/run-desktop-atelier.sh
```

More detail: [`desktop_atelier/README.md`](desktop_atelier/README.md)

## Project Layout

- [`translucent-folders@lucabrugaletta.github.io/`](translucent-folders@lucabrugaletta.github.io): extension source
- [`desktop_atelier/`](desktop_atelier): GTK4/libadwaita companion app
- [`scripts/build-release.sh`](scripts/build-release.sh): builds the release zip
- [`scripts/install-translucent-folders.sh`](scripts/install-translucent-folders.sh): installs the extension locally
- [`scripts/run-desktop-atelier.sh`](scripts/run-desktop-atelier.sh): launches the companion app
- [`ATTRIBUTION.md`](ATTRIBUTION.md): upstream attribution
- [`COPYING`](COPYING): GPL license text

## Status

The extension is packaged as a standalone installable project and currently targets GNOME Shell 46 to 49.

The companion app now provides a first complete vertical slice for:

- desktop organization suggestions and actions
- wallpaper backend detection and launch
- extension install/settings integration

The main open questions are product-level rather than structural now:

- how aggressive the organizer should be about automatic actions
- which wallpaper backend should be the long-term default for GNOME users
- whether `extensions.gnome.org` review accepts the current DING coordination model

## License

This project is derived from DING and distributed under GPL terms accordingly.
