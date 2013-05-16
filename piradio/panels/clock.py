import piradio.fonts
import base
import piradio.services.clock


class ClockPanel(base.Panel):
    def __init__(self):
        super(ClockPanel, self).__init__()
        self.clock_font = piradio.fonts.get('tempesta', 32)
        clocksvc = piradio.services.clock.instance()
        self.timeofday = clocksvc.timeofday()
        clocksvc.subscribe(clocksvc.TIME_CHANGED_EVENT,
                           self.on_time_changed)

    def on_time_changed(self, timeofday):
        self.timeofday = timeofday
        self.set_needs_repaint()

    def paint(self, surface):
        surface.fill(0)
        surface.center_text(self.clock_font, self.timeofday)
