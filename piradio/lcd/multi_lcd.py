"""LCD driver multiplexer. Allows you to run multiple LCD drivers
in parallel, e.g. raspi_lcd + web_lcd."""
import importlib
import logging

logging.basicConfig(level=logging.DEBUG)

# Attempt to load drivers in this order. If a driver fails to load
# we silently ignore the error and continue with the next
DRIVERS = [
    'piradio.lcd.raspi_lcd',
    'piradio.lcd.fake_lcd',
    'piradio.lcd.web_lcd'
]
_DRIVERS = []

LCD_WIDTH, LCD_HEIGHT = 128, 64

K_LEFT = 0
K_RIGHT = 1
K_UP = 2
K_DOWN = 3
K_CENTER = 4


def init(debug=True):
    for drv in DRIVERS:
        try:
            _DRIVERS.append(importlib.import_module(drv))
            logging.info('Loaded LCD driver %s', drv)
        except OSError:
            logging.warning('Failed to load LCD driver %s', drv)
    for drv in _DRIVERS:
        drv.init(debug)


def readkeys():
    keys = [False] * 5
    for drv in _DRIVERS:
        for i, k in enumerate(drv.readkeys()):
            keys[i] = keys[i] or k
    return keys


def update(pixels):
    for drv in _DRIVERS:
        drv.update(pixels)


def set_contrast(c):
    for drv in _DRIVERS:
        drv.set_contrast(c)


def set_backlight_enabled(enabled):
    for drv in _DRIVERS:
        drv.set_backlight_enabled(enabled)
