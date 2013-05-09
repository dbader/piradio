import fontlib
import datetime
import logging
import base


class ClockPanel(base.Panel):
    def __init__(self):
        self.clock_font = fontlib.get('tempesta', 32)
        self.prev_timestr = None

    def update(self):
        self.timestr = str(datetime.datetime.now().strftime(base.CONFIG['clock_format']))
        if self.timestr != self.prev_timestr:
            self.prev_timestr = self.timestr
            logging.debug('Redrawing the clock')
            self.needs_redraw = True

    def paint(self, framebuffer):
        framebuffer.fill(0)
        framebuffer.center_text(self.clock_font, self.timestr)

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        pass
