import mock
import time
from ..base import (BaseService, AsyncService, ServiceManager,
                    deliver_pending_notifications)


def test_subscriptions():
    svc = BaseService()
    client = mock.Mock()
    svc.subscribe('foo_event', client.on_foo)

    svc.notify_subscribers('foo_event', 1, 2, 3, value='hello')
    deliver_pending_notifications()
    client.on_foo.assert_called_once_with(1, 2, 3, value='hello')

    client.reset_mock()
    svc.notify_subscribers('bar_event')
    deliver_pending_notifications()
    assert not client.on_foo.called


def test_unsubscribe():
    svc = BaseService()
    client = mock.Mock()
    svc.subscribe('foo_event', client.on_foo)

    svc.notify_subscribers('foo_event')
    deliver_pending_notifications()
    client.on_foo.assert_called_once_with()

    client.reset_mock()
    svc.unsubscribe(client.on_foo)
    svc.notify_subscribers('foo_event')
    deliver_pending_notifications()
    assert not client.on_foo.called


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
