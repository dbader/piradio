import logging
import fontlib
import datetime
import audiolib
import time
import Queue
import protocol
import threading
import socket

LCD_WIDTH, LCD_HEIGHT = 128, 64
sock = None
eventqueue = Queue.Queue()
framebuffer = [0] * (LCD_WIDTH * LCD_HEIGHT)

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

def lcd_update():
    message = protocol.encode_message(protocol.CMD_BITBLT, bytearray(framebuffer))
    protocol.write_message(sock, message)

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

def client_main():
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
            lcd_clear()
            lcd_text(font, 100, 2, str(datetime.datetime.now().strftime('%I:%M')))
            lcd_hline(11)
            render_list(14, font, ['Radio', 'Podcasts', 'Settings'], cy)
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
