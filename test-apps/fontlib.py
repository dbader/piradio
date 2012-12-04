#!/usr/bin/env python
# -*- coding: utf-8 -*-
import freetype

def bits(x):
    """Unpack the bits of am 8bit word into a list."""
    data = []
    for i in range(8):
        data.insert(0, int((x & 1) == 1))
        x = x >> 1
    return data

def unpack_mono_bitmap(bitmap):
    """Unpack a freetype FT_LOAD_TARGET_MONO bitmap into a list that has one element per pixel."""
    data = []
    for i in range(bitmap.rows):
        row = []
        for j in range(bitmap.pitch):
            row.extend(bits(bitmap.buffer[i*bitmap.pitch+j]))
        data.extend(row[:bitmap.width])
    return data
    
def bitblt(src, dst, src_w, src_h, dst_w, dst_h, dst_x, dst_y):
    for x in range(src_w):
        for y in range(src_h):
            dst[(dst_y + y) * dst_w + dst_x + x] = src[y * src_w + x]
            
def bitmap2str(bmp, width, height, filled_char= '#', empty_char=' '):
    bstr = ''
    for i in range(height):
        rowstr = ''
        for j in range(width):
            rowstr += filled_char if bmp[i*width+j] else empty_char
        bstr += rowstr + '\n'
    return bstr

class Font(object):
    def __init__(self, filename, size):
        self._face = freetype.Face(filename)
        self.set_size(size)
      
    # @property
    # def size(self):
    #     """The font's size in pixels."""
    #     return self.thesize
       
    # @size.setter 
    def set_size(self, size):
        """Set the font's size in pixels."""
        self._face.set_pixel_sizes(size, size)
        # self.thesize = size        
        
    def text_extents(self, text):
        """Return (width, height, baseline) of `text` rendered in the current font."""
        slot = self._face.glyph
        width, height, baseline = 0, 0, 0
        previous = 0
        for c in text:
            self._face.load_char(c, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
            bitmap = slot.bitmap
            height = max(height, bitmap.rows + max (0, -(slot.bitmap_top - bitmap.rows)))
            baseline = max(baseline, max(0, -(slot.bitmap_top - bitmap.rows)))
            kerning = self._face.get_kerning(previous, c)
            width += (slot.advance.x >> 6) + (kerning.x >> 6)
            previous = c
        return (width, height, baseline)
        
    def render(self, text, width=None, height=None, baseline=None):
        if width is None or height is None or baseline is None:
            width, height, baseline = self.text_extents(text)
        outbuffer = [0] * (width * height)
        slot = self._face.glyph
        x, y = 0, 0
        previous = 0
        for c in text:
            self._face.load_char(c, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
            bitmap = slot.bitmap
            unpacked_bmp = unpack_mono_bitmap(bitmap)
            # print bitmap.buffer, 'unpacked:', unpacked_bmp, len(unpacked_bmp)
            top = slot.bitmap_top
            left = slot.bitmap_left
            w,h = bitmap.width, bitmap.rows
            y = height-baseline-top
            kerning = self._face.get_kerning(previous, c)
            x += (kerning.x >> 6)
            # print 'Glyph "%s" width=%i height=%i blt_x=%i blt_y=%i' % (c, w, h, x, y)
            # print_bitmap(unpacked_bmp, w, h)
            bitblt(unpacked_bmp, outbuffer, w, h, width, height, x, y)
            # print_bitmap(Z, width, height)
            x += (slot.advance.x >> 6)
            previous = c
            # print '\n\n'
        return outbuffer
            
if __name__ == '__main__':
    f = Font('/Users/daniel/dev/piradio/test-apps/font4.ttf', 16)
    text = u'Hello'
    width, height, baseline = f.text_extents(text)
    print '"%s": width=%i height=%i baseline=%i' % (text, width, height, baseline)
    print bitmap2str(f.render(text), width, height)
    
    def benchmark():
        for i in range(1000):
            f.render('Hello, World.')
    
    import cProfile
    cProfile.run('benchmark()')