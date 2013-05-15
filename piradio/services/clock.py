import logging
from piradio.services import base
from piradio import commons


class ClockService(base.AsyncService):
    def __init__(self):
        super(ClockService, self).__init__(tick_interval=1.0)
        self.timeofday = commons.timeofday()

    def tick(self):
        super(ClockService, self).tick()
        timeofday = commons.timeofday()
        if timeofday != self.timeofday:
            logging.debug('ClockService: time changed to %s', timeofday)
            self.timeofday = timeofday
            self.notify_subscribers('time_changed', {'time': self.timeofday})

_instance = None

def instance():
    if not _instance:
        logging.info('Creating clockservice instance')
        global _instance
        _instance = ClockService()
    return _instance
