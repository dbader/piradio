import os
import mock
import random
import piradio.graphics as graphics
import piradio.fonts as fonts
from piradio.panels.base import Panel
from piradio.panels import (AlarmPanel, ClockPanel, RandomPodcastPanel,
                            PublicTransportPanel, RadioPanel,
                            DitherTestPanel, AnimationTestPanel,
                            WeatherPanel)
from piradio.services import ServiceBroker


PANELS = [
    (Panel, {}),
    (AlarmPanel, {}),
    (ClockPanel, {}),
    (RandomPodcastPanel, {'url': 'http://domian.alpha-labs.net/domian.rss'}),
    (PublicTransportPanel, {'station': 'Marienplatz'}),
    (RadioPanel, {}),
    (DitherTestPanel, {}),
    (AnimationTestPanel, {}),
    (WeatherPanel, {'title': 'TestCity', 'lat': 48.5, 'lon': 11.5})
]


def make_service_mock(clsname):
    svc_class_mock = mock.Mock()
    svc_class_mock.__name__ = clsname
    svc_class_mock.return_value = mock.Mock()
    return svc_class_mock


def monkey_test(pnl):
    """Monkey-test the panels by randomly pressing buttons."""
    surf = graphics.Surface(128, 64)
    for _ in range(100):
        key_func = random.choice([pnl.up_pressed, pnl.down_pressed,
                                  pnl.center_pressed])
        key_func()
        pnl.update()
        pnl.paint(surf)


def test_init_paint_update():
    cwd = os.getcwd()
    fonts.register('tempesta',
                   os.path.join(cwd, 'assets/pf_tempesta_seven.ttf'))
    fonts.register('pixarrows', os.path.join(cwd, 'assets/pixarrows.ttf'))
    fonts.register('climacons', os.path.join(cwd, 'assets/climacons.ttf'))
    fonts.register('helvetica', os.path.join(cwd, 'assets/helvetica.ttf'))

    broker = ServiceBroker()
    clock_mock = make_service_mock('ClockServiceMock')
    clock_mock.return_value.timeofday.return_value = '13:37'
    weather_mock = make_service_mock('WeatherServiceMock')
    broker.register_service(clock_mock, 'ClockService')
    broker.register_service(weather_mock, 'WeatherService')

    surf = graphics.Surface(128, 64)

    for cls, config in PANELS:
        pnl = broker.instantiate(cls, config)
        pnl.paint(surf)
        pnl.update()
        monkey_test(pnl)
