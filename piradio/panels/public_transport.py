import base
import logging
from .. import fonts
from .. import graphics
from .. import ui
from ..services import mvg


class PublicTransportPanel(base.Panel):
    def __init__(self, **config):
        super(PublicTransportPanel, self).__init__()
        self.station = config['station']
        self.font = fonts.get('tempesta', 8)
        self.upcoming_trains = []
        self.refresh()

    def refresh(self):
        logging.info('Getting public transport data for station %s',
                     self.station)
        self.upcoming_trains = mvg.get_upcoming_trains(self.station)

    def paint(self, surface):
        def format_train(t):
            return '%s %s %s' % (str(t['minutes']).rjust(2, ' '),
                                 t['line'].rjust(3, ' '),
                                 t['destination'][:16])
        surface.fill(0)
        surface.fillrect(0, 0, surface.width, 10)
        surface.center_text(self.font, self.station, y=0, rop=graphics.rop_xor)
        surface.hline(11)
        trains = map(format_train, self.upcoming_trains[:5])
        ui.render_static_list(surface, 2, 14, self.font, trains, minheight=12)

    def center_pressed(self):
        self.refresh()
        self.set_needs_repaint()
