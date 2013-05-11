import base
import logging
from .. import fonts
from .. import graphics
from .. import ui
from ..services import mvg


class PublicTransportPanel(base.Panel):
    def __init__(self, station):
        self.station = station
        self.font = fonts.get('tempesta', 8)
        self.refresh()

    def refresh(self):
        logging.info('Getting public transport data for station %s', self.station)
        self.upcoming_trains = mvg.get_upcoming_trains(self.station)

    def update(self):
        pass

    def paint(self, framebuffer):
        def format_train(t):
            return '%s %s %s' % (str(t['minutes']).rjust(2, ' '), t['line'].rjust(3, ' '), t['destination'][:16])
        framebuffer.fill(0)
        framebuffer.fillrect(0, 0, framebuffer.width, 10)
        framebuffer.center_text(self.font, self.station, y=0, rop=graphics.rop_xor)
        framebuffer.hline(11)
        trains = map(format_train, self.upcoming_trains[:5])
        ui.render_static_list(framebuffer, 2, 14, self.font, trains, minheight=12)

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def center_pressed(self):
        self.refresh()
        self.needs_redraw = True
