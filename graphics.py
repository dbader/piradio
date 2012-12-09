import png

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

class Rect(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.rx = x + width
        self.ry = y + height

    def __repr__(self):
        return '%s(%i, %i, %i, %i)' % (self.__class__.__name__, self.x, self.y, self.width, self.height)

    @property
    def width(self):
        return self.rx - self.x

    @property
    def height(self):
        return self.ry - self.y

    def intersection(self, other):
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        rx = min(self.rx, other.rx)
        ry = min(self.ry, other.ry)
        return Rect(x, y, rx - x, ry - y)

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

    def __getitem__(self, key):
        return self.pixels[key]

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def rect(self):
        return Rect(0, 0, self._width, self._height)

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
        srcrect = Rect(x, y, src.width, src.height)
        cliprect = self.rect.intersection(srcrect)
        print self.rect, srcrect, cliprect
        for sx in range(cliprect.width):
            for sy in range(cliprect.height):
                pixel = (y + sy) * self._width + x + sx
                self.pixels[pixel] = op(self.pixels[pixel], src.pixels[sy * src.width + sx])

    def text(self, font, x, y, text):
        w, h, baseline = font.text_extents(text)
        bmp = font.render(text, w, h, baseline)
        print repr(bmp)
        self.bitblt(bmp, x, y)

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

    def apply(self, func):
        for i in range(len(self.pixels)):
            self.pixels[i] = func(self.pixels[i])

def clamp(v, min_value, max_value):
    return min(max(min_value, v), max_value)

def render_list(framebuffer, x, y, font, items, selected_index=-1, minheight=-1, maxvisible=4):
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
                framebuffer.hline(i)
        top_offset = (maxheight - textheight) / 2
        framebuffer.bitblt(textbitmap, x, y+top_offset, op=rop_xor)
        y += maxheight

if __name__ == '__main__':
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

    r1 = Rect(100, 100, 50, 50)
    r2 = Rect(50, 50, 100, 100)
    print r1, r2
    print r2.intersection(r1)
