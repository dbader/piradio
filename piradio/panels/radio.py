import logging
import json
import piradio.fonts as fonts
import piradio.ui as ui
import piradio.commons as commons
from . import base

GLYPH_PLAYING = '0'


class RadioPanel(base.Panel):
    def __init__(self, audio_service, clock_service):
        super(RadioPanel, self).__init__()
        self.font = fonts.get('tempesta', 8)
        self.glyph_font = fonts.get('pixarrows', 10)
        self.stations = json.loads(open('stations.json').read())
        self.cy = 0
        self.currstation = ''
        self.timeofday = clock_service.timeofday()
        self.audio_service = audio_service
        clock_service.subscribe(clock_service.TIME_CHANGED_EVENT,
                                self.on_time_changed)

    def on_time_changed(self, timeofday):
        self.timeofday = timeofday
        self.set_needs_repaint()

    def paint(self, surface):
        # Clear the surface
        surface.fill(0)

        # If necessary, draw the 'playing' icon and the
        # current station's name.
        if self.currstation:
            surface.text(self.glyph_font, -3, 0, GLYPH_PLAYING)
            surface.text(self.font, 7, 2, self.currstation)

        # Draw the clock
        clock_width, _, _ = self.font.text_dimensions(self.timeofday)
        surface.text(self.font, surface.width - clock_width, 2, self.timeofday)

        # Draw separator between the 'status area' and the station selector
        surface.hline(11)

        # Draw the station selector
        ui.render_list(surface, 2, 14, self.font, self.stations.keys(),
                       self.cy, minheight=12, maxvisible=4)

    def up_pressed(self):
        self.cy -= 1
        self.cy = commons.clamp(self.cy, 0, len(self.stations) - 1)
        self.set_needs_repaint()

    def down_pressed(self):
        self.cy += 1
        self.cy = commons.clamp(self.cy, 0, len(self.stations) - 1)
        self.set_needs_repaint()

    def center_pressed(self):
        if self.currstation == self.stations.keys()[self.cy]:
            self.audio_service.stop_playback()
            self.currstation = ''
        else:
            logging.debug('Switching station')
            self.audio_service.playstream(self.stations.values()[self.cy])
            self.currstation = self.stations.keys()[self.cy]
        self.set_needs_repaint()
