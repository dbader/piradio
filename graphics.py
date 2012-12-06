LCD_WIDTH, LCD_HEIGHT = 128, 64
framebuffer = bytearray([0] * (LCD_WIDTH * LCD_HEIGHT))

def clear(color=0):
    for i in range(len(framebuffer)):
        framebuffer[i] = color

def setpixel(x, y, color=1):
    pixel = y * LCD_WIDTH + x
    if pixel < len(framebuffer):
        framebuffer[pixel] = color

def vline(x, color=1):
    for y in range(LCD_HEIGHT):
        setpixel(x, y, color)

def hline(y, color=1):
    for x in range(LCD_WIDTH):
        setpixel(x, y, color)

def rect(x, y, w, h, color=1):
    pass

def clamp(v, min_value, max_value):
    return min(max(min_value, v), max_value)

def bitblt(src, src_w, src_h, x, y):
    for sx in range(src_w):
        for sy in range(src_h):
            dst_pixel = (y + sy) * LCD_WIDTH + x + sx
            if dst_pixel < len(framebuffer):
                framebuffer[dst_pixel] = src[sy * src_w + sx]

def text(font, x, y, text):
    w, h, baseline = font.text_extents(text)
    bmp = font.render(text, w, h, baseline)
    bitblt_op(bmp, w, h, x, y)

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

def bitblt_op(src, src_w, src_h, x, y, op=rop_replace):
    for sx in range(src_w):
        for sy in range(src_h):
            fb_index = (y + sy) * LCD_WIDTH + x + sx
            if fb_index < len(framebuffer):
                framebuffer[fb_index] = op(framebuffer[fb_index], src[sy * src_w + sx])

def render_list(x, y, font, items, selected_index=-1, minheight=-1):
    maxheight = max([font.text_extents(text)[1] for text in items])
    maxheight = max(minheight, maxheight)
    for i, text in enumerate(items):
        textwidth, textheight, baseline = font.text_extents(text)
        textbitmap = font.render(text, width=textwidth, height=textheight, baseline=baseline)
        if i == selected_index:
            for i in range(y,y+maxheight):
                hline(i)
        top_offset = (maxheight - textheight) / 2
        bitblt_op(textbitmap, textwidth, textheight, x, y+top_offset, rop_xor)
        y += maxheight
