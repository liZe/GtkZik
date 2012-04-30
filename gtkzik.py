#!/usr/bin/env python

from gi.repository import Gtk
import os
import sys

import songtree
import songlist


UI = """\
<ui>
 <toolbar name='ToolBar'>
   <toolitem action='Play'/>
   <toolitem action='Next'/>
 </toolbar>
</ui>
"""


class Window(Gtk.Window):
    def __init__(self):
        super(Gtk.Window, self).__init__()
        self.set_title("GtkZik")
        self.set_icon_from_file(
            os.path.join(os.path.dirname(__file__), "gtkzik.svg"))

        self.song_tree = songtree.SongTreeView()
        self.song_list = songlist.SongListView()

        self.action_group = Gtk.ActionGroup("actions")
        self.action_group.add_actions([
                ("Play", Gtk.STOCK_MEDIA_PLAY, None, None, None,
                 lambda *args: self.song_list.play()),
                ("Next", Gtk.STOCK_MEDIA_NEXT, None, None, None,
                 lambda *args: self.song_list.next())])

        self.ui_manager = Gtk.UIManager()
        self.ui_manager.add_ui_from_string(UI)
        self.ui_manager.insert_action_group(self.action_group, 1)

        self.main_box = Gtk.VBox()
        self.add(self.main_box)

        self.top_box = Gtk.HBox()
        self.main_box.pack_start(self.top_box, False, True, 0)

        self.toolbar = self.ui_manager.get_widget("/ToolBar")
        self.top_box.pack_start(self.toolbar, True, True, 0)

        self.volume = Gtk.VolumeButton()
        self.top_box.pack_start(self.volume, False, True, 0)

        self.pane = Gtk.HPaned()
        self.main_box.pack_start(self.pane, True, True, 0)

        self.artist_scroll = Gtk.ScrolledWindow()
        self.artist_scroll.set_policy(1, 1)
        self.pane.add1(self.artist_scroll)
        self.artist_scroll.add(self.song_tree)

        self.song_scroll = Gtk.ScrolledWindow()
        self.song_scroll.set_policy(1, 1)
        self.pane.add2(self.song_scroll)
        self.song_scroll.add(self.song_list)

        self.volume.connect(
            "value-changed",
            lambda button, value: self.song_list.set_volume(value))
        self.song_tree.connect("row-activated", self.activate_album)
        self.connect("destroy", lambda window: sys.exit())

        self.volume.set_value(1)

        self.show_all()
        Gtk.main()

    def activate_album(self, treeview, path, view=None):
        folder = os.path.join(*self.song_tree.props.model[path])
        self.song_list.set_album(folder)


window = Window()
