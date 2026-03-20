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

SECTION_TITLES = {
    'suggestions': 'Suggestions',
    'stale': 'Stale Items',
    'large': 'Large Files',
    'grouping': 'Grouping Plan',
    'duplicates': 'Duplicates',
    'empty': 'Empty Folders',
}


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
        self.set_default_size(1220, 860)

        self.organizer_section = 'suggestions'
        self.selected_payload = None
        self._building_views = False

        self._load_css()
        self.report = organizer.build_report(organizer.scan_desktop())

        self.toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(title='Desktop Atelier', subtitle='Desktop cleanup and motion wallpaper'))
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

    def _rebuild_views(self) -> None:
        self._building_views = True
        self.view_stack = Adw.ViewStack()
        self.view_stack.add_titled_with_icon(self._build_overview_page(), 'overview', 'Overview', 'view-grid-symbolic')
        self.view_stack.add_titled_with_icon(self._build_organizer_page(), 'organizer', 'Organizer', 'folder-symbolic')
        self.view_stack.add_titled_with_icon(self._build_wallpaper_page(), 'wallpaper', 'Motion Wallpaper', 'video-display-symbolic')
        self.switcher.set_stack(self.view_stack)
        self.toast_overlay.set_child(self.view_stack)
        self._building_views = False

    def _build_overview_page(self) -> Gtk.Widget:
        clamp = Adw.Clamp(maximum_size=1080)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, margin_top=24, margin_bottom=32, margin_start=24, margin_end=24)
        clamp.set_child(box)

        hero = self._make_card('hero-card')
        hero_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hero.append(hero_box)
        hero_box.append(self._label('DESKTOP CONTROL ROOM', ['hero-eyebrow']))
        hero_box.append(self._label('Tidy the root desktop. Keep the motion wallpaper workflow in one place.', ['hero-title']))
        hero_box.append(self._label(
            'Use the overview to jump into the exact problem area: stale items, heavy files, grouping opportunities, or wallpaper setup.',
            ['hero-body'],
            wrap=True,
        ))
        box.append(hero)

        metric_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        metric_row.append(self._metric_button('Desktop items', str(len(self.report.snapshot.items)), lambda *_: organizer.open_desktop()))
        metric_row.append(self._metric_button('Loose files', str(len(self.report.snapshot.loose_files)), lambda *_: self._jump_to_section('grouping')))
        metric_row.append(self._metric_button('Stale items', str(len(self.report.stale_items)), lambda *_: self._jump_to_section('stale')))
        metric_row.append(self._metric_button('Large files', str(len(self.report.large_files)), lambda *_: self._jump_to_section('large')))
        box.append(metric_row)

        queue = self._make_card('panel-card')
        queue_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        queue.append(queue_box)
        queue_box.append(self._section_title('Action queue'))
        if self.report.suggestions:
            for suggestion in self.report.suggestions:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                row_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                row_text.set_hexpand(True)
                row_text.append(self._label(suggestion.title))
                row_text.append(self._label(f'{suggestion.body} {suggestion.emphasis}'.strip(), ['subtle-caption'], wrap=True))
                row.append(row_text)
                row.append(self._button('Open', lambda _btn, key=suggestion.key: self._jump_to_section(self._section_for_suggestion(key))))
                queue_box.append(row)
        else:
            queue_box.append(self._label('Nothing urgent surfaced in the current desktop scan.', ['subtle-caption']))
        box.append(queue)

        return self._wrap_page(clamp)

    def _build_organizer_page(self) -> Gtk.Widget:
        clamp = Adw.Clamp(maximum_size=1140)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, margin_top=24, margin_bottom=32, margin_start=24, margin_end=24)
        clamp.set_child(outer)

        top = self._make_card('panel-card')
        top_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        top.append(top_box)
        top_box.append(self._section_title('Organizer'))
        top_box.append(self._label(
            'Pick a section, inspect the files or folders involved, and then apply a concrete action. This page is meant to work as a cleanup console, not a dashboard.',
            ['subtle-caption'],
            wrap=True,
        ))
        outer.append(top)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        actions.append(self._button('Refresh scan', self._refresh_report, suggested=True))
        actions.append(self._button('Open Desktop', self._open_desktop))
        actions.append(self._button('Group loose files', self._group_now))
        actions.append(self._button('Archive stale items', self._archive_stale))
        outer.append(actions)

        filter_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for section in ['suggestions', 'grouping', 'stale', 'large', 'duplicates', 'empty']:
            filter_row.append(self._filter_button(section))
        outer.append(filter_row)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        content.append(self._build_organizer_list_panel())
        content.append(self._build_organizer_detail_panel())
        outer.append(content)

        return self._wrap_page(clamp)

    def _build_organizer_list_panel(self) -> Gtk.Widget:
        panel = self._make_card('panel-card')
        panel.set_size_request(420, -1)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        panel.append(box)
        box.append(self._section_title(SECTION_TITLES[self.organizer_section]))

        entries = self._organizer_entries()
        listbox = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        listbox.add_css_class('boxed-list')
        listbox.connect('row-selected', self._on_organizer_row_selected)
        if entries:
            for index, entry in enumerate(entries):
                row = self._make_list_row(entry['title'], entry['subtitle'])
                row.entry_payload = entry
                listbox.append(row)
                if self.selected_payload is None and index == 0:
                    self.selected_payload = entry
                    listbox.select_row(row)
        else:
            placeholder = self._label('Nothing to show for this section right now.', ['subtle-caption'], wrap=True)
            box.append(placeholder)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_child(listbox)
        box.append(scroller)

        if entries and self.selected_payload is None:
            self.selected_payload = entries[0]
        return panel

    def _build_organizer_detail_panel(self) -> Gtk.Widget:
        panel = self._make_card('panel-card')
        panel.set_hexpand(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        panel.append(box)
        box.append(self._section_title('Details'))

        payload = self.selected_payload
        if not payload:
            box.append(self._label('Select an item on the left to inspect it.', ['subtle-caption']))
            return panel

        box.append(self._label(payload['title'], weight='bold'))
        if payload.get('subtitle'):
            box.append(self._label(payload['subtitle'], ['subtle-caption'], wrap=True))

        for line in payload.get('details', []):
            box.append(self._label(line, ['subtle-caption'], wrap=True))

        action_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        for label, callback in payload.get('actions', []):
            action_row.append(self._button(label, callback))
        if action_row.get_first_child():
            box.append(action_row)

        return panel

    def _build_wallpaper_page(self) -> Gtk.Widget:
        clamp = Adw.Clamp(maximum_size=1140)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, margin_top=24, margin_bottom=32, margin_start=24, margin_end=24)
        clamp.set_child(outer)

        status = wallpaper.detect_backend()
        metadata = wallpaper.probe_selected_video()

        hero = self._make_card('panel-card')
        hero_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hero.append(hero_box)
        hero_box.append(self._section_title('Motion wallpaper'))
        hero_box.append(self._label(
            'Choose the video here, inspect the actual file metadata, and then hand off to the wallpaper backend. The app should make the decision and verification clear before launch.',
            wrap=True,
        ))
        hero_box.append(self._label(status.detail, ['subtle-caption'], wrap=True))
        outer.append(hero)

        top_metrics = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        top_metrics.append(self._metric_static('Backend', status.backend_name))
        top_metrics.append(self._metric_static('Availability', 'Ready' if status.available else 'Needs install'))
        top_metrics.append(self._metric_static('Selected video', metadata.path.name if metadata else 'None'))
        outer.append(top_metrics)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
        content.append(self._build_wallpaper_selection_panel(status, metadata))
        content.append(self._build_wallpaper_detail_panel(status, metadata))
        outer.append(content)

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

    def _build_wallpaper_selection_panel(self, status, metadata) -> Gtk.Widget:
        panel = self._make_card('panel-card')
        panel.set_size_request(420, -1)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        panel.append(box)
        box.append(self._section_title('Select wallpaper video'))
        box.append(self._label(
            'This app stores the chosen file, shows its properties, and then launches the wallpaper backend. It does not fake a native GNOME wallpaper API.',
            ['subtle-caption'],
            wrap=True,
        ))

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        controls.append(self._button('Choose video', self._choose_video, suggested=True))
        if metadata:
            controls.append(self._button('Clear selection', self._clear_video_selection))
            controls.append(self._button('Open video folder', self._open_video_folder))
        box.append(controls)

        if not status.available:
            install_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            install_row.append(self._label('Backend install command', weight='bold'))
            install_row.append(self._label(status.install_command, ['subtle-caption'], wrap=True))
            install_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            install_actions.append(self._button('Copy install command', self._copy_backend_install_command))
            box.append(install_row)
            box.append(install_actions)

        if metadata:
            box.append(self._label(f'Selected file: {metadata.path.name}', weight='bold'))
            box.append(self._label(str(metadata.path), ['subtle-caption'], wrap=True))
        else:
            box.append(self._label('No wallpaper video selected yet.', ['subtle-caption']))
        return panel

    def _build_wallpaper_detail_panel(self, status, metadata) -> Gtk.Widget:
        panel = self._make_card('panel-card')
        panel.set_hexpand(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        panel.append(box)
        box.append(self._section_title('Video details'))

        if metadata:
            dimensions = f'{metadata.width} × {metadata.height}' if metadata.width and metadata.height else 'Unknown'
            duration = self._format_duration(metadata.duration_seconds)
            frame_rate = f'{metadata.frame_rate:.2f} fps' if metadata.frame_rate else 'Unknown'
            codec = metadata.codec or 'Unknown'
            size = organizer.human_size(metadata.size_bytes)
            for title, value in [
                ('Dimensions', dimensions),
                ('Duration', duration),
                ('Frame rate', frame_rate),
                ('Codec', codec),
                ('File size', size),
            ]:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                title_label = self._label(title, weight='bold')
                title_label.set_size_request(120, -1)
                row.append(title_label)
                row.append(self._label(value, ['subtle-caption'], wrap=True))
                box.append(row)
        else:
            box.append(self._label('Choose a video to inspect its dimensions, duration, codec, and size before you use it.', ['subtle-caption'], wrap=True))

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        actions.append(self._button('Launch wallpaper backend', self._launch_wallpaper_backend, suggested=status.available))
        if metadata:
            actions.append(self._button('Refresh metadata', self._refresh_wallpaper_page))
        box.append(actions)

        return panel

    def _wrap_page(self, child: Gtk.Widget) -> Gtk.Widget:
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_child(child)
        return scroller

    def _organizer_entries(self) -> list[dict]:
        if self.organizer_section == 'suggestions':
            return [
                {
                    'title': suggestion.title,
                    'subtitle': suggestion.emphasis or suggestion.body,
                    'details': [suggestion.body, suggestion.emphasis] if suggestion.emphasis else [suggestion.body],
                    'actions': [('Open section', lambda _btn, key=suggestion.key: self._jump_to_section(self._section_for_suggestion(key)))],
                }
                for suggestion in self.report.suggestions
            ]
        if self.organizer_section == 'stale':
            return [self._item_entry(item, [('Archive stale items', self._archive_stale)]) for item in self.report.stale_items]
        if self.organizer_section == 'large':
            return [self._item_entry(item, [('Open Desktop', self._open_desktop)]) for item in self.report.large_files]
        if self.organizer_section == 'empty':
            return [self._item_entry(item, [('Trash empty folders', self._trash_empty_folders)]) for item in self.report.empty_folders]
        if self.organizer_section == 'grouping':
            entries = []
            for category, items in self.report.grouping_plan.items():
                entries.append({
                    'title': category,
                    'subtitle': f'{len(items)} loose files ready to move',
                    'details': [item.path.name for item in items[:12]],
                    'actions': [('Group loose files', self._group_now)],
                })
            return entries
        if self.organizer_section == 'duplicates':
            entries = []
            for index, group in enumerate(self.report.duplicate_files, start=1):
                entries.append({
                    'title': f'Duplicate set {index}',
                    'subtitle': f'{len(group)} identical files',
                    'details': [f'{item.path.name} · {organizer.human_size(item.size_bytes)}' for item in group],
                    'actions': [('Open Desktop', self._open_desktop)],
                })
            return entries
        return []

    def _item_entry(self, item: organizer.DesktopItem, actions: list[tuple[str, callable]]) -> dict:
        subtitle = f'{item.category} · {item.age_days} days old'
        if not item.is_dir:
            subtitle += f' · {organizer.human_size(item.size_bytes)}'
        return {
            'title': item.path.name,
            'subtitle': subtitle,
            'details': organizer.describe_item(item),
            'actions': actions,
        }

    def _make_list_row(self, title: str, subtitle: str | None = None) -> Gtk.ListBoxRow:
        row = Gtk.ListBoxRow()
        row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin_top=12, margin_bottom=12, margin_start=12, margin_end=12)
        row.set_child(row_box)
        row_box.append(self._label(title, weight='bold'))
        if subtitle:
            row_box.append(self._label(subtitle, ['subtle-caption'], wrap=True))
        return row

    def _on_organizer_row_selected(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        if self._building_views:
            return
        self.selected_payload = getattr(row, 'entry_payload', None) if row else None
        self._rebuild_views()
        self.view_stack.set_visible_child_name('organizer')

    def _metric_button(self, label: str, value: str, callback) -> Gtk.Widget:
        button = Gtk.Button()
        button.add_css_class('flat')
        card = self._metric_static(label, value)
        button.set_child(card)
        button.connect('clicked', callback)
        return button

    def _metric_static(self, label: str, value: str) -> Gtk.Widget:
        card = self._make_card('metric-card')
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        card.append(box)
        box.append(self._label(value, ['metric-number']))
        box.append(self._label(label, ['metric-label']))
        return card

    def _filter_button(self, section: str) -> Gtk.Widget:
        button = Gtk.Button(label=SECTION_TITLES[section])
        if section == self.organizer_section:
            button.add_css_class('suggested-action')
        button.connect('clicked', lambda _btn, section_name=section: self._set_organizer_section(section_name))
        return button

    def _set_organizer_section(self, section: str) -> None:
        self.organizer_section = section
        self.selected_payload = None
        self._rebuild_views()
        self.view_stack.set_visible_child_name('organizer')

    def _jump_to_section(self, section: str) -> None:
        self._set_organizer_section(section)

    def _section_for_suggestion(self, key: str) -> str:
        return {
            'group': 'grouping',
            'archive': 'stale',
            'large': 'large',
            'duplicates': 'duplicates',
            'empty': 'empty',
        }.get(key, 'suggestions')

    def _make_card(self, css_class: str) -> Gtk.Widget:
        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        frame.add_css_class(css_class)
        return frame

    def _section_title(self, text: str) -> Gtk.Widget:
        return self._label(text, classes=['section-title'], weight='bold')

    def _label(self, text: str, classes: list[str] | None = None, wrap: bool = False, weight: str | None = None) -> Gtk.Widget:
        label = Gtk.Label(label=text or '', xalign=0)
        label.set_wrap(wrap)
        label.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        label.add_css_class('body-text')
        if weight == 'bold':
            label.set_markup(f'<b>{GLib.markup_escape_text(text or "")}</b>')
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

    def _refresh_report(self, _button: Gtk.Button | None = None) -> None:
        self.report = organizer.build_report(organizer.scan_desktop())
        self.selected_payload = None
        self._rebuild_views()
        self.view_stack.set_visible_child_name('organizer')
        self._show_message('Desktop scan refreshed.')

    def _refresh_wallpaper_page(self, _button: Gtk.Button | None = None) -> None:
        self._rebuild_views()
        self.view_stack.set_visible_child_name('wallpaper')
        self._show_message('Wallpaper metadata refreshed.')

    def _group_now(self, _button: Gtk.Button | None = None) -> None:
        moved = organizer.group_loose_files(self.report)
        self.report = organizer.build_report(organizer.scan_desktop())
        self.selected_payload = None
        self._rebuild_views()
        self.view_stack.set_visible_child_name('organizer')
        self._show_message(f'Grouped {len(moved)} files.' if moved else 'Nothing needed grouping.')

    def _archive_stale(self, _button: Gtk.Button | None = None) -> None:
        moved = organizer.archive_stale_items(self.report)
        self.report = organizer.build_report(organizer.scan_desktop())
        self.selected_payload = None
        self._rebuild_views()
        self.view_stack.set_visible_child_name('organizer')
        self._show_message(f'Archived {len(moved)} items.' if moved else 'No stale items to archive.')

    def _trash_empty_folders(self, _button: Gtk.Button | None = None) -> None:
        trashed = organizer.trash_empty_folders(self.report)
        self.report = organizer.build_report(organizer.scan_desktop())
        self.selected_payload = None
        self._rebuild_views()
        self.view_stack.set_visible_child_name('organizer')
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
        file_filter.add_pattern('*.webm')
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
        self.view_stack.set_visible_child_name('wallpaper')
        self._show_message(f'Selected video: {path.name}')

    def _clear_video_selection(self, _button: Gtk.Button) -> None:
        wallpaper.clear_selected_video()
        self._rebuild_views()
        self.view_stack.set_visible_child_name('wallpaper')
        self._show_message('Cleared selected wallpaper video.')

    def _launch_wallpaper_backend(self, _button: Gtk.Button | None = None) -> None:
        ok, message = wallpaper.launch_backend()
        self._show_message(message if ok else f'Backend not available. Install with: {message}')

    def _open_video_folder(self, _button: Gtk.Button | None = None) -> None:
        ok, message = wallpaper.open_selected_video_folder()
        self._show_message(message)

    def _copy_backend_install_command(self, _button: Gtk.Button | None = None) -> None:
        command = wallpaper.detect_backend().install_command
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(command)
        self._show_message('Copied backend install command.')

    def _install_extension(self, _button: Gtk.Button | None = None) -> None:
        subprocess.Popen([str(INSTALL_SCRIPT)])
        self._show_message('Started extension install/update script in the background.')

    def _open_extension_prefs(self, _button: Gtk.Button | None = None) -> None:
        subprocess.Popen(['gnome-extensions', 'prefs', EXTENSION_UUID])

    def _extension_status_text(self) -> str:
        result = subprocess.run(['gnome-extensions', 'info', EXTENSION_UUID], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else 'The translucent folders extension is not currently installed in this GNOME session.'

    def _show_message(self, message: str) -> None:
        self.toast_overlay.add_toast(Adw.Toast(title=message))

    def _format_duration(self, seconds: float | None) -> str:
        if seconds is None:
            return 'Unknown'
        total_seconds = int(seconds)
        minutes, sec = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f'{hours:d}:{minutes:02d}:{sec:02d}'
        return f'{minutes:d}:{sec:02d}'
