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

from gi.repository import Gtk, Gdk

from eolie.pages_manager_child import PagesManagerChild
from eolie.utils import get_safe_netloc
from eolie.logger import Logger


class PagesManagerBox(Gtk.EventBox):
    """
        Box linked to a Gtk.Stack
    """

    def __init__(self, window):
        """
            Init stack
            @param window as Window
        """
        Gtk.EventBox.__init__(self)
        self.__window = window
        self.__hovered_child = None
        self.__current_child = None
        # Sort pages by netloc
        self.__sort_pages = []
        self.__allow_left_right_in_entry = False
        self.get_style_context().add_class("sidebar")
        grid = Gtk.Grid()
        grid.set_orientation(Gtk.Orientation.VERTICAL)
        grid.show()
        self.__search_entry = Gtk.SearchEntry.new()
        self.__search_entry.connect("search-changed", self.__on_search_changed)
        self.__search_entry.connect("key-press-event",
                                    self.__on_search_key_press)
        self.__search_entry.connect("button-press-event",
                                    self.__on_search_button_press)
        self.__search_entry.show()
        self.__search_bar = Gtk.SearchBar.new()
        self.__search_bar.add(self.__search_entry)
        self.__scrolled = Gtk.ScrolledWindow()
        self.__scrolled.set_vexpand(True)
        self.__scrolled.set_hexpand(True)
        self.__scrolled.show()
        viewport = Gtk.Viewport()
        viewport.show()
        self.__scrolled.add(viewport)
        self.set_hexpand(False)

        self.__box = Gtk.FlowBox.new()
        self.__box.set_activate_on_single_click(True)
        self.__box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.__box.set_max_children_per_line(1000)
        self.__box.set_filter_func(self.__filter_func)
        self.__box.set_sort_func(self.__sort_func)
        self.__box.show()
        self.__box.connect("child-activated", self._on_child_activated)
        viewport.set_property("valign", Gtk.Align.START)
        viewport.add(self.__box)
        grid.add(self.__scrolled)
        grid.add(self.__search_bar)
        self.add(grid)
        self.__event_controller = Gtk.EventControllerMotion.new(self.__box)
        self.__event_controller.connect("motion", self.__on_box_motion)

    def add_webview(self, webview):
        """
            Add webview to pages manager
            @param view as View
            @return child
        """
        child = PagesManagerChild(webview, self.__window)
        child.show()
        self.__box.add(child)
        return child

    def remove_webview(self, webview):
        """
            Remove view from pages manager
        """
        for child in self.__box.get_children():
            if child.webview == webview:
                child.destroy()
                break

    def update_visible_child(self, visible=None):
        """
            Mark current child or visible if passed as arg
            Unmark all others
            @param visible as WebView
        """
        if visible is None:
            visible = self.__window.container.webview
        for child in self.__box.get_children():
            style_context = child.get_style_context()
            if child.webview == visible:
                child.set_state_flags(Gtk.StateFlags.VISITED, False)
                self.__current_child = child
            else:
                child.unset_state_flags(Gtk.StateFlags.VISITED)
                style_context.remove_class("item-selected")

    def update_shown_state(self, webview):
        """
            Update shown state for webview
            @param webview as WebView
        """
        for child in self.__box.get_children():
            if child.webview == webview:
                child.indicator_label.mark(webview)
                return

    def search_grab_focus(self):
        """
            Grab focus on search entry
        """
        self.__search_entry.grab_focus()

    def update_sort(self, sort=[]):
        """
            Reset sort
            @param group as [str]
        """
        self.__sort_pages = sort
        self.__box.invalidate_sort()

    def set_filter(self, search):
        """
            Filter webview
            @param search as str
        """
        self.__search_entry.set_text(search)
        self.__box.invalidate_filter()

    def set_filtered(self, b):
        """
            Show filtering widget
            @param b as bool
        """
        if b and not self.__search_bar.is_visible():
            self.__search_bar.show()
            self.__search_entry.grab_focus()
        elif self.__search_bar.is_visible():
            self.__search_bar.hide()
        self.__search_bar.set_search_mode(b)

    def next(self, switch=True):
        """
            Show next webview
            @param switch as bool
        """
        children = self.__box.get_children()
        if not children:
            return
        # Search for next child
        count = len(children)
        current_index = self.__current_child.get_index()
        wanted_index = current_index + 1
        if wanted_index >= count:
            wanted_index = 0
        child = self.__box.get_child_at_index(wanted_index)
        if switch:
            self.__window.container.set_visible_webview(child.webview)
        else:
            self.update_visible_child(child.webview)

    def previous(self, switch=True):
        """
            Show previous webview
            @param switch as bool
        """
        children = self.__box.get_children()
        if not children:
            return
        # Search for next child
        count = len(children)
        current_index = self.__current_child.get_index()
        wanted_index = current_index - 1
        if wanted_index < 0:
            wanted_index = count - 1
        child = self.__box.get_child_at_index(wanted_index)
        if switch:
            self.__window.container.set_visible_webview(child.webview)
        else:
            self.update_visible_child(child.webview)

    @property
    def filter(self):
        """
            Get filter
            @return str
        """
        return self.__search_entry.get_text()

    @property
    def filtered(self):
        """
            True if filtered
            @return bool
        """
        return self.__search_bar.get_search_mode()

    @property
    def children(self):
        """
            Get children ordered
            @return [PagesManagerChild]
        """
        return self.__box.get_children()

#######################
# PROTECTED           #
#######################
    def _on_child_activated(self, flowbox, child):
        """
            Show wanted webview
            @param flowbox as Gtk.FlowBox
            @param child as PagesManagerChild
        """
        self.__window.close_popovers()
        self.__window.container.set_visible_webview(child.webview)
        self.__window.container.set_expose(False)

#######################
# PRIVATE             #
#######################
    def __get_column_count(self):
        """
            Calculate column count
            @return int
        """
        count = 0
        current_y = None
        for child in self.__box.get_children():
            (x, y) = child.translate_coordinates(self.__box, 0, 0)
            if current_y is not None and current_y != y:
                break
            current_y = y
            count += 1
        return count

    def __get_index(self, webview):
        """
            Get webview index
            @param webview as WebView
            @return int
        """
        # Search current index
        children = self.__box.get_children()
        index = 0
        for child in children:
            if child.webview == webview:
                break
            index += 1
        return index

    def __sort_func(self, row1, row2):
        """
            Sort listbox
            @param row1 as Row
            @param row2 as Row
        """
        try:
            # Group pages by net location then atime
            if self.__sort_pages and row2.webview.uri is not None and\
                    row1.webview.uri is not None:
                netloc1 = get_safe_netloc(row1.webview.uri)
                netloc2 = get_safe_netloc(row2.webview.uri)
                if netloc1 != netloc2 and netloc1 in self.__sort_pages and\
                        netloc2 in self.__sort_pages:
                    index1 = self.__sort_pages.index(netloc1)
                    index2 = self.__sort_pages.index(netloc2)
                    return index2 < index1
                else:
                    return row2.webview.atime > row1.webview.atime
            # Always show current first
            elif self.__current_child is not None and\
                    self.__current_child in [row1, row2]:
                return self.__current_child == row2
            # Unshown first
            elif not row2.webview.shown and row1.webview.shown:
                return True
            else:
                return row2.webview.atime > row1.webview.atime
        except Exception as e:
            Logger.error("PagesManager::__sort_func(): %s", e)

    def __filter_func(self, row):
        """
            Filter list based on current filter
            @param row as Row
        """
        filter = self.__search_entry.get_text()
        if not filter:
            return True
        uri = row.webview.uri
        title = row.webview.title
        if (uri is not None and uri.find(filter) != -1) or\
                (title is not None and title.find(filter) != -1) or\
                (filter == "private://" and row.webview.ephemeral):
            return True
        return False

    def __unselect_selected(self):
        """
            Unselect selected child
        """
        if self.__hovered_child is not None:
            self.__hovered_child.unset_state_flags(
                Gtk.StateFlags.PRELIGHT)
            self.__hovered_child = None

    def __on_box_motion(self, event_controller, x, y):
        """
            Update current selected child
            @param event_controller as Gtk.EventControllerMotion
            @param x as int
            @param y as int
        """
        child = self.__box.get_child_at_pos(x, y)
        if child == self.__hovered_child:
            return
        elif child is not None:
            child.set_state_flags(Gtk.StateFlags.PRELIGHT, False)
            self.__unselect_selected()
            self.__hovered_child = child
        else:
            self.__unselect_selected()

    def __on_search_changed(self, entry):
        """
            Update filter
            @param entry as Gtk.Entry
        """
        self.__box.invalidate_filter()

    def __on_search_button_press(self, entry, event):
        """
            Allow user to use <- and -> in entry
            @param entry as Gtk.Entry
            @param event as Gdk.EventButton
        """
        self.__allow_left_right_in_entry = True

    def __on_search_key_press(self, entry, event):
        """
            Forward event to self if event is <- or -> and entry is empty
            @param entry as Gtk.Entry
            @param event as Gdk.EventKey
        """
        if event.keyval == Gdk.KEY_Left and\
                not self.__allow_left_right_in_entry:
            self.previous(False)
            return True
        elif event.keyval == Gdk.KEY_Right and\
                not self.__allow_left_right_in_entry:
            self.next(False)
            return True
        elif event.keyval in [Gdk.KEY_Down, Gdk.KEY_Up]:
            if self.__current_child is not None:
                column_count = self.__get_column_count()
                index = self.__current_child.get_index()
                if event.keyval == Gdk.KEY_Down:
                    new_index = index + column_count
                else:
                    new_index = index - column_count
                wanted_child = self.__box.get_child_at_index(new_index)
                if wanted_child is not None:
                    self.update_visible_child(wanted_child.webview)
        elif event.keyval in [Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
            if self.__current_child is not None:
                self._on_child_activated(self.__box, self.__current_child)
        elif event.keyval == Gdk.KEY_Escape:
            self.__search_entry.set_text("")
