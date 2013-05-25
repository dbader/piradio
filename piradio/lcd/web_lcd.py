import logging
import threading
import time
import bottle
import piradio.graphics as graphics

logger = logging.getLogger('weblcd')

LCD_WIDTH, LCD_HEIGHT = 128, 64

K_LEFT = 0
K_RIGHT = 1
K_UP = 2
K_DOWN = 3
K_CENTER = 4

_KEYS = [False] * 5
_SCREEN = graphics.Surface(LCD_WIDTH, LCD_HEIGHT)


@bottle.get('/')
def get_index():
    return """
        <img src="/screen" width="128" height="64">
        <a href="/keys/left">left</a>
        <a href="/keys/right">right</a>
        <a href="/keys/up">up</a>
        <a href="/keys/down">down</a>
        <a href="/keys/center">center</a>
    """


@bottle.get('/screen')
def get_screen_image():
    png_data = _SCREEN.as_png_image()
    headers = {
        'Content-Type': 'image/png',
        'Content-Length': len(png_data)
    }
    return bottle.HTTPResponse(png_data, **headers)


@bottle.get('/keys/<key>')
def get_keys(key):
    keymap = {
        'center': K_CENTER,
        'left': K_LEFT,
        'right': K_RIGHT,
        'up': K_UP,
        'down': K_DOWN
    }
    keycode = keymap[key]
    _KEYS[keycode] = True
    # fixme: wait for a screen redraw
    time.sleep(0.25)
    bottle.redirect('/')


def init(debug=True):
    web_thread = threading.Thread(target=bottle.run)
    # Let the web thread die when the main thread exits
    web_thread.daemon = True
    web_thread.start()


def readkeys():
    keys = list(_KEYS)
    for k in range(len(_KEYS)):
        _KEYS[k] = False
    return keys


def update(pixels):
    _SCREEN.bitblt_fast(pixels, 0, 0)


def set_contrast(c):
    pass


def set_backlight_enabled(enabled):
    pass
