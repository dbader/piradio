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

FONT_PATH = os.path.join(os.getcwd(), 'assets/font.ttf')
GLYPHFONT_PATH = os.path.join(os.getcwd(), 'assets/pixarrows.ttf')
GLYPH_PLAYING = '0'#unichr(9654)

sock = None
eventqueue = Queue.Queue()

def lcd_update():
    message = protocol.encode_message(protocol.CMD_DRAW, protocol.encode_bitmap(graphics.framebuffer))
    protocol.write_message(sock, message)

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
    while True:
        while not eventqueue.empty():
            event = eventqueue.get()
            logger.info('Got event: %s', event)
            if event.get('name') == 'key.down':
                if event.get('key') == protocol.KEY_UP:
                    cy -= 1
                    cy = graphics.clamp(cy, 0, len(stations)-1)
                if event.get('key') == protocol.KEY_DOWN:
                    cy += 1
                    cy = graphics.clamp(cy, 0, len(stations)-1)
                if event.get('key') == protocol.KEY_RIGHT:
                    w, h, img = graphics.loadimage('assets/dithertest.png')
                    print w, h
                    img_dithered = graphics.dither(img, w, h)
                    graphics.bitblt(img_dithered, 128, 64, 0, 0)
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
           graphics.clear()
           if currstation:
               w, h, baseline = glyph_font.text_extents(currstation)
               logging.debug('baseline is %i', baseline)
               graphics.text(glyph_font, -1, -baseline-1, GLYPH_PLAYING)
               w, h, baseline = font.text_extents(currstation)
               logging.debug('baseline is %i', baseline)
               graphics.text(font, 10, 3 - baseline, currstation)
           graphics.text(font, 100, 2, timestr)
           graphics.hline(12)
           graphics.render_list(2, 14, font, stations.keys(), cy, minheight=12)
           lcd_update()
           needs_redraw = False

        time.sleep(1.0 / 30.0)

def client_netloop():
    global sock
    HOST, PORT = "localhost", 7998
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))
        while True:
            received = protocol.read_message(sock)
            l, c, p = protocol.decode_message(received)
            if c == protocol.CMD_KEYSTATE:
                logging.debug('Got keystate')
                for i in range(len(p)):
                    if p[i]:
                        eventqueue.put({'name': 'key.down', 'key': i})
    finally:
        sock.close()

network_thread = threading.Thread(target=client_netloop)
network_thread.start()
time.sleep(1)
client_main()
