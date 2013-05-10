# -*- coding: utf-8 -*-
"""
The problem: Raspi LCD only supports polled keyboard input.
The solution: Have one thread (process via multiprocessing) poll the buttons at 60 Hz
              and generate events via multiprocessing's shared queues.
              We can also do rendering in this process (Note: this is starting to sound like an X11 server ...)
"""
import multiprocessing
import time
import logging
import lcd
import random
import time

logging.basicConfig(level=logging.INFO)

LCD_WIDTH, LCD_HEIGHT = lcd.LCD_WIDTH, lcd.LCD_HEIGHT

framebuffer_lock = multiprocessing.Lock()
framebuffer = multiprocessing.Array('b', LCD_WIDTH * LCD_HEIGHT, lock=False)
framebuffer_needs_redraw = multiprocessing.Value('b')
eventqueue = multiprocessing.Queue()

def server_main():
    """
    Read input and render at a fixed frame rate of 60 Hz.
    """
    ALL_KEYS = [fakelcd.KEY_LEFT, fakelcd.KEY_RIGHT, fakelcd.KEY_UP, fakelcd.KEY_DOWN, fakelcd.KEY_CENTER]
    logger = logging.getLogger('server')
    logger.info('starting up')
    fakelcd.init()
    keystates = [0] * len(ALL_KEYS)
    prev_keystates = list(keystates)
    while not fakelcd.should_quit:
        fakelcd.pollkeys()
        for index, key in enumerate(ALL_KEYS):
            keystates[index] = fakelcd.keydown(key)
            if keystates[index] and not prev_keystates[index]:
                eventqueue.put({'name':'key.down', 'key': index})
            elif prev_keystates[index] and not keystates[index]:
                eventqueue.put({'name':'key.up', 'key': index})
        prev_keystates = list(keystates)

        if framebuffer_needs_redraw.value:
            logging.info('redrawing display')
            framebuffer_lock.acquire()
            fakelcd.update(framebuffer)
            framebuffer_lock.release()
            framebuffer_needs_redraw.value = False

        time.sleep(1.0 / 60.0)

if __name__ == '__main__':
    import lcdclient
    logging.info('starting up')
    p = multiprocessing.Process(target=lcdclient.client_main, args=(eventqueue, framebuffer, framebuffer_lock, framebuffer_needs_redraw))
    p.start()
    server_main()
    eventqueue.put('quit')
    p.join()
