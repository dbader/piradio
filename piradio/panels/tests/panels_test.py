import os
import mock
import random
import piradio.graphics as graphics
import piradio.fonts as fonts
from piradio.panels.base import Panel
from piradio.panels import (AlarmPanel, ClockPanel, RandomPodcastPanel,
                            PublicTransportPanel, RadioPanel,
                            DitherTestPanel, AnimationTestPanel,
                            WeatherPanel, ShootEmUpGamePanel)
from piradio.services import ServiceBroker


PANELS = [
    (Panel, {}),
    (AlarmPanel, {}),
    (ClockPanel, {}),
    (RandomPodcastPanel, {
        'title': 'Test',
        'url': 'http://example.com/feed.rss'
    }),
    (PublicTransportPanel, {'station': 'Test'}),
    (RadioPanel, {
        "B5 Aktuell": "http://gffstream.ic.llnwd.net/stream/gffstream_w14b",
        "FM4": "http://mp3stream1.apasf.apa.at:8000",
        "M94.5": "http://stream.m945.mwn.de:80/m945-hq.mp3",
        "SomaFM": "http://voxsc1.somafm.com:3000",
        "Bob Marley Radio": "http://listen.radionomy.com/bob-marley",
        "Radio 2day": "http://stream2.radio2day.ip-streaming.net:80/radio2day",
        "Byte.FM": "http://streamingserver05.byte.fm:8000/",
        "Rock Antenne": "http://mp3.webradio.rockantenne.de:80",
        "Substanz FM": "http://streamplus36.leonex.de:21806"
    }),
    (DitherTestPanel, {}),
    (AnimationTestPanel, {}),
    (ShootEmUpGamePanel, {}),
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
    podcast_mock = make_service_mock('PodcastServiceMock')
    audio_mock = make_service_mock('AudioServiceMock')
    audio_mock.return_value.playback_progress.return_value = 0.5
    pt_mock = make_service_mock('PublicTransportServiceMock')
    broker.register_service(clock_mock, 'ClockService')
    broker.register_service(weather_mock, 'WeatherService')
    broker.register_service(podcast_mock, 'PodcastService')
    broker.register_service(audio_mock, 'AudioService')
    broker.register_service(pt_mock, 'PublicTransportService')

    surf = graphics.Surface(128, 64)

    for cls, config in PANELS:
        pnl = broker.instantiate(cls, config)
        pnl.paint(surf)
        pnl.update()
        monkey_test(pnl)
