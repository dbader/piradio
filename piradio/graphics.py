import png
import cStringIO as StringIO
import piradio.commons as commons

WHITE = 0
BLACK = 1

# For inspiration, see
# http://msdn.microsoft.com/de-de/library/dd162892(v=vs.85).aspx
rop_nop = lambda a, b: a
rop_copy = lambda a, b: b
rop_replace = rop_copy
rop_not = lambda a, b: not b
rop_invert = rop_not
rop_and = lambda a, b: a and b
rop_or = lambda a, b: a or b
rop_xor = lambda a, b: a ^ b
rop_black = lambda a, b: 0
rop_white = lambda a, b: 1


class Rect(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.rx = x + width
        self.ry = y + height

    def __repr__(self):
        return (self.__class__.__name__ +
                repr((self.x, self.y, self.width, self.height)))

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

    def clipped(self, other):
        def clamp(v, min_value, max_value):
            return min(max(min_value, v), max_value)

        # (x,y) must not be negative or larger than the
        # right or bottom edge.
        x = clamp(other.x, self.x, self.rx)
        y = clamp(other.y, self.y, self.ry)

        # (rx,ry) must not be less than (x,y) or larger than
        # the right or bottom edge.
        rx = clamp(other.rx, x, self.rx)
        ry = clamp(other.ry, y, self.ry)

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
        return self.__class__.__name__ + repr((self.width, self.height))

    def __repr__(self):
        bstr = ''
        for i in xrange(self._height):
            rowstr = ''
            for j in xrange(self._width):
                rowstr += '#' if self.pixels[i * self._width + j] else '.'
            bstr += rowstr + '\n'
        return bstr

    def __len__(self):
        return len(self.pixels)

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
        for i in xrange(len(self.pixels)):
            self.pixels[i] = color

    def clear(self):
        self.fill(color=0)

    def getpixel(self, x, y):
        return self.pixels[y * self._width + x]

    def setpixel(self, x, y, color=1):
        pixel = y * self._width + x
        self.pixels[pixel] = color

    def vline(self, x, color=1):
        px = x
        for _ in xrange(self._height):
            self.pixels[px] = color
            px += self._width

    def hline(self, y, color=1):
        px = y * self._width
        for _ in xrange(self._width):
            self.pixels[px] = color
            px += 1

    def bitblt_fast(self, src, x, y):
        """Blit without range checks, clipping and a hardwired rop_copy
        raster operation.
        """
        width = self.width
        pixels = self.pixels
        src_width, src_height = src.width, src.height
        src_pixels = src.pixels
        srcpixel = 0
        dstpixel = y * width + x

        for _ in xrange(src_height):
            for _ in xrange(src_width):
                pixels[dstpixel] = src_pixels[srcpixel]
                srcpixel += 1
                dstpixel += 1
            dstpixel += width - src_width

    def bitblt(self, src, x=0, y=0, op=rop_copy):
        # This is the area within the current surface we want to draw in.
        # It potentially lies outside of the bounds of the current surface.
        # Therefore we must clip it to only cover valid pixels within
        # the surface.
        dstrect = Rect(x, y, src.width, src.height)
        cliprect = self.rect.clipped(dstrect)

        # xoffs and yoffs are important when we clip against
        # the left or top edge.
        xoffs = src.width - cliprect.width if x <= 0 else 0
        yoffs = src.height - cliprect.height if y <= 0 else 0

        # Copy pixels from `src` to `cliprect`.
        dstrowwidth = cliprect.rx - cliprect.x
        srcpixel = yoffs * src._width + xoffs
        dstpixel = cliprect.y * self._width + cliprect.x
        dstpixels = self.pixels
        srcpixels = src.pixels
        for _ in xrange(cliprect.ry - cliprect.y):
            for _ in xrange(dstrowwidth):
                dstpixels[dstpixel] = op(dstpixels[dstpixel],
                                         srcpixels[srcpixel])
                srcpixel += 1
                dstpixel += 1
            srcpixel += src._width - dstrowwidth
            dstpixel += self._width - dstrowwidth

    # TODO: REFACTOR: Font rendering into Surfaces should be done
    # solely through fontlib.
    def text(self, font, x, y, text, rop=rop_copy):
        w, h, baseline = font.text_extents(text)
        bmp = font.render(text, w, h, baseline)
        self.bitblt(bmp, x, y, op=rop)

    def center_text(self, font, text, x=None, y=None, rop=rop_copy):
        w, h, _ = font.text_dimensions(text)
        x = x if x is not None else self.width / 2 - w / 2
        y = y if y is not None else y or self.height / 2 - h / 2
        self.text(font, x, y, text, rop)

    def strokerect(self, x, y, w, h, color=1):
        for dx in xrange(x, x + w):
            self.setpixel(dx, y, color)
            self.setpixel(dx, y + h - 1, color)
        for dy in xrange(y, y + h):
            self.setpixel(x, dy, color)
            self.setpixel(x + w - 1, dy, color)

    def fillrect(self, x, y, w, h, color=1):
        for dy in xrange(y, y + h):
            for dx in xrange(x, x + w):
                self.pixels[dy * self._width + dx] = color

    def loadimage(self, filename):
        reader = png.Reader(filename)
        self._width, self._height, pixels, _ = reader.read_flat()
        self.pixels = bytearray(px for i, px in
                                enumerate(reversed(pixels)) if i % 3 == 0)

    def as_png_image(self):
        buf = StringIO.StringIO()
        writer = png.Writer(self.width, self.height,
                            greyscale=True, bitdepth=1)
        writer.write_array(buf, [not px for px in self.pixels])
        return buf.getvalue()

    def write_image(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.as_png_image())

    def dither(self):
        """Return an Atkinson-dithered version of `bitmap`.

        Each pixel in `bitmap` may take a value in [0, 255].
        Based on code by Michal Migurski:
        http://mike.teczno.com/notes/atkinson.html
        """
        threshold = 128*[0] + 128*[255]
        for y in xrange(self._height):
            for x in xrange(self._width):
                old = self.pixels[y * self._width + x]
                new = threshold[old]
                err = (old - new) // 8
                self.pixels[y * self._width + x] = new
                for nxy in [(x+1, y), (x+2, y), (x-1, y+1),
                            (x, y+1), (x+1, y+1), (x, y+2)]:
                    try:
                        px = nxy[1] * self._width + nxy[0]
                        self.pixels[px] = commons.clamp(self.pixels[px] + err,
                                                        0, 255)
                    except IndexError:
                        pass

    def apply(self, func):
        for i in xrange(len(self.pixels)):
            self.pixels[i] = func(self.pixels[i])

    def copy(self):
        return self.__class__(width=self.width,
                              height=self.height,
                              pixels=self.pixels)

if __name__ == '__main__':
    s = Surface(32, 32)
    print(s)
    print(repr(s))
    s.fill()
    print(repr(s))
    s.loadimage('assets/dithertest.png')
    s.dither()
    print(repr(s))

    s = Surface(16, 16)
    s.vline(0)
    s.hline(0)
    print(repr(s))

    import time
    t0 = time.time()
    for p in xrange(10):
        s = Surface(filename='assets/dithertest.png')
        s.dither()
    print(time.time() - t0)

    s1 = Surface(8, 8)
    s2 = Surface(2, 2)
    s2.fill(1)
    print(repr(s1))
    print(repr(s2))
    s1.bitblt(s2, 0, 0)
    s1.bitblt(s2, 0, 6)
    s1.bitblt(s2, 6, 0)
    s1.bitblt(s2, 6, 6)
    s1.bitblt(s2, 3, 3)
    print(repr(s1))
    s1.bitblt(s2, 7, 3)
    print(repr(s1))

    print('--- clipping')
    r1 = Rect(100, 100, 50, 50)
    r2 = Rect(50, 50, 100, 100)
    print(r1, r2)
    print(r2.intersection(r1))
    print(r2.clipped(r1))

    print()

    s2.clear()
    s2.setpixel(0, 0)
    s2.setpixel(1, 1)
    r1 = Rect(50, 50, 50, 50)
    r2 = Rect(0, 0, 100, 100)
    print(r1, r2)
    print(r2.intersection(r1))
    print(r2.clipped(r1))

    print(repr(s1))
    print("blt:")
    print(repr(s2))
    s1.clear()
    # s1.blt(s2, 0, 0, Rect(1,1,2,2))
    s1.bitblt(s2, -1, -1)
    print(repr(s1))
    # s1.clear()
    s1.bitblt(s2, 7, 7)
    print(repr(s1))

    print('////')

    s2 = Surface(3, 3)
    s2.setpixel(1, 1)
    s2.setpixel(0, 1)
    s2.setpixel(2, 1)
    s2.setpixel(1, 0)
    s2.setpixel(1, 2)

    s1.clear()
    print(repr(s1))
    print("blt:")
    print(repr(s2))
    s1.clear()
    # s1.blt(s2, 0, 0, Rect(1,1,2,2))
    s1.bitblt(s2, -1, -1)
    print(repr(s1))
    # s1.clear()
    s1.bitblt(s2, 6, 6)
    print(repr(s1))

    s1.clear()
    s1.strokerect(1, 1, 6, 3)
    print(repr(s1))

    # s1.clear()
    s1.fillrect(1, 5, 6, 2)
    print(repr(s1))

    print('fill test:')
    t0 = time.time()
    s = Surface(128 * 64)
    for p in xrange(10000):
        s.fill(0)
        s.fill(1)
    print(time.time() - t0)

    print(s1.as_png_image())
    s1.write_image('test-image-grey.png')
