import logging
from piradio.services import base
from piradio import commons


class ClockService(base.AsyncService):
    TIME_CHANGED_EVENT = 'time_changed'

    def __init__(self):
        super(ClockService, self).__init__(tick_interval=1.0)
        self.timeofday = None

    def tick(self):
        super(ClockService, self).tick()
        timeofday = commons.timeofday()
        if timeofday != self.timeofday:
            logging.debug('ClockService: time changed to %s', timeofday)
            self.timeofday = timeofday
            self.notify_subscribers(self.TIME_CHANGED_EVENT, self.timeofday)

_instance = None


def instance():
    if not _instance:
        logging.info('Creating clockservice instance')
        global _instance
        _instance = ClockService()
        _instance.start()
    return _instance
