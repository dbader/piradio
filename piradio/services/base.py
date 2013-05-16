import threading
import Queue as queue
import time
import logging

# Pending notifications that should be delivered on the main thread.
notifications = queue.Queue()


def deliver_pending_notifications():
    """Deliver all pending notifications.
    Make sure this is called on the main thread.
    """
    while not notifications.empty():
        msg = notifications.get()
        msg.deliver()


class Notification(object):
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return '%s(%s, %s, %s)' % (self.__class__.__name__, self.callback,
                                   self.args, self.kwargs)

    def deliver(self):
        logging.debug('Delivering %s', self)
        self.callback(*self.args, **self.kwargs)


class BaseService(object):
    """Base class for all services.
    Implements the observer pattern.
    """
    def __init__(self):
        self.subscriptions = {}

    def start(self):
        logging.info('Starting service %s', self.__class__.__name__)

    def stop(self):
        logging.info('Stopping service %s', self.__class__.__name__)

    def subscribe(self, event, callback):
        if not event in self.subscriptions:
            self.subscriptions[event] = set()
        self.subscriptions[event].add(callback)
        logging.debug('%s subscribed to %s.%s', callback,
                      self.__class__.__name__, event)

    def unsubscribe(self, callback):
        for event in self.subscriptions:
            self.subscriptions[event].remove(callback)
            logging.debug('%s unsubscribed from %s.%s',
                          callback, self.__class__.__name__, event)

    def notify_subscribers(self, event, *args, **kwargs):
        if not event in self.subscriptions:
            return
        for callback in self.subscriptions[event]:
            notifications.put(Notification(callback, *args, **kwargs))


# Fixme: should be PeriodicService, AsyncPeriodicService
class AsyncService(BaseService):
    """An asynchronous service that performs its work on a background
    thread.
    """
    def __init__(self, tick_interval=1.0):
        super(AsyncService, self).__init__()
        self.is_running = False
        self.tick_interval = tick_interval
        self.tick_thread = threading.Thread(target=self.tick_thread_main)

    def start(self):
        super(AsyncService, self).start()
        if self.is_running:
            logging.warning('%s: start() called while service '
                            'is already running', self.__class__.__name__)
            return
        self.is_running = True
        self.tick_thread.start()

    def stop(self):
        super(AsyncService, self).stop()
        self.is_running = False
        self.tick_thread.join()

    def tick_thread_main(self):
        """Calls tick() in periodic intervals."""
        while self.is_running:
            self.tick()
            time.sleep(self.tick_interval)

    def tick(self):
        pass
