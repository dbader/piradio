import logging
import os
import fontlib
import datetime
import audiolib
import time
import graphics
import json
import commons
import ui

import fakelcd as lcd
# import lcd

FONT_PATH = os.path.join(os.getcwd(), 'assets/font.ttf')
GLYPHFONT_PATH = os.path.join(os.getcwd(), 'assets/pixarrows.ttf')
CLOCK_FONT_PATH = os.path.join(os.getcwd(), 'assets/SourceCodePro-Regular.otf')
GLYPH_PLAYING = '0'#unichr(9654)


UPDATE_RATE = 60.0

framebuffer = graphics.Surface(lcd.LCD_WIDTH, lcd.LCD_HEIGHT)
lcd.init()

def lcd_update():
    # framebuffer.apply(lambda pixel: 0 if pixel else 1)
    # framebuffer.apply(lambda pixel: pixel * 200)
    # framebuffer.dither()
    print repr(framebuffer)
    logging.debug('Updating LCD')
    lcd.update(framebuffer)

prev_keystates = None
def trigger_key_events():
    global prev_keystates
    keystates = lcd.readkeys()
    if keystates != prev_keystates:
        for i in range(len(keystates)):
            if keystates[i]:
                on_key_down(i)
    prev_keystates = keystates

# ----------- SLEEP
LCD_SLEEPTIME = 5 * 60
sleeptime = None
sleeping = False

def shouldsleep():
    return time.time() > sleeptime

def resetsleep():
    global sleeptime
    sleeptime = time.time() + LCD_SLEEPTIME
    logging.debug('Sleeptime set to %f', sleeptime)

def sleep():
    logging.info('Going to sleep')
    lcd.set_backlight_enabled(False)
    global sleeping
    sleeping = True
    global UPDATE_RATE
    UPDATE_RATE /= 4

def wakeup():
    logging.info('Waking up')
    lcd.set_backlight_enabled(True)
    global sleeping
    sleeping = False
    global UPDATE_RATE
    UPDATE_RATE *= 4

def update_sleep():
    global sleeping
    if not sleeping and shouldsleep():
        sleep()
    elif sleeping and not shouldsleep():
        wakeup()
        resetsleep()
# ------------------------

logger = logging.getLogger('client')
logger.info('Starting up')

font = fontlib.Font(FONT_PATH, 8)
glyph_font = fontlib.Font(GLYPHFONT_PATH, 10)
stations = json.loads(open('stations.json').read())

cy = 0
needs_redraw = True
currstation = ''
prev_timestr = ''
resetsleep()
audiolib.stop()

def dither_test():
    img = graphics.Surface(filename='assets/dithertest.png')
    img.dither()
    framebuffer.bitblt(img, 0, 0)
    lcd_update()
    time.sleep(5)

def big_clock():
    time_of_day = str(datetime.datetime.now().strftime('%H:%M'))
    clock_font = fontlib.Font(CLOCK_FONT_PATH, 40)
    framebuffer.fill(0)
    framebuffer.center_text(clock_font, time_of_day)
    lcd_update()
    time.sleep(5)

def on_key_down(key):
    global cy, needs_redraw, currstation
    resetsleep()
    if key == lcd.K_UP:
        cy -= 1
        cy = commons.clamp(cy, 0, len(stations)-1)
    if key == lcd.K_DOWN:
        cy += 1
        cy = commons.clamp(cy, 0, len(stations)-1)
    if key == lcd.K_RIGHT:
        dither_test()
    if key == lcd.K_LEFT:
        big_clock()
    if key == lcd.K_CENTER:
        if currstation == stations.keys()[cy]:
            logging.debug('Stopping playback')
            audiolib.stop()
            currstation = ''
        else:
            logging.debug('Switching station')
            audiolib.playstream(stations.values()[cy], fade=False)
            currstation = stations.keys()[cy]
    needs_redraw = True

def update_clock():
    global timestr, prev_timestr, needs_redraw
    timestr = str(datetime.datetime.now().strftime('%H:%M'))
    if timestr != prev_timestr:
        prev_timestr = timestr
        logging.debug('Redrawing the clock')
        needs_redraw = True

def redraw():
    # Clear the framebuffer
    framebuffer.fill(0)

    # If necessary, draw the 'playing' icon and the name of the current station
    if currstation:
        w, h, baseline = glyph_font.text_extents(currstation)
        framebuffer.text(glyph_font, 0, -baseline-1, GLYPH_PLAYING)

        w, h, baseline = font.text_extents(currstation)
        framebuffer.text(font, 10, 2 - baseline, currstation)

    # Draw the clock
    w, h, baseline = font.text_extents(timestr)
    framebuffer.text(font, framebuffer.width - w - 2, 2-baseline, timestr)

    # Draw separator between the 'status area' and the station selector
    framebuffer.hline(11)

    # Draw the station selector
    ui.render_list(framebuffer, 2, 14, font, stations.keys(), cy, minheight=12)

    lcd_update()

while True:
    update_sleep()
    trigger_key_events()
    update_clock()

    if needs_redraw:
        redraw()
        needs_redraw = False

    time.sleep(1.0 / UPDATE_RATE)