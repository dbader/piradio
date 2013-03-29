import logging
import fontlib
import datetime
import audiolib
import time
import Queue
import protocol
import threading
import socket
import os
import graphics
import json
import commons
import ui

import fakelcd as lcd
# import lcd

FONT_PATH = os.path.join(os.getcwd(), 'assets/font.ttf')
GLYPHFONT_PATH = os.path.join(os.getcwd(), 'assets/pixarrows.ttf')
GLYPH_PLAYING = '0'#unichr(9654)

sock = None
eventqueue = Queue.Queue()

UPDATE_RATE = 60.0

framebuffer = graphics.Surface(128, 64)

lcd.init()

def lcd_update():
    lcd.update(framebuffer)
    # print repr(framebuffer)
    # message = protocol.encode_message(protocol.CMD_DRAW, protocol.encode_bitmap(graphics.framebuffer))
    # protocol.write_message(sock, message)

prev_keystates = None
def readkeys():
    global prev_keystates
    keystates = lcd.readkeys()
    if keystates != prev_keystates:
        for i in range(len(keystates)):
            if keystates[i]:
                eventqueue.put({'name': 'key.down', 'key': i})
    prev_keystates = keystates

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

def client_main():
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
    while True:
        readkeys()
        if not sleeping and shouldsleep():
            sleep()
        elif sleeping and not shouldsleep():
            wakeup()
            resetsleep()
        while not eventqueue.empty():
            event = eventqueue.get()
            logger.info('Got event: %s', event)
            if event.get('name') == 'key.down':
                resetsleep()
                if event.get('key') == protocol.KEY_UP:
                    cy -= 1
                    cy = commons.clamp(cy, 0, len(stations)-1)
                if event.get('key') == protocol.KEY_DOWN:
                    cy += 1
                    cy = commons.clamp(cy, 0, len(stations)-1)
                if event.get('key') == protocol.KEY_RIGHT:
                    img = graphics.Surface(filename='assets/dithertest.png')
                    img.dither()
                    framebuffer.bitblt(img, 0, 0)
                    lcd_update()
                    time.sleep(10)
                if event.get('key') == protocol.KEY_CENTER:
                    if currstation == stations.keys()[cy]:
                        logging.debug('Stopping playback')
                        audiolib.stop()
                        currstation = ''
                    else:
                        logging.debug('Switching station')
                        audiolib.playstream(stations.values()[cy], fade=False)
                        currstation = stations.keys()[cy]
                needs_redraw = True

        timestr = str(datetime.datetime.now().strftime('%H:%M'))
        if timestr != prev_timestr:
            prev_timestr = timestr
            logging.debug('Redrawing clock')
            needs_redraw = True

        if needs_redraw:
           framebuffer.fill(0)
           if currstation:
               w, h, baseline = glyph_font.text_extents(currstation)
               framebuffer.text(glyph_font, 0, -baseline-1, GLYPH_PLAYING)
               w, h, baseline = font.text_extents(currstation)
               framebuffer.text(font, 10, 2 - baseline, currstation)
           w, h, baseline = font.text_extents(timestr)
           framebuffer.text(font, 100, 2-baseline, timestr)
           framebuffer.hline(12)
           ui.render_list(framebuffer, 2, 14, font, stations.keys(), cy, minheight=12)
           # framebuffer.apply(lambda pixel: 0 if pixel else 1)
           # framebuffer.apply(lambda pixel: pixel * 200)
           # framebuffer.dither()
           print repr(framebuffer)
           lcd_update()
           needs_redraw = False

        time.sleep(1.0 / UPDATE_RATE)

client_main()
