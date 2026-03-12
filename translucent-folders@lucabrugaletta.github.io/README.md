# Translucent Folders

This folder is the standalone, uniquely named extension package intended for direct installation and future store-style distribution.

Public identity:

- Name: `Translucent Folders`
- UUID: `translucent-folders@lucabrugaletta.github.io`

Intended behavior:

- install it like a normal GNOME Shell extension
- enable it to get the translucent folder style
- disable it to return to stock DING folders
- configure folder preview count, label visibility, and tile size from the DING settings window

Implementation model:

- this package is a uniquely named DING-based extension
- when enabled, it turns off stock `ding@rastersoft.com`
- when disabled, it restores stock `ding@rastersoft.com`

Current limitation observed on Ubuntu GNOME:

- disabling this extension cleanly restores stock `ding@rastersoft.com`
- enabling this extension updates the shell settings correctly, but stock DING may remain active in the current live session until one manual disable or one relog

This is still the cleanest path if you want something users can discover and install as its own extension entry.
