# Copyright (c) 2017-2021 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gio, GLib, Gtk

from gettext import gettext as _

from eolie.define import App, LoadingType


class ApplicationMenu(Gio.Menu):
    """
        Show application menu
    """

    def __init__(self, window):
        """
            Init menu
            @param window as Window
        """
        Gio.Menu.__init__(self)
        self.__window = window
        # Main actions menu
        action = Gio.SimpleAction(name="new-private")
        App().add_action(action)
        action.connect("activate",
                       self.__on_private_clicked)
        self.append(_("New private page"), "app.new-private")

        # Blockers submenu
        blockers_menu = Gio.Menu()
        for (label, blocker) in [
                (_("Block ads"), "block-ads"),
                (_("Block popups"), "block-popups"),
                (_("Block images"), "block-images"),
                (_("Block multimedia"), "block-medias"),
                (_("Block scripts"), "block-scripts")]:
            value = App().settings.get_value(blocker)
            action = Gio.SimpleAction.new_stateful(
                blocker,
                None,
                GLib.Variant.new_boolean(value))
            App().add_action(action)
            action.connect("change-state",
                           self.__on_blocker_change_state,
                           blocker)
            blockers_menu.append(label, "app.%s" % blocker)

        self.append_submenu(_("Blockers"), blockers_menu)

        # Default application menu
        section = Gio.Menu()
        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self.__on_settings_activate)
        App().add_action(settings_action)
        section.append(_("_Preferences"), "app.settings")

        show_sidebar = App().settings.get_value("show-sidebar")
        sidebar_action = Gio.SimpleAction.new_stateful(
            "sidebar",
            None,
            GLib.Variant.new_boolean(show_sidebar))
        sidebar_action.connect("change-state", self.__on_sidebar_change_state)
        App().add_action(sidebar_action)
        section.append(_("_Sidebar"), "app.sidebar")

        value = App().settings.get_value("night-mode")
        action = Gio.SimpleAction.new_stateful(
            "night-mode",
            None,
            GLib.Variant.new_boolean(value))
        App().add_action(action)
        action.connect("change-state",
                       self.__on_night_mode_change_state)
        section.append(_("Night mode"), "app.night-mode")

        shortcuts_action = Gio.SimpleAction.new("shortcuts", None)
        shortcuts_action.connect("activate", self.__on_shortcuts_activate)
        App().add_action(shortcuts_action)
        section.append(_("_Keyboard Shortcuts"), "app.shortcuts")
        self.append_section(None, section)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.__on_about_activate)
        App().add_action(about_action)
        section.append(_("_About"), "app.about")

#######################
# PRIVATE             #
#######################
    def __on_settings_activate(self, action, param):
        """
            Show settings dialog
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        from eolie.dialog_settings import SettingsDialog
        dialog = SettingsDialog(self.__window)
        dialog.show()

    def __on_about_activate(self, action, param):
        """
            Setup about dialog
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        builder = Gtk.Builder()
        builder.add_from_resource('/org/gnome/Eolie/AboutDialog.ui')
        about = builder.get_object('about_dialog')
        about.set_transient_for(self.__window)
        about.connect("response", self.__on_about_activate_response)
        about.show()

    def __on_shortcuts_activate(self, action, param):
        """
            Show shortcuts
            @param action as Gio.SimpleAction
            @param param as GLib.Variant
        """
        builder = Gtk.Builder()
        builder.add_from_resource("/org/gnome/Eolie/Shortcuts.ui")
        shortcuts = builder.get_object("shortcuts")
        shortcuts.set_transient_for(self.__window)
        shortcuts.show()

    def __on_about_activate_response(self, dialog, response_id):
        """
            Destroy about dialog when closed
            @param dialog as Gtk.Dialog
            @param response ID as int
        """
        dialog.destroy()

    def __on_sidebar_change_state(self, action, value):
        """
            Show/hide sidebar
            @param action as Gio.SimpleAction
            @param value as bool
        """
        action.set_state(value)
        App().settings.set_value("show-sidebar", GLib.Variant("b", value))

    def __on_blocker_change_state(self, action, value, blocker):
        """
            Update blocker value
            @param action as Gio.SimpleAction
            @param value as bool
            @param blocker as str
        """
        action.set_state(value)
        App().settings.set_value(blocker, GLib.Variant("b", value))
        self.__window.container.webview.reload()

    def __on_night_mode_change_state(self, action, value):
        """
            Update night mode value
            @param action as Gio.SimpleAction
            @param value as bool
        """
        action.set_state(value)
        App().settings.set_value("night-mode", GLib.Variant("b", value))
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", value)
        for window in App().windows:
            GLib.idle_add(window.toolbar.title.entry.update_style)
            for webview in window.container.webviews:
                webview.night_mode()

    def __on_private_clicked(self, action, variant):
        """
            Add a new private view
            @param Gio.SimpleAction
            @param GVariant
        """
        App().active_window.container.add_webview_for_uri(
                                                  App().start_page,
                                                  LoadingType.FOREGROUND,
                                                  True)
