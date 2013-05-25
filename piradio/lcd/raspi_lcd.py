"""LCD driver for the "Raspi LCD" board by emsystech engineering

The driver uses the libraspilcd.so C library built from the
libraspi-lcd/ directory in the project root. The board can be ordered at
http://www.emsystech.de/produkt/raspi-lcd/.
"""
import ctypes
import time
import logging

logging.basicConfig(level=logging.DEBUG)

K_LEFT = 0
K_RIGHT = 1
K_UP = 2
K_DOWN = 3
K_CENTER = 4

LCD_WIDTH, LCD_HEIGHT = 128, 64
KEY_CENTER = 0x04
KEY_LEFT = 0x02
KEY_RIGHT = 0x08
KEY_UP = 0x01
KEY_DOWN = 0x10

raspilcd = ctypes.cdll.LoadLibrary("./libraspilcd.so")
buttons = ctypes.c_uint8.in_dll(raspilcd, "Button")
_KEYS = [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_CENTER]


def init(debug=True):
    raspilcd.RaspiLcdHwInit()
    raspilcd.LCD_Init()
    raspilcd.LCD_ClearScreen()
    raspilcd.LCD_WriteFramebuffer()
    if debug:
        raspilcd.LCD_SetPenColor(1)
        raspilcd.LCD_DrawLine(0, 0, LCD_WIDTH-1, LCD_HEIGHT-1)
        raspilcd.LCD_DrawLine(0, LCD_HEIGHT-1, LCD_WIDTH-1, 0)
        raspilcd.LCD_WriteFramebuffer()


def readkeys():
    raspilcd.UpdateButtons()
    return [_keydown(k) for k in _KEYS]


def _keydown(key):
    return bool(buttons.value & key)


def update(pixels):
    raspilcd.LCD_ClearScreen()
    px = pixels.pixels
    row_idx = 0
    for y in xrange(LCD_HEIGHT):
        for x in xrange(LCD_WIDTH):
            if px[row_idx + x]:
                raspilcd.LCD_PutPixel(x, y)
        row_idx += LCD_WIDTH
    raspilcd.LCD_WriteFramebuffer()


def set_contrast(c):
    MAX_CONTRAST = 10
    value = int(min(MAX_CONTRAST, max(0, c)) * MAX_CONTRAST)
    logging.debug('Setting contrast to %.2f (%i)', c, value)
    raspilcd.LCD_SetContrast(value)


def set_backlight_enabled(enabled):
    logging.debug('Setting backlight to %s', 'on' if enabled else 'off')
    raspilcd.SetBacklight(enabled)

if __name__ == '__main__':
    init()
    set_contrast(0.6)
    set_backlight_enabled(True)
    t = 1.0
    while not True in readkeys():
        update([0] * (LCD_WIDTH * LCD_HEIGHT))
        set_backlight_enabled(False)
        time.sleep(t)
        update([1] * (LCD_WIDTH * LCD_HEIGHT))
        set_backlight_enabled(True)
        time.sleep(t)
