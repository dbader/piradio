import piradio.fonts as fonts
import piradio.graphics as graphics
import piradio.ui as ui
from . import base


class PublicTransportPanel(base.Panel):
    def __init__(self, public_transport_service, **config):
        super(PublicTransportPanel, self).__init__()
        self.station = config['station']
        self.font = fonts.get('tempesta', 8)
        self.upcoming_trains = []
        self.svc = public_transport_service
        self.svc.subscribe(self.station, self.on_trains_changed)

    def on_trains_changed(self, trains):
        self.upcoming_trains = trains

    def paint(self, surface):
        def format_train(t):
            return '%s %s %s' % (str(t['minutes']).rjust(2, ' '),
                                 t['line'].rjust(3, ' '),
                                 t['destination'][:16])
        surface.fill(0)
        surface.fillrect(0, 0, surface.width, 10)
        surface.center_text(self.font, self.station, y=0, rop=graphics.rop_xor)
        surface.hline(11)
        if self.upcoming_trains:
            trains = map(format_train, self.upcoming_trains[:5])
            ui.render_static_list(surface, 2, 14, self.font,
                                  trains, minheight=12)

    def center_pressed(self):
        self.set_needs_repaint()
