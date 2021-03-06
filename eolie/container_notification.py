# Copyright (c) 2014-2018 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
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


class ContainerNotification(Gtk.Revealer):
    """
        Show a notification to user with a button connected to an action
    """

    def __init__(self, label, button_labels, actions):
        """
            Init notification
            @param label as str
            @param button_label as [str]
            @param action as [callback]
        """
        Gtk.Revealer.__init__(self)
        widget = Gtk.Grid()
        widget.get_style_context().add_class("app-notification")
        widget.set_column_spacing(5)
        widget.add(Gtk.Label.new(label))
        for i in range(0, len(button_labels)):
            button = Gtk.Button.new()
            button.set_label(button_labels[i])
            button.connect("clicked", self.__on_button_clicked, actions[i])
            widget.add(button)
        button = Gtk.Button.new_from_icon_name("window-close-symbolic",
                                               Gtk.IconSize.BUTTON)
        button.connect("clicked", self.__on_button_clicked, None)
        button.set_relief(Gtk.ReliefStyle.NONE)
        widget.add(button)
        widget.show_all()
        self.add(widget)
        self.set_property("halign", Gtk.Align.CENTER)
        self.set_property("valign", Gtk.Align.START)

#######################
# PRIVATE             #
#######################
    def __on_button_clicked(self, button, action=None):
        """
            Execute action
            @param button as Gtk.Button
            @param action as callback
        """
        self.set_reveal_child(False)
        GLib.timeout_add(1000, self.destroy)
        if action is not None:
            action()
