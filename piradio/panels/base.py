import json

CONFIG = json.loads(open('config.json').read())


class Panel(object):
    """Base class for all panels.
    Panels control the whole display area and receive input events from the UP, DOWN, and
    CENTER buttons. The LEFT and RIGHT buttons are used for switching between panels.
    """
    def __init__(self):
        self.needs_redraw = False

    def update(self):
        """Called at a variable refresh rate (usually 60 Hz).
        Use this to update the panels internal state and to trigger redraws.
        """
        pass

    def paint(self, surface):
        """Called whenever the panel should paint its contents.
        `surface` is the graphics.Surface the panel should paint to.
        A panel needs to paint its contents if its `needs_redraw` property is True.
        """
        pass

    def up_pressed(self):
        """The UP button was pressed."""
        pass

    def down_pressed(self):
        """The DOWN button was pressed."""
        pass

    def center_pressed(self):
        """The CENTER button was pressed."""
        pass
