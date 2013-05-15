import weakref
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
        logging.debug('Delivering %s', msg)
        msg.receiver.notify(msg.event, msg.payload)


class Notification(object):
    def __init__(self, receiver, event, payload):
        self.receiver = receiver
        self.event = event
        self.payload = payload or {}

    def __repr__(self):
        return '%s(%s, %s, %s)' % (self.__class__.__name__,
                                   self.receiver,
                                   self.event,
                                   self.payload)


class Callback(object):
    """A weak callback that does not keep pointed-at object alive."""

    def __init__(self, method):
        self.obj_ref = weakref.ref(method.im_self)
        self.method_name = method.im_func.__name__

    def __str__(self):
        return '%s(%s.%s)' % (self.__class__.__name__,
                              self.obj_ref,
                              self.method_name)

    def __call__(self, *args, **kwargs):
        obj = self.obj_ref()
        if obj:
            method = getattr(obj, self.method_name)
            method(*args, **kwargs)
        else:
            logging.debug('%s: weakref is gone', self)


class BaseService(object):
    """Base class for all services.
    Implements the observer pattern.
    """
    def __init__(self):
        self.subscribers = weakref.WeakSet()

    def start(self):
        logging.info('Starting service %s', self.__class__.__name__)
        pass

    def stop(self):
        logging.info('Stopping service %s', self.__class__.__name__)
        pass

    def subscribe(self, client):
        self.subscribers.add(client)
        logging.debug('%s subscribed to %s', client, self)

    def unsubscribe(self, client):
        self.subscribers.remove(client)
        logging.debug('%s unsubscribed from %s', client, self)

    def notify_subscribers(self, event, payload=None):
        for each in self.subscribers:
            notifications.put(Notification(each, event, payload))


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
        self.is_running = True
        self.tick_thread.start()

    def stop(self):
        super(AsyncService, self).stop()
        self.is_running = False
        self.tick_thread.join()

    def tick_thread_main(self):
        while self.is_running:
            self.tick()
            time.sleep(self.tick_interval)

    def tick(self):
        pass
