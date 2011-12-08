from gi.repository import Gtk
import gst
import os
import urllib


class SongList(Gtk.ListStore):
    """ListStore representing a list of songs"""
    def __init__(self):
        """Initialize the SongList as a ListStore with Song attributes"""
        # path, artist, album, title, track
        super(SongList, self).__init__(str, str, str, str, int)


class SongListView(Gtk.TreeView):
    """TreeView representing a SongList."""
    def __init__(self):
        """Initialize the SongListView as a Treeview."""
        super(SongListView, self).__init__()
        self.set_model(SongList())
        self.set_reorderable(True)

        self.rank = None

        self.playbin = gst.element_factory_make("playbin2", "player")
        self.bus = self.playbin.get_bus()
        self.bus.add_signal_watch()

        self.bus.connect("message", self.message)
        self.connect("row-activated", self.activate)

        track_column = Gtk.TreeViewColumn("Track")
        track_column.set_resizable(True)
        track_column.set_reorderable(True)
        track_cell = Gtk.CellRendererText()
        track_column.pack_start(track_cell, True)
        track_column.add_attribute(track_cell, "text", 4)
        track_column.set_sort_column_id(4)
        self.append_column(track_column)

        title_column = Gtk.TreeViewColumn("Title")
        title_column.set_resizable(True)
        title_column.set_reorderable(True)
        title_cell = Gtk.CellRendererText()
        title_column.pack_start(title_cell, True)
        title_column.add_attribute(title_cell, "text", 3)
        title_column.set_sort_column_id(3)
        self.append_column(title_column)

        artist_column = Gtk.TreeViewColumn("Artist")
        artist_column.set_resizable(True)
        artist_column.set_reorderable(True)
        artist_cell = Gtk.CellRendererText()
        artist_column.pack_start(artist_cell, True)
        artist_column.add_attribute(artist_cell, "text", 1)
        artist_column.set_sort_column_id(1)
        self.append_column(artist_column)

        album_column = Gtk.TreeViewColumn("Album")
        album_column.set_resizable(True)
        album_column.set_reorderable(True)
        album_cell = Gtk.CellRendererText()
        album_column.pack_start(album_cell, True)
        album_column.add_attribute(album_cell, "text", 2)
        album_column.set_sort_column_id(2)
        self.append_column(album_column)

    def set_album(self, folder):
        """Set the active album."""
        self.props.model.clear()

        for item in sorted(os.listdir(folder)):
            path = os.path.join(folder, item)
            if item.endswith(".ogg"):
                item = item[:-4]
                track, title = item.split("-", 1)
                track = int(track.strip())
                title = title.strip()
                artist, album = folder.rstrip("/").split("/")[-2:]
                self.props.model.append((path, artist, album, title, track))

    def message(self, bus, message):
        """Manage message emitted by the gstreamer player."""
        if message.type == gst.MESSAGE_EOS:
            self.next()
        elif message.type == gst.MESSAGE_ERROR:
            print("GStreamer Error: %s" % message.parse_error()[1])

    def next(self):
        """Play next song corresponding to the context."""
        if self.rank == None:
            rank = 0
        else:
            rank = self.rank + 1
        self.play(rank)

    def play(self, rank=None):
        """Play music at given rank."""
        state = self.playbin.get_state()[1]
        if state == gst.STATE_PAUSED and rank == None:
            # Player is paused, resume last song
            self.playbin.set_state(gst.STATE_PLAYING)
        elif state == gst.STATE_PLAYING and rank == None:
            # Player is playing, pause
            self.playbin.set_state(gst.STATE_PAUSED)
        else:
            # Player is not paused, play new song
            self.stop()
            # No song playing, no song asked: play first
            if rank == None:
                rank = 0
            # At last play song
            if len(self.props.model) > rank >= 0:
                self.playbin.set_property(
                    "uri", "file://%s" % urllib.quote(self.props.model[rank][0]))
                self.playbin.set_state(gst.STATE_PLAYING)
                self.rank = rank
            else:
                self.rank = None

    def stop(self):
        """Stop playing music."""
        self.playbin.set_state(gst.STATE_NULL)
        self.rank = None

    def activate(self, treeview, path, view=None):
        """Activate song at path in song list."""
        self.play(rank=path.get_indices()[0])

    def set_volume(self, volume):
        """Set the player volume."""
        self.playbin.set_property("volume", volume)
