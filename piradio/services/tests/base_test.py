import mock
import time
from ..base import (BaseService, Callback, AsyncService, ServiceManager,
                    deliver_pending_notifications)


def test_subscriptions():
    svc = BaseService()
    client = mock.Mock()
    svc.subscribe(client)

    svc.notify_subscribers('foo', {'magic': 23})
    deliver_pending_notifications()
    client.notify.assert_called_once_with('foo', {'magic': 23})

    client.reset_mock()
    svc.notify_subscribers('bar')
    deliver_pending_notifications()
    client.notify.assert_called_once_with('bar', {})


def test_unsubscribe():
    svc = BaseService()
    client = mock.Mock()
    svc.subscribe(client)

    svc.notify_subscribers('foo')
    deliver_pending_notifications()
    client.notify.assert_called_once_with('foo', {})

    client.reset_mock()
    svc.unsubscribe(client)
    svc.notify_subscribers('bar')
    deliver_pending_notifications()
    client.notify.assert_not_called()
    assert not client.notify.called


def test_callback():
    class MockClass(object):
        def func(self, param):
            assert self.__class__ is MockClass
            assert param == 'foo'
    obj = MockClass()
    cb = Callback(obj.func)
    cb('foo')
    del obj
    cb('bar')  # This should not cause an exception.


def test_async_service():
    class MockService(AsyncService):
        def __init__(self):
            super(MockService, self).__init__(tick_interval=0.01)
            self.call_count = 0

        def tick(self):
            super(MockService, self).tick()
            self.call_count += 1

    svc = MockService()

    time.sleep(0.05)
    assert svc.call_count == 0

    svc.start()
    time.sleep(0.05)
    assert svc.call_count >= 5

    svc.stop()
    time.sleep(0.05)
    assert svc.call_count <= 6


def test_service_manager():
    mgr = ServiceManager()
    inst = mgr.bind(BaseService)
    assert inst is not None
    inst2 = mgr.bind(BaseService)
    assert inst is inst2
    mgr.unbind(BaseService)
    mgr.unbind(BaseService)
    inst3 = mgr.bind(BaseService)
    assert inst is not inst3
