# Desktop Atelier

Desktop Atelier is the companion control app for the Translucent Folders project.

It brings two workflows into one GNOME-friendly window:

- desktop cleanup and reorganization suggestions
- motion wallpaper control, using a dedicated video wallpaper backend when GNOME itself does not provide one

## What It Does Today

### Organizer

- scans `~/Desktop`
- highlights stale items, empty folders, large files, and exact duplicate files
- suggests grouping loose files into category folders
- can archive stale items into a dated archive folder
- can trash empty folders

### Motion Wallpaper

- tracks a selected video wallpaper file
- detects a usable GNOME-compatible backend
- launches the backend when available
- exposes install guidance when the backend is missing

### Extension Integration

- checks the status of `Translucent Folders`
- can run the extension install/update script
- can open the extension preferences directly

## Run

```bash
./scripts/run-desktop-atelier.sh
```

The app uses `/usr/bin/python3` so it can rely on Ubuntu's GTK4/libadwaita bindings instead of the active conda environment.

## Why The Wallpaper Backend Is External

GNOME does not expose native video wallpaper support. The practical path is to use a backend designed for it.

The current app is structured so that the wallpaper feature can work with dedicated Linux wallpaper tools instead of pretending this is a normal GNOME background API.
