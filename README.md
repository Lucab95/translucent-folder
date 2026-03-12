# Translucent Folders

`Translucent Folders` is a GNOME Shell extension that gives desktop folders a translucent preview-style appearance on top of DING behavior.

What it changes:

- folders render as rounded translucent tiles
- the closed folder tile shows a preview of the folder contents
- single click opens a folder preview popover
- double click still opens the folder normally
- clicking outside closes the preview

Configurable settings:

- number of preview items shown
- whether expanded previews show item names
- preferred folder tile size in pixels

## Repository Contents

- [translucent-folders@lucabrugaletta.github.io](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/translucent-folders@lucabrugaletta.github.io): extension source
- [scripts/install-translucent-folders.sh](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/scripts/install-translucent-folders.sh): compile schemas, build the zip, and install locally with `gnome-extensions`
- [ATTRIBUTION.md](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/ATTRIBUTION.md): upstream attribution for DING
- [COPYING](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/COPYING): GPL license text

## Local Install

```bash
./scripts/install-translucent-folders.sh
gnome-extensions enable translucent-folders@lucabrugaletta.github.io
```

Open preferences with:

```bash
gnome-extensions prefs translucent-folders@lucabrugaletta.github.io
```

## Packaging

The local installer also produces a zip in `dist/`:

```bash
dist/translucent-folders@lucabrugaletta.github.io.shell-extension.zip
```

That zip is the package you use for local testing and release preparation.

## Notes

- This project is derived from DING and remains GPL-covered accordingly.
- The extension uses a unique UUID and is intended to be distributed as its own installable extension.
