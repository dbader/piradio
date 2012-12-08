import png

LCD_WIDTH, LCD_HEIGHT = 128, 64
framebuffer = bytearray(LCD_WIDTH * LCD_HEIGHT)

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

class Surface(object):
    def __init__(self, width=0, height=0, filename=None, pixels=None):
        self._width = width
        self._height = height
        if filename:
            self.loadimage(filename)
        elif pixels:
            self.pixels = bytearray(pixels)
        else:
            self.pixels = bytearray(width * height)

    def __str__(self):
        return '%s<%ix%i>' % (self.__class__.__name__, self._width, self._height)

    def __repr__(self):
        bstr = ''
        for i in range(self._height):
            rowstr = ''
            for j in range(self._width):
                rowstr += '#' if self.pixels[i * self._width + j] else '.'
            bstr += rowstr + '\n'
        return bstr

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def fill(self, color=1):
        for i in range(len(self.pixels)):
            self.pixels[i] = color

    def getpixel(self, x, y):
        return self.pixels[y * self._width + x]

    def setpixel(self, x, y, color=1):
        pixel = y * self._width + x
        self.pixels[pixel] = color

    def vline(self, x, color=1):
        for y in range(self._height):
            self.setpixel(x, y, color)

    def hline(self, y, color=1):
        for x in range(self._width):
            self.setpixel(x, y, color)

    def bitblt(self, src, x=0, y=0, op=rop_replace):
        for sx in range(src.width):
            for sy in range(src.height):
                pixel = (y + sy) * self._width + x + sx
                if pixel < len(self.pixels):
                    self.pixels[pixel] = op(self.pixels[pixel], src.pixels[sy * src.width + sx])

    # def rect(x, y, w, h, color=1):
    #     pass

    def loadimage(self, filename):
        reader = png.Reader(filename)
        self._width, self._height, pixels, metadata = reader.read_flat()
        self.pixels = bytearray(px for i, px in enumerate(reversed(pixels)) if i % 3 == 0)

    def dither(self):
        """
        Return an Atkinson-dithered version of `bitmap`. Each pixel in `bitmap` may take
        values may lie in [0, 255].
        Based on code by Michal Migurski: http://mike.teczno.com/notes/atkinson.html
        """
        threshold = 128*[0] + 128*[255]
        for y in range(self._height):
            for x in range(self._width):
                old = self.pixels[y * self._width + x]
                new = threshold[old]
                err = (old - new) >> 3 # divide by 8
                self.pixels[y * self._width + x] = new
                for nxy in [(x+1, y), (x+2, y), (x-1, y+1), (x, y+1), (x+1, y+1), (x, y+2)]:
                    try:
                        px = nxy[1] * self._width + nxy[0]
                        self.pixels[px] = max(min(self.pixels[px] + err, 255), 0)
                    except IndexError:
                        pass

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
    bitblt_op(bmp.pixels, bmp.width, bmp.height, x, y)

def bitblt_op(src, src_w, src_h, x, y, op=rop_replace):
    for sx in range(src_w):
        for sy in range(src_h):
            fb_index = (y + sy) * LCD_WIDTH + x + sx
            if fb_index < len(framebuffer):
                framebuffer[fb_index] = op(framebuffer[fb_index], src[sy * src_w + sx])

def render_list(x, y, font, items, selected_index=-1, minheight=-1, maxvisible=4):
    maxheight = max([font.text_extents(text)[1] for text in items])
    maxheight = max(minheight, maxheight)
    start = max(0, min(selected_index-maxvisible+1, len(items)-maxvisible))
    end = start + maxvisible
    selected_index -= start
    for i, text in enumerate(items[start:end]):
        textwidth, textheight, baseline = font.text_extents(text)
        textbitmap = font.render(text, width=textwidth, height=textheight, baseline=baseline)
        if i == selected_index:
            for i in range(y,y+maxheight):
                hline(i)
        top_offset = (maxheight - textheight) / 2
        bitblt_op(textbitmap.pixels, textwidth, textheight, x, y+top_offset, rop_xor)
        y += maxheight

def dither(bitmap, width, height):
    """
    Return an Atkinson-dithered version of `bitmap`. Each pixel in `bitmap` may take
    values may lie in [0, 255].
    Based on code by Michal Migurski: http://mike.teczno.com/notes/atkinson.html
    """
    threshold = 128*[0] + 128*[255]
    out = bytearray(bitmap)
    for y in range(height):
        for x in range(width):
            old = out[y*width+x]
            new = threshold[old]
            err = (old - new) >> 3 # divide by 8
            out[y*width+x] = new
            for nxy in [(x+1, y), (x+2, y), (x-1, y+1), (x, y+1), (x+1, y+1), (x, y+2)]:
                try:
                    out[nxy[1]*width+nxy[0]] = max(min(out[nxy[1]*width+nxy[0]] + err, 255), 0)
                except IndexError:
                    pass
    return out

def bitmap2str(bmp, width, height, filled_char= ' # ', empty_char=' . '):
    bstr = ''
    for i in range(height):
        rowstr = ''
        for j in range(width):
            rowstr += filled_char if bmp[i*width+j] else empty_char
        bstr += rowstr + '\n'
    return bstr

def loadimage(filename):
    import png
    reader = png.Reader(filename)
    width, height, pixels, metadata = reader.read_flat()
    pixels = [px for i, px in enumerate(pixels) if i % 3 == 0]
    return width, height, pixels

if __name__ == '__main__':
    # inb = [32] * (32*32) + [64] * (32*32) + [128] * (32*32) + [255] * (32*32)
    # # inb = [100] * (4096)
    # print inb
    # print bitmap2str(inb, 64, 64)
    # outb = dither(inb, 64, 64)
    # print bitmap2str(outb, 64, 64)

    # w, h, img = loadimage('assets/michelangelo.png')
    # # print w, h
    # # print bitmap2str(img, w, h)
    # img_dithered = dither(img, w, h)
    # # print bitmap2str(img_dithered, w, h)

    s = Surface(32, 32)
    print s
    print repr(s)
    s.fill()
    print repr(s)
    s.loadimage('assets/dithertest.png')
    s.dither()
    print repr(s)

    s = Surface(16, 16)
    s.vline(0)
    s.hline(0)
    print repr(s)

    import time
    t0 = time.time()
    for i in range(10000):
        s = Surface('assets/dithertest.png')
        s.dither()
    print time.time() - t0

    s1 = Surface(8, 8)
    s2 = Surface(2, 2)
    s2.fill(1)
    print repr(s1)
    print repr(s2)
    s1.bitblt(s2, 0, 0)
    s1.bitblt(s2, 0, 6)
    s1.bitblt(s2, 6, 0)
    s1.bitblt(s2, 6, 6)
    s1.bitblt(s2, 3, 3)
    print repr(s1)
    s1.bitblt(s2, 7, 3)
    print repr(s1)
