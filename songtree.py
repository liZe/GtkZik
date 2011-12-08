from gi.repository import Gtk
import os

ROOT = "/home/lize/Musique"


class SongTree(Gtk.TreeStore):
    """TreeStore representing a list of items."""
    def __init__(self):
        super(SongTree, self).__init__(str, str)


class SongTreeView(Gtk.TreeView):
    """TreeView representing a SongTree."""
    def __init__(self):
        """Initialize the SongTreeView as a TreeView."""
        super(SongTreeView, self).__init__()
        self.set_model(SongTree())
        self.set_headers_visible(False)

        pane_column = Gtk.TreeViewColumn()
        pane_cell = Gtk.CellRendererText()
        pane_column.pack_start(pane_cell, True)
        pane_column.add_attribute(pane_cell, "text", 1)
        self.append_column(pane_column)

        self.parse()

    def parse(self, parent=None):
        """Add the songs to the song tree."""
        if parent:
            folder = os.path.join(*self.props.model[parent])
        else:
            parent = self.props.model.get_iter_first()
            folder = ROOT

        for item in sorted(os.listdir(folder)):
            path = os.path.join(folder, item)
            if os.path.isdir(path) and not item.startswith("."):
                iterator = self.props.model.append(parent, (folder, item))
                self.parse(iterator)
