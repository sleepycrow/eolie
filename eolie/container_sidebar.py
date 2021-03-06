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

from gi.repository import Gtk, GLib

from eolie.sites_manager import SitesManager
from eolie.define import App


class SidebarContainer:
    """
        Sidebar management for container
    """

    def __init__(self):
        """
            Init container
        """
        self.__sites_manager = SitesManager(self._window)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        position = App().settings.get_value("sidebar-position").get_int32()
        self.set_position(position)
        self.__sites_manager.show_labels(position > 60)
        self.connect("notify::position", self.__on_paned_notify_position)
        self.pack1(self.__sites_manager, False, False)
        if App().settings.get_value("show-sidebar"):
            self.__sites_manager.show()
        App().settings.connect("changed::show-sidebar",
                               self.__on_show_sidebar_changed)

    @property
    def sites_manager(self):
        """
            Get sites manager
            @return SitesManager
        """
        return self.__sites_manager

#######################
# PRIVATE             #
#######################
    def __on_paned_notify_position(self, paned, ignore):
        """
            Save position
            @param paned as Gtk.Paned
            @param ignore as GParamInt
        """
        position = paned.get_position()
        App().settings.set_value("sidebar-position",
                                 GLib.Variant("i", position))
        self.__sites_manager.show_labels(position > 60)

    def __on_show_sidebar_changed(self, settings, key):
        """
            Show/hide panel
            @param settings as Gio.Settings
            @param key as str
        """
        if App().settings.get_value("show-sidebar"):
            self.__sites_manager.show()
        else:
            self.__sites_manager.hide()
