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

FONT_PATH = os.path.join(os.getcwd(), 'test-apps/font4.ttf')

sock = None
eventqueue = Queue.Queue()

def lcd_update():
    message = protocol.encode_message(protocol.CMD_DRAW, protocol.encode_bitmap(graphics.framebuffer))
    protocol.write_message(sock, message)

def client_main():
    logger = logging.getLogger('client')
    logger.info('starting up')
    font = fontlib.Font(FONT_PATH, 8)

    r = 0.5
    cx = 0
    cy = 0
    needs_redraw = True
    while True:
        while not eventqueue.empty():
            event = eventqueue.get()
            logger.info('got event: %s', event)
            if event == 'quit':
                return
            if event.get('name') == 'key.down':
                if event.get('key') == 0:
                    r += 0.05
                    cx -= 1
                if event.get('key') == 1:
                    r -= 0.05
                    cx += 1
                if event.get('key') == 2:
                    cy -= 1
                if event.get('key') == 3:
                    cy += 1
                if event.get('key') == 4:
                    audiolib.playstream([
                        'http://gffstream.ic.llnwd.net/stream/gffstream_w14b',
                        'http://mp3stream1.apasf.apa.at:8000',
                        'http://stream.m945.mwn.de:80/m945-hq.mp3'
                    ][cy], fade=False)
                    # cy = -1
                needs_redraw = True

        if needs_redraw:
            graphics.clear()
            graphics.text(font, 100, 2, str(datetime.datetime.now().strftime('%II:%MM')))
            graphics.hline(11)
            graphics.render_list(14, font, ['Radio', 'Podcasts', 'Settings'], cy)
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
                print 'got keystate'
                for i in range(len(p)):
                    print i, p[i]
                    if p[i]:
                        eventqueue.put({'name': 'key.down', 'key': i})
    finally:
        sock.close()

network_thread = threading.Thread(target=client_netloop)
network_thread.start()
time.sleep(1)
client_main()
