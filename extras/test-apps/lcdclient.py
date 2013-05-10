import logging
import fontlib
import datetime
import audiolib
import time

LCD_WIDTH, LCD_HEIGHT = 128, 64

eventqueue = None
framebuffer = None
framebuffer_lock = None
framebuffer_needs_redraw = None

def lcd_clear(color=False):
    for i in range(len(framebuffer)):
        framebuffer[i] = color

def lcd_setpixel(x, y, color=True):
    pixel = y * LCD_WIDTH + x
    if pixel < len(framebuffer):
        framebuffer[pixel] = color

def lcd_vline(x, color=True):
    for y in range(LCD_HEIGHT):
        lcd_setpixel(x, y, color)

def lcd_hline(y, color=True):
    for x in range(LCD_WIDTH):
        lcd_setpixel(x, y, color)

def lcd_rect(x, y, w, h, color=True):
    pass

def clamp(v, min_value, max_value):
    return min(max(min_value, v), max_value)

def lcd_bitblt(src, src_w, src_h, x, y):
    for sx in range(src_w):
        for sy in range(src_h):
            dst_pixel = (y + sy) * LCD_WIDTH + x + sx
            if dst_pixel < len(framebuffer):
                framebuffer[dst_pixel] = src[sy * src_w + sx]

def lcd_text(font, x, y, text):
    w, h, baseline = font.text_extents(text)
    bmp = font.render(text, w, h, baseline)
    lcd_bitblt_op(bmp, w, h, x, y)

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
            if fb_index < len(framebuffer):
                framebuffer[fb_index] = op(framebuffer[fb_index], src[sy * src_w + sx])

def render_list(top, font, items, selected_index=-1):
    maxheight = max([font.text_extents(text)[1] for text in items])
    y = top
    for i, text in enumerate(items):
        textwidth, textheight, baseline = font.text_extents(text)
        textbitmap = font.render(text, width=textwidth, height=textheight, baseline=baseline)
        if i == selected_index:
            for i in range(y,y+maxheight):
                lcd_hline(i)
        top_offset = (maxheight - textheight) / 2
        lcd_bitblt_op(textbitmap, textwidth, textheight, 0, y+top_offset, rop_xor)
        y += maxheight

def client_main(_eventqueue, _framebuffer, _framebuffer_lock, _framebuffer_needs_redraw):
    global eventqueue
    global framebuffer
    global framebuffer_lock
    global framebuffer_needs_redraw
    eventqueue = _eventqueue
    framebuffer = _framebuffer
    framebuffer_lock = _framebuffer_lock
    framebuffer_needs_redraw = _framebuffer_needs_redraw
    logger = logging.getLogger('client')
    logger.info('starting up')

    font = fontlib.Font('/Users/daniel/dev/piradio/test-apps/font4.ttf', 8)

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
            framebuffer_lock.acquire()
            lcd_clear()
            lcd_text(font, 100, 2, str(datetime.datetime.now().strftime('%I:%M')))
            lcd_hline(11)
            render_list(14, font, ['Radio', 'Podcasts', 'Settings'], cy)
            framebuffer_lock.release()
            framebuffer_needs_redraw.value = True
            needs_redraw = False

        time.sleep(1.0 / 30.0)