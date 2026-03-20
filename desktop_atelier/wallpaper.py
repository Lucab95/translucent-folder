from __future__ import annotations

import json
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


@dataclass(slots=True)
class VideoMetadata:
    path: Path
    width: int | None
    height: int | None
    duration_seconds: float | None
    frame_rate: float | None
    codec: str | None
    size_bytes: int


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


def clear_selected_video() -> None:
    state = load_state()
    state['selected_video'] = ''
    save_state(state)


def probe_selected_video() -> VideoMetadata | None:
    video = get_selected_video()
    if not video or not video.exists():
        return None
    return probe_video(video)


def probe_video(path: Path) -> VideoMetadata | None:
    if not path.exists():
        return None

    if shutil.which('ffprobe'):
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'error',
                '-print_format', 'json',
                '-show_streams',
                '-show_format',
                str(path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                video_stream = next((stream for stream in data.get('streams', []) if stream.get('codec_type') == 'video'), {})
                duration = _safe_float(data.get('format', {}).get('duration')) or _safe_float(video_stream.get('duration'))
                frame_rate = _parse_frame_rate(video_stream.get('avg_frame_rate') or video_stream.get('r_frame_rate'))
                return VideoMetadata(
                    path=path,
                    width=_safe_int(video_stream.get('width')),
                    height=_safe_int(video_stream.get('height')),
                    duration_seconds=duration,
                    frame_rate=frame_rate,
                    codec=video_stream.get('codec_name'),
                    size_bytes=path.stat().st_size,
                )
            except (OSError, ValueError, StopIteration, KeyError, json.JSONDecodeError):
                pass

    return VideoMetadata(
        path=path,
        width=None,
        height=None,
        duration_seconds=None,
        frame_rate=None,
        codec=None,
        size_bytes=path.stat().st_size,
    )


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


def _safe_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_frame_rate(value: str | None) -> float | None:
    if not value or value == '0/0':
        return None
    if '/' in value:
        numerator, denominator = value.split('/', 1)
        try:
            numerator_f = float(numerator)
            denominator_f = float(denominator)
            if denominator_f == 0:
                return None
            return numerator_f / denominator_f
        except ValueError:
            return None
    return _safe_float(value)
