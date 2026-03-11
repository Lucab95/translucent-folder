# Desktop Organizer Folders

`Desktop Organizer Folders` is a small fork of Desktop Icons NG (`DING`) that changes how desktop folders look and behave.

It keeps DING's native desktop handling for:

- drag and drop
- monitor support
- desktop ownership and z-order
- normal file behavior

It adds an optional folder-focused UI layer:

- desktop folders render as rounded preview tiles
- the tile shows up to 4 child icons
- single click opens a preview popover
- double click still opens the folder in Files
- clicking outside closes the preview

## Status

This repository is prepared to be published as a GPLv3 fork/patch set.

It is not presented as official DING.

## Upstream

This project is derived from:

- Desktop Icons NG (`DING`)
- Upstream site: https://gitlab.com/rastersoft/desktop-icons-ng

See [ATTRIBUTION.md](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/ATTRIBUTION.md) for details.

## License

This fork should be distributed under `GPL-3.0-only`.

- Full license text: [COPYING](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/COPYING)
- Summary of changes: [CHANGES.md](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/CHANGES.md)

## Repository Layout

- [ding-transparent-folders@lucabrugaletta.com](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/ding-transparent-folders@lucabrugaletta.com): source fork of DING with the folder-preview changes
- [scripts/install-user-override.sh](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/scripts/install-user-override.sh): install as a local override in `~/.local/share/gnome-shell/extensions/ding@rastersoft.com`
- [scripts/install-system-extension.sh](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/scripts/install-system-extension.sh): install into `/usr/share/...` with backup
- [scripts/restore-system-extension.sh](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/scripts/restore-system-extension.sh): restore the backed up system DING copy
- `transparent-folders@lucabrugaletta`: archived experimental overlay approach, not the recommended path

## Install

### Option 1: User override

Use this if your GNOME session prefers the user extension copy over the distro one.

```bash
./scripts/install-user-override.sh
```

### Option 2: System install

Use this if Ubuntu keeps loading DING from `/usr/share/gnome-shell/extensions/ding@rastersoft.com`.

```bash
./scripts/install-system-extension.sh
```

This script:

- creates a dated backup of the current system DING
- copies this fork into the live system DING path
- restarts the DING extension

## Verify

```bash
gnome-extensions info ding@rastersoft.com
```

What matters:

- the extension is enabled
- the folder preview behavior is active

If GNOME keeps stale code loaded, log out and back in once.

## Publishing

Before publishing to GitHub:

1. Create a new repository for this fork.
2. Keep `COPYING`, `ATTRIBUTION.md`, and `CHANGES.md` in the root.
3. Make clear in the repo description that this is a DING fork/patch set.
4. If you later publish a separate commercial organizer app, keep this DING-derived component separate and GPL.

See [PUBLISHING.md](/home/lucabrugaletta/Desktop/personal/desktop%20organizer/PUBLISHING.md).
