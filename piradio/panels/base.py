from piradio.config import CONFIG


class Panel(object):
    """Base class for all panels.
    Panels control the whole display area and receive input events from
    the UP, DOWN, and CENTER buttons. The LEFT and RIGHT buttons are
    used for switching between panels.
    """
    def __init__(self):
        self.needs_repaint = True

    def activate(self):
        """Called when the panel enters the foreground."""
        pass

    def deactivate(self):
        """Called when the panel leaves the foreground."""
        pass

    def update(self):
        """Called at a variable refresh rate (usually 60 Hz).
        Use this to update the panels internal state and
        to trigger repaints.
        """
        pass

    #pylint: disable=W0613
    def paint(self, surface):
        """Called whenever the panel should paint its contents.
        `surface` is the graphics.Surface the panel should paint to.
        A panel needs to paint its contents if its `needs_repaint`
        property is True.
        """
        self.needs_repaint = False

    def up_pressed(self):
        """The UP button was pressed."""
        pass

    def down_pressed(self):
        """The DOWN button was pressed."""
        pass

    def center_pressed(self):
        """The CENTER button was pressed."""
        pass

    def set_needs_repaint(self):
        self.needs_repaint = True

    def paint_if_needed(self, surface):
        if not self.needs_repaint:
            return False
        self.paint(surface)
        self.needs_repaint = False
        return True
