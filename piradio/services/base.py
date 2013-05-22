import threading
import Queue as queue
import inspect
import logging

# Pending notifications that should be delivered on the main thread.
notifications = queue.Queue()

logging.basicConfig(level=logging.INFO)


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
        # logging.debug('Delivering %s', self)
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
        # logging.debug('%s subscribed to %s.%s', callback,
                      # self.__class__.__name__, event)

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
        self.stop_event = threading.Event()
        self.tick_interval = tick_interval
        self.tick_thread = threading.Thread(target=self.tick_thread_main)

    def start(self):
        super(AsyncService, self).start()
        if self.is_running:
            logging.warning('%s: start() called while service '
                            'is already running', self.__class__.__name__)
            return
        self.tick_thread.start()

    def stop(self):
        super(AsyncService, self).stop()
        self.stop_event.set()
        self.tick_thread.join()

    def tick_thread_main(self):
        """Calls tick() in periodic intervals."""
        try:
            while not self.stop_event.wait(0):
                self.is_running = True
                try:
                    self.tick()
                except Exception as e:
                    logging.exception(e)
                self.stop_event.wait(self.tick_interval)
        finally:
            self.is_running = False

    def tick(self):
        pass


class ServiceBroker(object):
    def __init__(self):
        self.service_classes = {}
        self.service_instances = {}

    def register_service(self, service_class, key=None):
        key = key or service_class.__name__
        # logging.info('Registered %s -> %s', key, service_class.__name__)
        self.service_classes[key] = service_class

    def stop_running(self):
        for service in self.service_instances.values():
            service.stop()
        self.service_instances.clear()

    def get_service_instance(self, service_class):
        try:
            return self.service_instances[service_class]
        except KeyError:
            try:
                logging.info('Broker: instantiating %s', service_class)
                instance = self.service_classes[service_class]()
                self.service_instances[service_class] = instance
                return instance
            except KeyError:
                raise Exception('Unknown service key %s' % service_class)

    def instantiate(self, cls, kwargs):
        resolved_args = []
        for arg in inspect.getargspec(cls.__init__).args[1:]:
            if not arg.endswith('_service'):
                raise Exception('Cannot inject service from arg %s' % arg)
            clsname = ''.join([c.title() for c in arg.split('_')])
            # logging.debug('(%s) Injecting %s -> %s',
                          # cls.__name__, arg, clsname)
            instance = self.get_service_instance(clsname)
            resolved_args.append(instance)
        return cls(*resolved_args, **kwargs)

    def start_bound_services(self):
        for service in self.service_instances.values():
            service.start()
