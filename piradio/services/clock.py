import logging
import piradio.commons as commons
from piradio.services import base


class ClockService(base.AsyncService):
    TIME_CHANGED_EVENT = 'time_changed'

    def __init__(self):
        super(ClockService, self).__init__(tick_interval=1.0)
        self.prev_timeofday = commons.timeofday()

    def timeofday(self):
        return self.prev_timeofday

    def tick(self):
        super(ClockService, self).tick()
        timeofday = commons.timeofday()
        if timeofday != self.prev_timeofday:
            logging.debug('ClockService: time changed to %s', timeofday)
            self.prev_timeofday = timeofday
            self.notify_subscribers(self.TIME_CHANGED_EVENT, timeofday)
