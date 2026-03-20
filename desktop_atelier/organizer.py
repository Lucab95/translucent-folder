from __future__ import annotations

import hashlib
import mimetypes
import os
import shutil
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

DESKTOP_DIR = Path.home() / 'Desktop'
STALE_DAYS = 90
LARGE_FILE_BYTES = 500 * 1024 * 1024
GROUP_FOLDER_NAMES = {
    'Documents': 'Desktop Documents',
    'Media': 'Desktop Media',
    'Archives': 'Desktop Archives',
    'Code': 'Desktop Code',
    'Other': 'Desktop Sorted',
}

DOCUMENT_SUFFIXES = {'.pdf', '.doc', '.docx', '.odt', '.txt', '.rtf', '.md'}
SHEET_SUFFIXES = {'.xls', '.xlsx', '.ods', '.csv'}
SLIDE_SUFFIXES = {'.ppt', '.pptx', '.odp'}
ARCHIVE_SUFFIXES = {'.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar'}
CODE_SUFFIXES = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.toml', '.xml', '.c', '.cpp', '.h', '.hpp', '.java', '.rs', '.go', '.sh'}
MEDIA_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.mp4', '.mkv', '.mov', '.avi', '.mp3', '.wav', '.flac'}


@dataclass(slots=True)
class DesktopItem:
    path: Path
    is_dir: bool
    size_bytes: int
    last_touched: datetime
    category: str

    @property
    def age_days(self) -> int:
        return max(0, (datetime.now() - self.last_touched).days)


@dataclass(slots=True)
class Snapshot:
    desktop_path: Path
    items: list[DesktopItem]

    @property
    def loose_files(self) -> list[DesktopItem]:
        return [item for item in self.items if not item.is_dir]

    @property
    def folders(self) -> list[DesktopItem]:
        return [item for item in self.items if item.is_dir]


@dataclass(slots=True)
class Suggestion:
    key: str
    title: str
    body: str
    emphasis: str = ''


@dataclass(slots=True)
class OrganizerReport:
    snapshot: Snapshot
    stale_items: list[DesktopItem]
    empty_folders: list[DesktopItem]
    large_files: list[DesktopItem]
    duplicate_files: list[list[DesktopItem]]
    grouping_plan: dict[str, list[DesktopItem]]
    suggestions: list[Suggestion]


def _safe_last_touched(path: Path) -> datetime:
    stat = path.stat()
    ts = max(stat.st_atime, stat.st_mtime)
    return datetime.fromtimestamp(ts)


def _categorize(path: Path, is_dir: bool) -> str:
    if is_dir:
        return 'Folders'
    suffix = path.suffix.lower()
    if suffix in DOCUMENT_SUFFIXES or suffix in SHEET_SUFFIXES or suffix in SLIDE_SUFFIXES:
        return 'Documents'
    if suffix in ARCHIVE_SUFFIXES:
        return 'Archives'
    if suffix in CODE_SUFFIXES:
        return 'Code'
    if suffix in MEDIA_SUFFIXES:
        return 'Media'
    mime, _ = mimetypes.guess_type(path.name)
    if mime and mime.startswith(('image/', 'video/', 'audio/')):
        return 'Media'
    if mime and mime.startswith(('text/', 'application/pdf')):
        return 'Documents'
    return 'Other'


def scan_desktop(desktop_path: Path | None = None) -> Snapshot:
    desktop_path = desktop_path or DESKTOP_DIR
    items: list[DesktopItem] = []
    desktop_path.mkdir(parents=True, exist_ok=True)
    for path in sorted(desktop_path.iterdir(), key=lambda p: p.name.lower()):
        if path.name.startswith('.'):
            continue
        is_dir = path.is_dir()
        size_bytes = 0 if is_dir else path.stat().st_size
        items.append(DesktopItem(
            path=path,
            is_dir=is_dir,
            size_bytes=size_bytes,
            last_touched=_safe_last_touched(path),
            category=_categorize(path, is_dir),
        ))
    return Snapshot(desktop_path=desktop_path, items=items)


def _find_duplicates(files: Iterable[DesktopItem]) -> list[list[DesktopItem]]:
    by_size: dict[int, list[DesktopItem]] = defaultdict(list)
    for item in files:
        if item.size_bytes == 0:
            continue
        by_size[item.size_bytes].append(item)

    groups: list[list[DesktopItem]] = []
    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        by_hash: dict[str, list[DesktopItem]] = defaultdict(list)
        for item in same_size:
            try:
                digest = hashlib.sha256(item.path.read_bytes()).hexdigest()
            except OSError:
                continue
            by_hash[digest].append(item)
        groups.extend(group for group in by_hash.values() if len(group) > 1)
    return groups


def build_report(snapshot: Snapshot) -> OrganizerReport:
    now = datetime.now()
    stale_cutoff = now - timedelta(days=STALE_DAYS)
    stale_items = [item for item in snapshot.items if item.last_touched <= stale_cutoff]
    empty_folders = [item for item in snapshot.folders if not any(item.path.iterdir())]
    large_files = sorted(
        [item for item in snapshot.loose_files if item.size_bytes >= LARGE_FILE_BYTES],
        key=lambda item: item.size_bytes,
        reverse=True,
    )
    duplicate_files = _find_duplicates(snapshot.loose_files)

    grouping_plan: dict[str, list[DesktopItem]] = defaultdict(list)
    for item in snapshot.loose_files:
        grouping_plan[item.category].append(item)
    grouping_plan = {category: items for category, items in grouping_plan.items() if len(items) >= 2}

    suggestions: list[Suggestion] = []
    if grouping_plan:
        suggestions.append(Suggestion(
            key='group',
            title='Group loose files',
            body='Create a few category folders and move repeated loose files out of the root desktop.',
            emphasis=f"{sum(len(items) for items in grouping_plan.values())} files can be grouped",
        ))
    if stale_items:
        suggestions.append(Suggestion(
            key='archive',
            title='Archive stale items',
            body='Move items that have not been touched recently into a dated archive folder instead of deleting them.',
            emphasis=f"{len(stale_items)} items older than {STALE_DAYS} days",
        ))
    if empty_folders:
        suggestions.append(Suggestion(
            key='empty',
            title='Remove empty folders',
            body='Trash folders that no longer contain anything useful.',
            emphasis=f"{len(empty_folders)} empty folders",
        ))
    if large_files:
        suggestions.append(Suggestion(
            key='large',
            title='Review heavy files',
            body='Large files are easy to forget on the desktop and often belong in Downloads, Media, or project folders.',
            emphasis=f"{len(large_files)} files over 500 MB",
        ))
    if duplicate_files:
        suggestions.append(Suggestion(
            key='duplicates',
            title='Check duplicates',
            body='Exact duplicate files can usually be consolidated into one copy.',
            emphasis=f"{sum(len(group) for group in duplicate_files)} duplicate files",
        ))

    return OrganizerReport(
        snapshot=snapshot,
        stale_items=stale_items,
        empty_folders=empty_folders,
        large_files=large_files,
        duplicate_files=duplicate_files,
        grouping_plan=grouping_plan,
        suggestions=suggestions,
    )


def group_loose_files(report: OrganizerReport) -> list[str]:
    moved: list[str] = []
    for category, items in report.grouping_plan.items():
        target = report.snapshot.desktop_path / GROUP_FOLDER_NAMES.get(category, GROUP_FOLDER_NAMES['Other'])
        target.mkdir(exist_ok=True)
        for item in items:
            destination = _unique_destination(target / item.path.name)
            shutil.move(str(item.path), str(destination))
            moved.append(f'{item.path.name} -> {destination.parent.name}')
    return moved


def archive_stale_items(report: OrganizerReport) -> list[str]:
    archive_root = report.snapshot.desktop_path / 'Desktop Archive' / datetime.now().strftime('%Y-%m-%d')
    archive_root.mkdir(parents=True, exist_ok=True)
    moved: list[str] = []
    for item in report.stale_items:
        destination = _unique_destination(archive_root / item.path.name)
        shutil.move(str(item.path), str(destination))
        moved.append(f'{item.path.name} -> {archive_root.relative_to(report.snapshot.desktop_path)}')
    return moved


def trash_empty_folders(report: OrganizerReport) -> list[str]:
    trashed: list[str] = []
    for item in report.empty_folders:
        subprocess.run(['gio', 'trash', str(item.path)], check=False)
        trashed.append(item.path.name)
    return trashed


def open_desktop(desktop_path: Path | None = None) -> None:
    desktop_path = desktop_path or DESKTOP_DIR
    subprocess.Popen(['xdg-open', str(desktop_path)])


def _unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    counter = 2
    while True:
        candidate = path.with_name(f'{stem} {counter}{suffix}')
        if not candidate.exists():
            return candidate
        counter += 1
