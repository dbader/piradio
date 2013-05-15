import logging
import piradio.fonts as fonts
from piradio.panels import base
import piradio.services.clock


class ClockPanel(base.Panel):
    def __init__(self):
        super(ClockPanel, self).__init__()
        self.clock_font = fonts.get('tempesta', 32)
        self.timeofday = 'XX:XX'

    def activate(self):
        clocksvc = piradio.services.clock.instance()
        clocksvc.subscribe(self)

    def deactivate(self):
        clocksvc = piradio.services.clock.instance()
        clocksvc.unsubscribe(self)

    def notify(self, event, payload):
        if event == piradio.services.clock.TIME_CHANGED_EVENT:
            self.timeofday = payload['time']
            self.needs_redraw = True
            logging.debug('Redrawing the clock')

    def paint(self, surface):
        surface.fill(0)
        surface.center_text(self.clock_font, self.timeofday)
