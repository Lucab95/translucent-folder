from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import load_state, save_state

HIDAMARI_FLATPAK_ID = 'io.github.jeffshee.Hidamari'


@dataclass(slots=True)
class WallpaperBackendStatus:
    backend_name: str
    available: bool
    launch_command: list[str] | None
    install_command: str
    detail: str


def detect_backend() -> WallpaperBackendStatus:
    if shutil.which('hidamari'):
        return WallpaperBackendStatus(
            backend_name='Hidamari',
            available=True,
            launch_command=['hidamari'],
            install_command='pipx install hidamari  # or use the project\'s packaging method',
            detail='Native Hidamari executable detected.',
        )
    if shutil.which('flatpak') and _flatpak_has_app(HIDAMARI_FLATPAK_ID):
        return WallpaperBackendStatus(
            backend_name='Hidamari (Flatpak)',
            available=True,
            launch_command=['flatpak', 'run', HIDAMARI_FLATPAK_ID],
            install_command=f'flatpak install flathub {HIDAMARI_FLATPAK_ID}',
            detail='Flatpak install detected. This is the most practical GNOME-compatible path today.',
        )
    return WallpaperBackendStatus(
        backend_name='Hidamari',
        available=False,
        launch_command=None,
        install_command=f'flatpak install flathub {HIDAMARI_FLATPAK_ID}',
        detail='GNOME does not expose native video wallpaper support. Using a dedicated backend is the most reliable approach.',
    )


def get_selected_video() -> Path | None:
    state = load_state()
    selected = state.get('selected_video', '')
    return Path(selected) if selected else None


def set_selected_video(path: Path) -> None:
    state = load_state()
    state['selected_video'] = str(path)
    save_state(state)


def launch_backend() -> tuple[bool, str]:
    status = detect_backend()
    if not status.available or not status.launch_command:
        return False, status.install_command
    subprocess.Popen(status.launch_command)
    return True, 'Launched wallpaper backend.'


def open_selected_video_folder() -> tuple[bool, str]:
    video = get_selected_video()
    if not video:
        return False, 'No video selected yet.'
    subprocess.Popen(['xdg-open', str(video.parent)])
    return True, 'Opened video folder.'


def _flatpak_has_app(app_id: str) -> bool:
    result = subprocess.run(['flatpak', 'info', app_id], capture_output=True, text=True)
    return result.returncode == 0
