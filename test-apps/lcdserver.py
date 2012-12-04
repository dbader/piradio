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
import fakelcd
import random
import freetypetest2 as fnt
import freetype

logging.basicConfig(level=logging.INFO)

framebuffer_lock = multiprocessing.Lock()
framebuffer = multiprocessing.Array('b', 128 * 64, lock=False)
framebuffer_needs_redraw = multiprocessing.Value('b')
eventqueue = multiprocessing.Queue()

LCD_WIDTH, LCD_HEIGHT = fakelcd.LCD_WIDTH, fakelcd.LCD_HEIGHT

def lcd_clear(enabled=False):
    for i in range(len(framebuffer)):
        framebuffer[i] = enabled

def lcd_setpixel(x, y, enabled=True):
    framebuffer[y*LCD_WIDTH + x] = enabled
    
def lcd_vline(x, enabled=True):
    for y in range(LCD_HEIGHT):
        lcd_setpixel(x, y, enabled)

def lcd_hline(y, enabled=True):
    for x in range(LCD_WIDTH):
        lcd_setpixel(x, y, enabled)
        
def lcd_bitblt(src, src_w, src_h, x, y):
    for sx in range(src_w):
        for sy in range(src_h):
            framebuffer[(y + sy) * LCD_WIDTH + x + sx] = src[sy * src_w + sx]
            
def rop_replace(a, b):
    return b
    
def rop_invert(a, b):
    return not b
    
def rop_and(a, b):
    return a and b
    
def rop_or(a, b):
    return a or b
    
def rop_xor(a, b):
    return a ^ b            

def lcd_bitblt_op(src, src_w, src_h, x, y, op=rop_replace):
    for sx in range(src_w):
        for sy in range(src_h):
            fb_index = (y + sy) * LCD_WIDTH + x + sx
            framebuffer[fb_index] = op(framebuffer[fb_index], src[sy * src_w + sx])


def client_main():
    logger = logging.getLogger('client')
    logger.info('starting up')

    face = freetype.Face('/Users/daniel/dev/piradio/test-apps/font4.ttf')
    text = u'Hello, piradio'
    face.set_char_size( 16*64 )    
    width, height, baseline = fnt.text_extents(face, text)
    text_bmp = fnt.text_render(face, width, height, baseline, text)    
    print '"%s": width=%i height=%i baseline=%i' % (text, width, height, baseline)
    # fnt.print_bitmap(text_bmp, width, height)
        
    r = 0.5
    cx = 0
    cy = 0
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
                    cy -= 3    
                if event.get('key') == 3:
                    cy += 3
                    
        
        framebuffer_lock.acquire()

        lcd_clear()
        lcd_bitblt([1] * 40 * 50, 40, 50, 10, 10)
        lcd_bitblt_op(text_bmp, width, height, cx, cy, op=rop_xor)

        lcd_hline(0)
        lcd_hline(LCD_HEIGHT-1)
        lcd_vline(0)
        lcd_vline(LCD_WIDTH-1)        
        framebuffer_lock.release()
        framebuffer_needs_redraw.value = True
                    
        time.sleep(1.0 / 30.0)
        
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
            logging.debug('redrawing display')
            framebuffer_lock.acquire()
            fakelcd.update(framebuffer)
            framebuffer_lock.release()
            framebuffer_needs_redraw.value = False

        time.sleep(1.0 / 60.0)        

if __name__ == '__main__':
    logging.info('starting up')
    p = multiprocessing.Process(target=client_main)
    p.start()
    server_main()
    eventqueue.put('quit')
    p.join()