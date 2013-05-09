import base
import fontlib
import ui
import audiolib
import commons
import datetime
import logging
import json

GLYPH_PLAYING = '0'


class RadioPanel(base.Panel):
    def __init__(self):
        self.font = fontlib.get('tempesta', 8)
        self.glyph_font = fontlib.get('pixarrows', 10)
        self.stations = json.loads(open('stations.json').read())

        self.cy = 0
        self.currstation = ''
        self.prev_timestr = ''
        self.needs_redraw = True

    def update(self):
        self.update_clock()

    def paint(self, framebuffer):
        # Clear the framebuffer
        framebuffer.fill(0)

        # If necessary, draw the 'playing' icon and the name of the current station
        if self.currstation:
            framebuffer.text(self.glyph_font, -3, 0, GLYPH_PLAYING)
            framebuffer.text(self.font, 7, 2, self.currstation)

        # Draw the clock
        w, h, baseline = self.font.text_extents(self.timestr)
        framebuffer.text(self.font, framebuffer.width - w, 2, self.timestr)

        # Draw separator between the 'status area' and the station selector
        framebuffer.hline(11)

        # Draw the station selector
        ui.render_list(framebuffer, 2, 14, self.font, self.stations.keys(), self.cy, minheight=12, maxvisible=4)

    def up_pressed(self):
        self.cy -= 1
        self.cy = commons.clamp(self.cy, 0, len(self.stations)-1)
        self.needs_redraw = True

    def down_pressed(self):
        self.cy += 1
        self.cy = commons.clamp(self.cy, 0, len(self.stations)-1)
        self.needs_redraw = True

    def center_pressed(self):
        if self.currstation == self.stations.keys()[self.cy]:
            logging.debug('Stopping playback')
            audiolib.stop()
            self.currstation = ''
        else:
            logging.debug('Switching station')
            audiolib.playstream(self.stations.values()[self.cy], fade=False)
            self.currstation = self.stations.keys()[self.cy]
        self.needs_redraw = True

    def update_clock(self):
        self.timestr = str(datetime.datetime.now().strftime(base.CONFIG['clock_format']))
        if self.timestr != self.prev_timestr:
            self.prev_timestr = self.timestr
            logging.debug('Redrawing the clock')
            self.needs_redraw = True
