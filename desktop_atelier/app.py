from __future__ import annotations

import subprocess
from pathlib import Path

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gio, Gdk, GLib, Gtk

from . import organizer, wallpaper

APP_ID = 'io.github.lucab95.DesktopAtelier'
EXTENSION_UUID = 'translucent-folders@lucabrugaletta.github.io'
REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = REPO_ROOT / 'scripts' / 'install-translucent-folders.sh'


class DesktopAtelierApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID)
        self.connect('activate', self.on_activate)

    def on_activate(self, _app: Adw.Application) -> None:
        window = DesktopAtelierWindow(self)
        window.present()


class DesktopAtelierWindow(Adw.ApplicationWindow):
    def __init__(self, app: DesktopAtelierApplication) -> None:
        super().__init__(application=app, title='Desktop Atelier')
        self.set_default_size(1180, 820)

        self._load_css()
        self.report = organizer.build_report(organizer.scan_desktop())

        self.toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(title='Desktop Atelier', subtitle='Tidy the desktop. Keep the motion.'))
        self.toolbar_view.add_top_bar(header)

        self.switcher = Adw.ViewSwitcher()
        header.pack_start(self.switcher)

        self.toast_overlay = Adw.ToastOverlay()
        self.toolbar_view.set_content(self.toast_overlay)
        self.set_content(self.toolbar_view)

        self._rebuild_views()

    def _load_css(self) -> None:
        provider = Gtk.CssProvider()
        provider.load_from_path(str(REPO_ROOT / 'desktop_atelier' / 'styles.css'))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _build_overview_page(self) -> Gtk.Widget:
        clamp = Adw.Clamp(maximum_size=1040)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, margin_top=24, margin_bottom=32, margin_start=24, margin_end=24)
        clamp.set_child(box)

        hero = self._make_card('hero-card')
        hero_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hero.append(hero_box)
        hero_box.append(self._label('DESKTOP CONTROL ROOM', ['hero-eyebrow']))
        hero_box.append(self._label('One app to tame the mess and own the backdrop.', ['hero-title']))
        hero_box.append(self._label(
            'Desktop Atelier wraps your translucent folder workflow, scans the desktop for cleanup opportunities, and gives you a practical path to video wallpaper on GNOME.',
            ['hero-body'], wrap=True,
        ))
        box.append(hero)

        metrics = Gtk.FlowBox(max_children_per_line=4, selection_mode=Gtk.SelectionMode.NONE, column_spacing=14, row_spacing=14)
        metrics.insert(self._metric_card('Desktop items', str(len(self.report.snapshot.items))), -1)
        metrics.insert(self._metric_card('Loose files', str(len(self.report.snapshot.loose_files))), -1)
        metrics.insert(self._metric_card('Stale items', str(len(self.report.stale_items))), -1)
        metrics.insert(self._metric_card('Large files', str(len(self.report.large_files))), -1)
        box.append(metrics)

        spotlight = self._make_card('panel-card')
        spotlight_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        spotlight.append(spotlight_box)
        spotlight_box.append(self._section_title('What the app can act on now'))
        for suggestion in self.report.suggestions[:4]:
            row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            row.append(self._label(suggestion.title))
            row.append(self._label(f'{suggestion.body} {suggestion.emphasis}'.strip(), ['subtle-caption'], wrap=True))
            spotlight_box.append(row)
        box.append(spotlight)

        return self._wrap_page(clamp)

    def _build_organizer_page(self) -> Gtk.Widget:
        clamp = Adw.Clamp(maximum_size=1040)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, margin_top=24, margin_bottom=32, margin_start=24, margin_end=24)
        clamp.set_child(outer)

        summary = self._make_card('panel-card')
        summary_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        summary.append(summary_box)
        summary_box.append(self._section_title('Organizer suggestions'))
        summary_box.append(self._label(
            'Suggestions are based on the current Desktop folder. Last touched uses access time when available, otherwise modification time.',
            ['subtle-caption'], wrap=True,
        ))
        outer.append(summary)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        actions.append(self._button('Refresh scan', self._refresh_report, suggested=True))
        actions.append(self._button('Open Desktop', self._open_desktop))
        outer.append(actions)

        suggestion_card = self._make_card('panel-card')
        suggestion_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        suggestion_card.append(suggestion_box)
        for suggestion in self.report.suggestions:
            suggestion_box.append(self._suggestion_row(suggestion))
        if not self.report.suggestions:
            suggestion_box.append(self._label('The desktop already looks tidy. Nothing urgent to suggest right now.', ['subtle-caption']))
        outer.append(suggestion_card)

        details = Gtk.Grid(column_spacing=18, row_spacing=18)
        details.attach(self._detail_card('Stale items', self._format_items(self.report.stale_items[:6])), 0, 0, 1, 1)
        details.attach(self._detail_card('Large files', self._format_large_files(self.report.large_files[:6])), 1, 0, 1, 1)
        details.attach(self._detail_card('Duplicate files', self._format_duplicates(self.report.duplicate_files[:3])), 0, 1, 1, 1)
        details.attach(self._detail_card('Grouping preview', self._format_grouping(self.report.grouping_plan)), 1, 1, 1, 1)
        outer.append(details)

        return self._wrap_page(clamp)

    def _build_wallpaper_page(self) -> Gtk.Widget:
        clamp = Adw.Clamp(maximum_size=1040)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, margin_top=24, margin_bottom=32, margin_start=24, margin_end=24)
        clamp.set_child(outer)

        status = wallpaper.detect_backend()
        selected_video = wallpaper.get_selected_video()

        hero = self._make_card('panel-card')
        hero_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hero.append(hero_box)
        hero_box.append(self._section_title('Motion wallpaper strategy'))
        hero_box.append(self._label(
            'GNOME does not provide native video wallpaper support. The pragmatic route is to use a purpose-built backend and let this app manage selection, launch, and guidance.',
            wrap=True,
        ))
        hero_box.append(self._label(status.detail, ['subtle-caption'], wrap=True))
        outer.append(hero)

        status_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        status_row.append(self._metric_card('Backend', status.backend_name))
        status_row.append(self._metric_card('Availability', 'Ready' if status.available else 'Needs install'))
        status_row.append(self._metric_card('Selected video', selected_video.name if selected_video else 'None'))
        outer.append(status_row)

        controls = self._make_card('panel-card')
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        controls.append(controls_box)
        controls_box.append(self._section_title('Wallpaper controls'))
        controls_box.append(self._label(
            status.install_command if not status.available else 'Pick a video here, then launch the backend to finish applying it. The selected file is stored so the workflow stays in one place.',
            ['subtle-caption'],
            wrap=True,
        ))

        button_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_row.append(self._button('Choose video', self._choose_video, suggested=True))
        button_row.append(self._button('Launch wallpaper backend', self._launch_wallpaper_backend))
        button_row.append(self._button('Open selected video folder', self._open_video_folder))
        if not status.available:
            button_row.append(self._button('Copy install command', self._copy_backend_install_command))
        controls_box.append(button_row)

        controls_box.append(self._label(
            f'Selected video: {selected_video}' if selected_video else 'Selected video: none yet',
            wrap=True,
        ))
        outer.append(controls)

        extension_card = self._make_card('panel-card')
        extension_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        extension_card.append(extension_box)
        extension_box.append(self._section_title('Translucent folders integration'))
        extension_box.append(self._label(self._extension_status_text(), ['subtle-caption'], wrap=True))
        ext_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        ext_buttons.append(self._button('Install / update extension', self._install_extension))
        ext_buttons.append(self._button('Open extension settings', self._open_extension_prefs))
        extension_box.append(ext_buttons)
        outer.append(extension_card)

        return self._wrap_page(clamp)

    def _wrap_page(self, child: Gtk.Widget) -> Gtk.Widget:
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_child(child)
        return scroller

    def _rebuild_views(self) -> None:
        self.view_stack = Adw.ViewStack()
        self.view_stack.add_titled_with_icon(self._build_overview_page(), 'overview', 'Overview', 'view-grid-symbolic')
        self.view_stack.add_titled_with_icon(self._build_organizer_page(), 'organizer', 'Organizer', 'folder-symbolic')
        self.view_stack.add_titled_with_icon(self._build_wallpaper_page(), 'wallpaper', 'Motion Wallpaper', 'video-display-symbolic')
        self.switcher.set_stack(self.view_stack)
        self.toast_overlay.set_child(self.view_stack)

    def _suggestion_row(self, suggestion: organizer.Suggestion) -> Gtk.Widget:
        row = self._make_card('panel-card')
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        row.append(row_box)

        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        text.set_hexpand(True)
        text.append(self._label(suggestion.title))
        text.append(self._label(suggestion.body, ['subtle-caption'], wrap=True))
        if suggestion.emphasis:
            text.append(self._label(suggestion.emphasis, ['subtle-caption']))
        row_box.append(text)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        if suggestion.key == 'group':
            actions.append(self._button('Group now', self._group_now, suggested=True))
        elif suggestion.key == 'archive':
            actions.append(self._button('Archive stale', self._archive_stale, suggested=True))
        elif suggestion.key == 'empty':
            actions.append(self._button('Trash empty folders', self._trash_empty_folders))
        else:
            actions.append(self._button('Open Desktop', self._open_desktop))
        row_box.append(actions)
        return row

    def _detail_card(self, title: str, lines: list[str]) -> Gtk.Widget:
        card = self._make_card('panel-card')
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.append(box)
        box.append(self._section_title(title))
        if not lines:
            box.append(self._label('Nothing to show right now.', ['subtle-caption']))
        else:
            for line in lines:
                box.append(self._label(line, ['subtle-caption'], wrap=True))
        return card

    def _metric_card(self, label: str, value: str) -> Gtk.Widget:
        card = self._make_card('metric-card')
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        card.append(box)
        box.append(self._label(value, ['metric-number']))
        box.append(self._label(label, ['metric-label']))
        return card

    def _make_card(self, css_class: str) -> Gtk.Widget:
        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        frame.add_css_class(css_class)
        return frame

    def _section_title(self, text: str) -> Gtk.Widget:
        return self._label(text, weight='bold')

    def _label(self, text: str, classes: list[str] | None = None, wrap: bool = False, weight: str | None = None) -> Gtk.Widget:
        label = Gtk.Label(label=text, xalign=0)
        label.set_wrap(wrap)
        label.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        if weight == 'bold':
            label.set_markup(f'<b>{GLib.markup_escape_text(text)}</b>')
        if classes:
            for css_class in classes:
                label.add_css_class(css_class)
        return label

    def _button(self, text: str, callback, suggested: bool = False) -> Gtk.Widget:
        button = Gtk.Button(label=text)
        if suggested:
            button.add_css_class('suggested-action')
        button.connect('clicked', callback)
        return button

    def _format_items(self, items: list[organizer.DesktopItem]) -> list[str]:
        return [f'{item.path.name} · {item.age_days} days' for item in items]

    def _format_large_files(self, items: list[organizer.DesktopItem]) -> list[str]:
        return [f'{item.path.name} · {item.size_bytes / (1024 * 1024):.0f} MB' for item in items]

    def _format_duplicates(self, groups: list[list[organizer.DesktopItem]]) -> list[str]:
        lines: list[str] = []
        for group in groups:
            names = ', '.join(item.path.name for item in group)
            lines.append(names)
        return lines

    def _format_grouping(self, grouping_plan: dict[str, list[organizer.DesktopItem]]) -> list[str]:
        return [f'{category}: {len(items)} files' for category, items in grouping_plan.items()]

    def _refresh_report(self, _button: Gtk.Button | None = None) -> None:
        self.report = organizer.build_report(organizer.scan_desktop())
        self._rebuild_views()
        self._show_message('Desktop scan refreshed.')

    def _group_now(self, _button: Gtk.Button) -> None:
        moved = organizer.group_loose_files(self.report)
        self.report = organizer.build_report(organizer.scan_desktop())
        self._rebuild_views()
        self._show_message(f'Grouped {len(moved)} files.' if moved else 'Nothing needed grouping.')

    def _archive_stale(self, _button: Gtk.Button) -> None:
        moved = organizer.archive_stale_items(self.report)
        self.report = organizer.build_report(organizer.scan_desktop())
        self._rebuild_views()
        self._show_message(f'Archived {len(moved)} items.' if moved else 'No stale items to archive.')

    def _trash_empty_folders(self, _button: Gtk.Button) -> None:
        trashed = organizer.trash_empty_folders(self.report)
        self.report = organizer.build_report(organizer.scan_desktop())
        self._rebuild_views()
        self._show_message(f'Trashed {len(trashed)} empty folders.' if trashed else 'No empty folders found.')

    def _open_desktop(self, _button: Gtk.Button | None = None) -> None:
        organizer.open_desktop()

    def _choose_video(self, _button: Gtk.Button) -> None:
        dialog = Gtk.FileDialog(title='Choose a wallpaper video')
        filters = Gio.ListStore.new(Gtk.FileFilter)
        file_filter = Gtk.FileFilter()
        file_filter.set_name('Video files')
        file_filter.add_mime_type('video/*')
        file_filter.add_pattern('*.mp4')
        file_filter.add_pattern('*.mkv')
        file_filter.add_pattern('*.mov')
        filters.append(file_filter)
        dialog.set_filters(filters)
        dialog.open(self, None, self._on_video_selected)

    def _on_video_selected(self, dialog: Gtk.FileDialog, result) -> None:
        try:
            file = dialog.open_finish(result)
        except Exception:
            return
        if not file:
            return
        path = Path(file.get_path())
        wallpaper.set_selected_video(path)
        self._rebuild_views()
        self._show_message(f'Selected video: {path.name}')

    def _launch_wallpaper_backend(self, _button: Gtk.Button) -> None:
        ok, message = wallpaper.launch_backend()
        self._show_message(message if ok else f'Backend not available. Install with: {message}')

    def _open_video_folder(self, _button: Gtk.Button) -> None:
        ok, message = wallpaper.open_selected_video_folder()
        self._show_message(message)

    def _copy_backend_install_command(self, _button: Gtk.Button) -> None:
        command = wallpaper.detect_backend().install_command
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(command)
        self._show_message('Copied backend install command.')

    def _install_extension(self, _button: Gtk.Button) -> None:
        subprocess.Popen([str(INSTALL_SCRIPT)])
        self._show_message('Started extension install/update script in the background.')

    def _open_extension_prefs(self, _button: Gtk.Button) -> None:
        subprocess.Popen(['gnome-extensions', 'prefs', EXTENSION_UUID])

    def _extension_status_text(self) -> str:
        result = subprocess.run(['gnome-extensions', 'info', EXTENSION_UUID], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else 'The translucent folders extension is not currently installed in this GNOME session.'

    def _show_message(self, message: str) -> None:
        self.toast_overlay.add_toast(Adw.Toast(title=message))
