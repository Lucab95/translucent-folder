/* Desktop Icons GNOME Shell extension
 *
 * Copyright (C) 2019 Sergio Costas (rastersoft@gmail.com)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
'use strict';
import Gio from 'gi://Gio';
import Gtk from 'gi://Gtk';
import Adw from 'gi://Adw';

import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

const TRANSLUCENT_FOLDERS_SCHEMA = 'org.gnome.shell.extensions.translucent-folders';

export default class DingPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings(TRANSLUCENT_FOLDERS_SCHEMA);

        const page = new Adw.PreferencesPage();
        const previewGroup = new Adw.PreferencesGroup({
            title: 'Folder Preview',
            description: 'Settings for the Translucent Folders preview tile and popover.',
        });

        const itemCountRow = new Adw.ActionRow({
            title: 'Preview items shown',
            subtitle: 'Controls how many items appear in the closed folder tile and expanded preview.',
        });
        const itemCountAdjustment = new Gtk.Adjustment({
            lower: 1,
            upper: 9,
            step_increment: 1,
            page_increment: 1,
            value: settings.get_int('folder-preview-tile-items'),
        });
        const itemCountSpin = new Gtk.SpinButton({
            adjustment: itemCountAdjustment,
            valign: Gtk.Align.CENTER,
            digits: 0,
            numeric: true,
        });
        itemCountSpin.connect('value-changed', widget => {
            settings.set_int('folder-preview-tile-items', widget.get_value_as_int());
        });
        settings.connect('changed::folder-preview-tile-items', () => {
            const current = settings.get_int('folder-preview-tile-items');
            if (itemCountSpin.get_value_as_int() !== current) {
                itemCountSpin.set_value(current);
            }
        });
        itemCountRow.add_suffix(itemCountSpin);
        itemCountRow.activatable_widget = itemCountSpin;
        previewGroup.add(itemCountRow);

        const labelsRow = new Adw.ActionRow({
            title: 'Show item names',
            subtitle: 'Shows labels in the expanded folder preview.',
        });
        const labelsSwitch = new Gtk.Switch({
            valign: Gtk.Align.CENTER,
        });
        settings.bind('folder-preview-show-item-labels', labelsSwitch, 'active', Gio.SettingsBindFlags.DEFAULT);
        labelsRow.add_suffix(labelsSwitch);
        labelsRow.activatable_widget = labelsSwitch;
        previewGroup.add(labelsRow);

        const tileSizeRow = new Adw.ActionRow({
            title: 'Folder tile size',
            subtitle: 'Preferred folder tile size in pixels.',
        });
        const tileSizeAdjustment = new Gtk.Adjustment({
            lower: 48,
            upper: 120,
            step_increment: 4,
            page_increment: 4,
            value: settings.get_int('folder-preview-tile-size'),
        });
        const tileSizeSpin = new Gtk.SpinButton({
            adjustment: tileSizeAdjustment,
            valign: Gtk.Align.CENTER,
            digits: 0,
            numeric: true,
        });
        tileSizeSpin.connect('value-changed', widget => {
            settings.set_int('folder-preview-tile-size', widget.get_value_as_int());
        });
        settings.connect('changed::folder-preview-tile-size', () => {
            const current = settings.get_int('folder-preview-tile-size');
            if (tileSizeSpin.get_value_as_int() !== current) {
                tileSizeSpin.set_value(current);
            }
        });
        tileSizeRow.add_suffix(tileSizeSpin);
        tileSizeRow.activatable_widget = tileSizeSpin;
        previewGroup.add(tileSizeRow);

        const dingGroup = new Adw.PreferencesGroup({
            title: 'Desktop Settings',
            description: 'Open the DING settings window for general desktop icon and Nautilus options.',
        });

        const dingSettingsRow = new Adw.ActionRow({
            title: 'Open DING desktop settings',
            subtitle: 'Use this for desktop icon size, placement, and Nautilus-shared options.',
        });
        const dingSettingsButton = new Gtk.Button({
            label: 'Open',
            valign: Gtk.Align.CENTER,
        });
        dingSettingsButton.connect('clicked', () => {
            try {
                const mainAppControl = Gio.DBusActionGroup.get(
                    Gio.DBus.session,
                    'com.rastersoft.ding',
                    '/com/rastersoft/ding'
                );
                mainAppControl.activate_action('changeDesktopIconSettings', null);
            } catch (error) {
                logError(error, 'Failed to open DING settings');
            }
        });
        dingSettingsRow.add_suffix(dingSettingsButton);
        dingSettingsRow.activatable_widget = dingSettingsButton;
        dingGroup.add(dingSettingsRow);

        page.add(previewGroup);
        page.add(dingGroup);
        window.add(page);
    }
}
